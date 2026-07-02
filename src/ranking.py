"""
Ranking Algorithm Module for D1 Baseball Recruitment Dashboard

Implements weighted composite scoring for ranking players by potential.
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    STARTING_PITCHER_WEIGHTS,
    RELIEF_PITCHER_WEIGHTS,
    HITTER_WEIGHTS,
    NUM_STARTING_PITCHERS,
    NUM_RELIEF_PITCHERS,
    NUM_HITTERS
)


class PlayerRanker:
    """
    Ranks players using weighted composite scoring based on key metrics.
    """
    
    def __init__(self):
        self.sp_weights = STARTING_PITCHER_WEIGHTS
        self.rp_weights = RELIEF_PITCHER_WEIGHTS
        self.hitter_weights = HITTER_WEIGHTS
    
    def _normalize_stat(self, series: pd.Series, lower_is_better: bool = False) -> pd.Series:
        """
        Normalize a stat to 0-100 scale using min-max normalization.
        
        Args:
            series: Pandas series of stat values
            lower_is_better: If True, invert so lower values get higher scores
            
        Returns:
            Normalized series (0-100 scale)
        """
        min_val = series.min()
        max_val = series.max()
        
        if max_val == min_val:
            return pd.Series([50] * len(series), index=series.index)
        
        if lower_is_better:
            # Invert: lower values should get higher scores
            normalized = 100 - ((series - min_val) / (max_val - min_val) * 100)
        else:
            # Higher values get higher scores
            normalized = (series - min_val) / (max_val - min_val) * 100
        
        return normalized
    
    def rank_starting_pitchers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank starting pitchers based on weighted criteria.
        
        Priority Order:
        1. Strike Rate (BB/9 - lower is better) - 50%
        2. ERA (lower is better) - 30%
        3. K/9 (higher is better, velocity proxy) - 20%
        
        NOTE: WHIP excluded - hits allowed not available on NCAA.com
        """
        df = df.copy()
        
        # Normalize each stat (ONLY real data - no WHIP)
        df['norm_bb_per_9'] = self._normalize_stat(df['bb_per_9'], lower_is_better=True)
        df['norm_era'] = self._normalize_stat(df['era'], lower_is_better=True)
        df['norm_k_per_9'] = self._normalize_stat(df['k_per_9'], lower_is_better=False)
        
        # Calculate weighted composite score (NO WHIP - only real data)
        df['composite_score'] = (
            df['norm_bb_per_9'] * self.sp_weights['bb_per_9'] +
            df['norm_era'] * self.sp_weights['era'] +
            df['norm_k_per_9'] * self.sp_weights['k_per_9']
        )
        
        # Rank by composite score
        df['rank'] = df['composite_score'].rank(ascending=False, method='min').astype(int)
        
        # Sort by rank
        df = df.sort_values('rank')
        
        # Add tier classification
        df['tier'] = pd.cut(
            df['composite_score'],
            bins=[0, 40, 55, 70, 85, 100],
            labels=['Tier 5', 'Tier 4', 'Tier 3', 'Tier 2', 'Tier 1']
        )
        
        return df
    
    def rank_relief_pitchers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank relief pitchers based on weighted criteria.
        
        Priority Order:
        1. K/9 (higher is better, velocity/stuff proxy) - 50%
        2. ERA (lower is better) - 35%
        3. IP/App ratio (lower = short stints = true reliever) - 15%
        
        NOTE: WHIP excluded - hits allowed not available on NCAA.com
        """
        df = df.copy()
        
        # Normalize each stat (ONLY real data - no WHIP)
        df['norm_k_per_9'] = self._normalize_stat(df['k_per_9'], lower_is_better=False)
        df['norm_era'] = self._normalize_stat(df['era'], lower_is_better=True)
        df['norm_ip_per_app'] = self._normalize_stat(df['ip_per_app'], lower_is_better=True)
        
        # Calculate weighted composite score (NO WHIP - only real data)
        df['composite_score'] = (
            df['norm_k_per_9'] * self.rp_weights['k_per_9'] +
            df['norm_era'] * self.rp_weights['era'] +
            df['norm_ip_per_app'] * self.rp_weights['ip_per_app']
        )
        
        # Rank by composite score
        df['rank'] = df['composite_score'].rank(ascending=False, method='min').astype(int)
        
        # Sort by rank
        df = df.sort_values('rank')
        
        # Add tier classification
        df['tier'] = pd.cut(
            df['composite_score'],
            bins=[0, 40, 55, 70, 85, 100],
            labels=['Tier 5', 'Tier 4', 'Tier 3', 'Tier 2', 'Tier 1']
        )
        
        return df
    
    def rank_hitters(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Rank hitters based on weighted criteria.
        
        Priority Order:
        1. K:BB Ratio (lower is better) - 35%
        2. wRC+ (higher is better) - 20%
        3. wOBA (higher is better) - 15%
        4. OBP (higher is better) - 15%
        5. SLG (higher is better) - 10%
        6. OPS (higher is better) - 5%
        """
        df = df.copy()
        
        # Normalize each stat
        df['norm_k_bb_ratio'] = self._normalize_stat(df['k_bb_ratio'], lower_is_better=True)
        df['norm_wrc_plus'] = self._normalize_stat(df['wrc_plus'], lower_is_better=False)
        df['norm_woba'] = self._normalize_stat(df['woba'], lower_is_better=False)
        df['norm_obp'] = self._normalize_stat(df['obp'], lower_is_better=False)
        df['norm_slg'] = self._normalize_stat(df['slg'], lower_is_better=False)
        df['norm_ops'] = self._normalize_stat(df['ops'], lower_is_better=False)
        
        # Calculate weighted composite score
        df['composite_score'] = (
            df['norm_k_bb_ratio'] * self.hitter_weights['k_bb_ratio'] +
            df['norm_wrc_plus'] * self.hitter_weights['wrc_plus'] +
            df['norm_woba'] * self.hitter_weights['woba'] +
            df['norm_obp'] * self.hitter_weights['obp'] +
            df['norm_slg'] * self.hitter_weights['slg'] +
            df['norm_ops'] * self.hitter_weights['ops']
        )
        
        # Rank by composite score
        df['rank'] = df['composite_score'].rank(ascending=False, method='min').astype(int)
        
        # Sort by rank
        df = df.sort_values('rank')
        
        # Add tier classification
        df['tier'] = pd.cut(
            df['composite_score'],
            bins=[0, 40, 55, 70, 85, 100],
            labels=['Tier 5', 'Tier 4', 'Tier 3', 'Tier 2', 'Tier 1']
        )
        
        return df
    
    def get_top_players(self, starters_df: pd.DataFrame, relievers_df: pd.DataFrame, 
                        hitters_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Get the top players for each category based on the required counts.
        
        Returns:
            Tuple of (top_30_starters, top_15_relievers, top_50_hitters)
        """
        # Rank each category
        ranked_starters = self.rank_starting_pitchers(starters_df)
        ranked_relievers = self.rank_relief_pitchers(relievers_df)
        ranked_hitters = self.rank_hitters(hitters_df)
        
        # Get top N for each
        top_starters = ranked_starters.head(NUM_STARTING_PITCHERS)
        top_relievers = ranked_relievers.head(NUM_RELIEF_PITCHERS)
        top_hitters = ranked_hitters.head(NUM_HITTERS)
        
        print(f"Selected top {len(top_starters)} starting pitchers")
        print(f"Selected top {len(top_relievers)} relief pitchers")
        print(f"Selected top {len(top_hitters)} hitters")
        
        return top_starters, top_relievers, top_hitters


def generate_all_rankings(pitching_df: pd.DataFrame, batting_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to generate all rankings.
    
    Args:
        pitching_df: Processed pitching data with metrics
        batting_df: Processed batting data with metrics
        
    Returns:
        Tuple of (ranked_starters, ranked_relievers, ranked_hitters)
    """
    from src.metrics import MetricsCalculator
    
    calculator = MetricsCalculator()
    ranker = PlayerRanker()
    
    # Get qualified players
    starters = calculator.get_starters(pitching_df)
    relievers = calculator.get_relievers(pitching_df)
    hitters = calculator.get_qualified_hitters(batting_df)
    
    # Generate rankings
    return ranker.get_top_players(starters, relievers, hitters)


def main():
    """Test ranking algorithm."""
    from src.data_collection import DataCollector
    from src.draft_filter import filter_all_data
    from src.metrics import process_all_metrics
    
    # Collect, filter, and calculate metrics
    collector = DataCollector()
    pitching, batting = collector.collect_all_data(use_cache=False)
    pitching, batting = filter_all_data(pitching, batting)
    pitching, batting = process_all_metrics(pitching, batting)
    
    # Generate rankings
    top_starters, top_relievers, top_hitters = generate_all_rankings(pitching, batting)
    
    print("\n" + "="*60)
    print("TOP 10 STARTING PITCHERS")
    print("="*60)
    cols = ['rank', 'name', 'team', 'conference', 'era', 'k_per_9', 'bb_per_9', 'whip', 'composite_score', 'tier']
    print(top_starters.head(10)[cols].to_string(index=False))
    
    print("\n" + "="*60)
    print("TOP 10 RELIEF PITCHERS")
    print("="*60)
    cols = ['rank', 'name', 'team', 'conference', 'era', 'k_per_9', 'bb_per_9', 'composite_score', 'tier']
    print(top_relievers.head(10)[cols].to_string(index=False))
    
    print("\n" + "="*60)
    print("TOP 10 HITTERS")
    print("="*60)
    cols = ['rank', 'name', 'team', 'conference', 'position', 'k_bb_ratio', 'obp', 'slg', 'wrc_plus', 'composite_score', 'tier']
    print(top_hitters.head(10)[cols].to_string(index=False))


if __name__ == "__main__":
    main()

