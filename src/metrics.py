"""
Metrics Calculation Module for D1 Baseball Recruitment Dashboard

Calculates derived metrics and prepares data for ranking algorithm.
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    MIN_IP_STARTER,
    MIN_IP_RELIEVER,
    MIN_PA_HITTERS,
    STARTER_IP_PER_APP_THRESHOLD
)
from src.utils import calculate_percentile


class MetricsCalculator:
    """
    Calculates advanced metrics and derived statistics for player evaluation.
    """
    
    def __init__(self):
        pass
    
    def calculate_pitching_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived pitching metrics.
        
        Adds/updates:
        - k_per_9: Strikeouts per 9 innings
        - bb_per_9: Walks per 9 innings (strike rate proxy)
        - h_per_9: Hits per 9 innings
        - k_bb_ratio: Strikeout to walk ratio
        - ip_per_app: Innings per appearance
        - is_starter: Boolean indicating likely starter
        - is_reliever: Boolean indicating likely reliever
        - strike_rate_score: Normalized strike rate (lower BB/9 = higher score)
        - stuff_score: Combined K/9 metric (velocity proxy)
        """
        df = df.copy()
        
        # Ensure IP is numeric
        df['ip'] = pd.to_numeric(df['ip'], errors='coerce')
        
        # Calculate rate stats per 9 innings
        df['k_per_9'] = np.where(
            df['ip'] > 0,
            (df['strikeouts'] / df['ip']) * 9,
            0
        )
        
        df['bb_per_9'] = np.where(
            df['ip'] > 0,
            (df['walks'] / df['ip']) * 9,
            0
        )
        
        df['h_per_9'] = np.where(
            df['ip'] > 0,
            (df['hits'] / df['ip']) * 9,
            0
        )
        
        # K:BB ratio (higher is better)
        df['k_bb_ratio'] = np.where(
            df['walks'] > 0,
            df['strikeouts'] / df['walks'],
            df['strikeouts']  # If no walks, use strikeouts as the ratio
        )
        
        # WHIP calculation (if not already present)
        if 'whip' not in df.columns or df['whip'].isna().all():
            df['whip'] = np.where(
                df['ip'] > 0,
                (df['hits'] + df['walks']) / df['ip'],
                0
            )
        
        # Innings per appearance (to classify starter vs reliever)
        df['ip_per_app'] = np.where(
            df['appearances'] > 0,
            df['ip'] / df['appearances'],
            0
        )
        
        # Classify as starter or reliever
        # If 'games_started' column exists, use it; otherwise estimate from IP/App
        if 'games_started' in df.columns:
            df['is_starter'] = (
                (df['ip_per_app'] >= STARTER_IP_PER_APP_THRESHOLD) &
                (df['games_started'] >= df['appearances'] * 0.5) &
                (df['ip'] >= MIN_IP_STARTER)
            )
        else:
            # Estimate: pitchers with high IP/App are likely starters
            df['is_starter'] = (
                (df['ip_per_app'] >= STARTER_IP_PER_APP_THRESHOLD) &
                (df['ip'] >= MIN_IP_STARTER)
            )
        
        df['is_reliever'] = (
            (df['ip_per_app'] < STARTER_IP_PER_APP_THRESHOLD) &
            (df['ip'] >= MIN_IP_RELIEVER) &
            (~df['is_starter'])
        )
        
        # If saves > 0, definitely a reliever
        if 'saves' in df.columns:
            df.loc[df['saves'] > 0, 'is_reliever'] = True
            df.loc[df['saves'] > 0, 'is_starter'] = False
        
        # Round calculated fields
        for col in ['k_per_9', 'bb_per_9', 'h_per_9', 'k_bb_ratio', 'whip', 'ip_per_app']:
            df[col] = df[col].round(2)
        
        return df
    
    def calculate_batting_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate derived batting metrics.
        
        Adds/updates:
        - k_bb_ratio: Strikeout to walk ratio (lower is better for hitters)
        - iso: Isolated power (SLG - AVG)
        - woba: Weighted on-base average (if not present)
        - wrc_plus: Weighted runs created plus (if not present)
        """
        df = df.copy()
        
        # Ensure PA is numeric
        df['plate_appearances'] = pd.to_numeric(df['plate_appearances'], errors='coerce')
        df['at_bats'] = pd.to_numeric(df['at_bats'], errors='coerce')
        
        # Ensure walks and strikeouts exist
        if 'walks' not in df.columns:
            df['walks'] = 0
        if 'strikeouts' not in df.columns:
            df['strikeouts'] = 0
        
        # K:BB ratio for hitters (lower is better - good plate discipline)
        df['k_bb_ratio'] = np.where(
            df['walks'] > 0,
            df['strikeouts'] / df['walks'],
            np.where(df['strikeouts'] > 0, df['strikeouts'], 999)  # High ratio if no walks
        )
        
        # Isolated Power (pure power metric)
        df['iso'] = df['slg'] - df['avg']
        
        # Calculate wOBA if not present (NO HBP - using only real data)
        if 'woba' not in df.columns or df['woba'].isna().all():
            # Ensure all required columns exist
            if 'doubles' not in df.columns:
                df['doubles'] = 0
            if 'triples' not in df.columns:
                df['triples'] = 0
            if 'home_runs' not in df.columns:
                df['home_runs'] = 0
            
            # wOBA weights (2024 values) - HBP excluded since it's estimated
            df['singles'] = df['hits'] - df['doubles'] - df['triples'] - df['home_runs']
            df['singles'] = df['singles'].clip(lower=0)
            
            woba_numerator = (
                0.69 * df['walks'].fillna(0) +
                0.89 * df['singles'] +
                1.27 * df['doubles'] +
                1.62 * df['triples'] +
                2.10 * df['home_runs']
            )
            
            # Denominator: AB + BB (NO HBP)
            woba_denominator = df['at_bats'].fillna(0) + df['walks'].fillna(0)
            
            df['woba'] = np.where(
                woba_denominator > 0,
                woba_numerator / woba_denominator,
                0
            )
        
        # Calculate wRC+ if not present (approximation)
        if 'wrc_plus' not in df.columns or df['wrc_plus'].isna().all():
            # wRC+ = ((wRAA/PA + league R/PA) / league wRC/PA) * 100
            # Simplified: Convert wOBA to wRC+
            league_woba = 0.320  # Approximate league average
            woba_scale = 1.25
            
            df['wrc_plus'] = ((df['woba'] - league_woba) / woba_scale * 100 + 100).astype(int)
            df['wrc_plus'] = df['wrc_plus'].clip(0, 250)
        
        # Filter by minimum plate appearances
        df['qualified'] = df['plate_appearances'] >= MIN_PA_HITTERS
        
        # Round calculated fields
        for col in ['k_bb_ratio', 'iso', 'woba']:
            if col in df.columns:
                df[col] = df[col].round(3)
        
        return df
    
    def add_percentile_rankings(self, df: pd.DataFrame, stat_columns: dict) -> pd.DataFrame:
        """
        Add percentile rankings for key statistics.
        
        Args:
            df: DataFrame with player stats
            stat_columns: Dict mapping column name to whether lower is better
                         e.g., {'era': True, 'k_per_9': False}
        
        Returns:
            DataFrame with added percentile columns
        """
        df = df.copy()
        
        for col, lower_is_better in stat_columns.items():
            if col in df.columns:
                pctl_col = f"{col}_pctl"
                df[pctl_col] = df[col].apply(
                    lambda x: calculate_percentile(x, df[col], lower_is_better)
                )
        
        return df
    
    def get_starters(self, pitching_df: pd.DataFrame) -> pd.DataFrame:
        """Get qualified starting pitchers."""
        if 'is_starter' not in pitching_df.columns:
            pitching_df = self.calculate_pitching_metrics(pitching_df)
        
        starters = pitching_df[pitching_df['is_starter']].copy()
        print(f"Found {len(starters)} qualified starting pitchers")
        return starters
    
    def get_relievers(self, pitching_df: pd.DataFrame) -> pd.DataFrame:
        """Get qualified relief pitchers."""
        if 'is_reliever' not in pitching_df.columns:
            pitching_df = self.calculate_pitching_metrics(pitching_df)
        
        relievers = pitching_df[pitching_df['is_reliever']].copy()
        print(f"Found {len(relievers)} qualified relief pitchers")
        return relievers
    
    def get_qualified_hitters(self, batting_df: pd.DataFrame) -> pd.DataFrame:
        """Get qualified hitters by plate appearances."""
        if 'qualified' not in batting_df.columns:
            batting_df = self.calculate_batting_metrics(batting_df)
        
        qualified = batting_df[batting_df['qualified']].copy()
        print(f"Found {len(qualified)} qualified hitters")
        return qualified


def process_all_metrics(pitching_df: pd.DataFrame, batting_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to calculate all metrics.
    
    Args:
        pitching_df: Raw pitching data
        batting_df: Raw batting data
        
    Returns:
        Tuple of (processed_pitching, processed_batting)
    """
    calculator = MetricsCalculator()
    
    print("Calculating pitching metrics...")
    processed_pitching = calculator.calculate_pitching_metrics(pitching_df)
    
    # Add percentiles for pitching (NO WHIP - not available)
    pitching_pctl_cols = {
        'era': True,      # Lower is better
        'bb_per_9': True, # Lower is better (strike rate)
        'k_per_9': False, # Higher is better
        'k_bb_ratio': False  # Higher is better for pitchers
    }
    processed_pitching = calculator.add_percentile_rankings(processed_pitching, pitching_pctl_cols)
    
    print("Calculating batting metrics...")
    processed_batting = calculator.calculate_batting_metrics(batting_df)
    
    # Add percentiles for batting
    batting_pctl_cols = {
        'k_bb_ratio': True,  # Lower is better for hitters
        'obp': False,        # Higher is better
        'slg': False,        # Higher is better
        'ops': False,        # Higher is better
        'woba': False,       # Higher is better
        'wrc_plus': False    # Higher is better
    }
    processed_batting = calculator.add_percentile_rankings(processed_batting, batting_pctl_cols)
    
    return processed_pitching, processed_batting


def main():
    """Test metrics calculation."""
    from src.data_collection import DataCollector
    from src.draft_filter import filter_all_data
    
    # Collect and filter data
    collector = DataCollector()
    pitching, batting = collector.collect_all_data(use_cache=False)
    pitching, batting = filter_all_data(pitching, batting)
    
    # Calculate metrics
    processed_pitching, processed_batting = process_all_metrics(pitching, batting)
    
    # Show results
    calculator = MetricsCalculator()
    
    starters = calculator.get_starters(processed_pitching)
    relievers = calculator.get_relievers(processed_pitching)
    hitters = calculator.get_qualified_hitters(processed_batting)
    
    print(f"\nQualified Players:")
    print(f"  Starting Pitchers: {len(starters)}")
    print(f"  Relief Pitchers: {len(relievers)}")
    print(f"  Hitters: {len(hitters)}")
    
    print("\nTop 5 Starters by ERA:")
    print(starters.nsmallest(5, 'era')[['name', 'team', 'era', 'k_per_9', 'bb_per_9', 'whip']])


if __name__ == "__main__":
    main()

