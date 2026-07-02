"""
Explanation Generator Module for D1 Baseball Recruitment Dashboard

Generates contextual, human-readable explanations for player rankings.
"""

import pandas as pd
import numpy as np
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import get_grade


class ExplanationGenerator:
    """
    Generates intelligent explanations for player rankings based on their statistics.
    """
    
    def __init__(self):
        # Thresholds for evaluation
        self.pitcher_thresholds = {
            'era': {'elite': 2.50, 'good': 3.50, 'average': 4.50, 'below_avg': 5.50},
            'k_per_9': {'elite': 11.0, 'good': 9.0, 'average': 7.5, 'below_avg': 6.0},
            'bb_per_9': {'elite': 2.0, 'good': 3.0, 'average': 4.0, 'below_avg': 5.0},
            'whip': {'elite': 1.00, 'good': 1.20, 'average': 1.40, 'below_avg': 1.60}
        }
        
        self.hitter_thresholds = {
            'k_bb_ratio': {'elite': 1.0, 'good': 1.5, 'average': 2.0, 'below_avg': 2.5},
            'obp': {'elite': 0.420, 'good': 0.380, 'average': 0.340, 'below_avg': 0.300},
            'slg': {'elite': 0.550, 'good': 0.480, 'average': 0.420, 'below_avg': 0.360},
            'wrc_plus': {'elite': 140, 'good': 120, 'average': 100, 'below_avg': 85},
            'woba': {'elite': 0.400, 'good': 0.360, 'average': 0.320, 'below_avg': 0.290}
        }
    
    def _get_rating(self, value: float, stat: str, thresholds: dict, lower_is_better: bool = False) -> str:
        """Get rating category for a stat value."""
        if stat not in thresholds:
            return 'average'
        
        t = thresholds[stat]
        
        if lower_is_better:
            if value <= t['elite']:
                return 'elite'
            elif value <= t['good']:
                return 'good'
            elif value <= t['average']:
                return 'average'
            elif value <= t['below_avg']:
                return 'below_avg'
            else:
                return 'poor'
        else:
            if value >= t['elite']:
                return 'elite'
            elif value >= t['good']:
                return 'good'
            elif value >= t['average']:
                return 'average'
            elif value >= t['below_avg']:
                return 'below_avg'
            else:
                return 'poor'
    
    def _describe_control(self, bb_per_9: float) -> str:
        """Generate description of pitcher control."""
        rating = self._get_rating(bb_per_9, 'bb_per_9', self.pitcher_thresholds, lower_is_better=True)
        
        descriptions = {
            'elite': "exceptional command with pinpoint control",
            'good': "above-average control, minimizes free passes",
            'average': "adequate control, occasional wildness",
            'below_avg': "struggles with command at times",
            'poor': "needs significant improvement in control"
        }
        return descriptions.get(rating, "average control")
    
    def _describe_strikeouts(self, k_per_9: float, is_reliever: bool = False) -> str:
        """Generate description of strikeout ability."""
        rating = self._get_rating(k_per_9, 'k_per_9', self.pitcher_thresholds)
        
        if is_reliever:
            descriptions = {
                'elite': "dominant stuff with swing-and-miss arsenal",
                'good': "misses bats consistently, high-leverage potential",
                'average': "solid strikeout numbers for a reliever",
                'below_avg': "contact-oriented approach",
                'poor': "limited strikeout upside"
            }
        else:
            descriptions = {
                'elite': "overpowering stuff, true swing-and-miss ability",
                'good': "generates strikeouts, can pitch out of jams",
                'average': "adequate strikeout rate for a starter",
                'below_avg': "relies more on contact management",
                'poor': "limited ability to miss bats"
            }
        return descriptions.get(rating, "moderate strikeout ability")
    
    def _describe_era(self, era: float) -> str:
        """Generate description of ERA performance."""
        rating = self._get_rating(era, 'era', self.pitcher_thresholds, lower_is_better=True)
        
        descriptions = {
            'elite': "elite run prevention, ace-caliber performance",
            'good': "strong run prevention, reliable option",
            'average': "serviceable ERA, room for improvement",
            'below_avg': "struggles to limit runs at times",
            'poor': "concerning run prevention issues"
        }
        return descriptions.get(rating, "average run prevention")
    
    def _describe_plate_discipline(self, k_bb_ratio: float) -> str:
        """Generate description of hitter plate discipline."""
        rating = self._get_rating(k_bb_ratio, 'k_bb_ratio', self.hitter_thresholds, lower_is_better=True)
        
        descriptions = {
            'elite': "exceptional plate discipline, controls the strike zone",
            'good': "patient approach, works counts effectively",
            'average': "adequate strike zone judgment",
            'below_avg': "can be exploited with off-speed pitches",
            'poor': "struggles with pitch recognition"
        }
        return descriptions.get(rating, "average plate discipline")
    
    def _describe_power(self, slg: float, iso: float = None) -> str:
        """Generate description of hitter power."""
        rating = self._get_rating(slg, 'slg', self.hitter_thresholds)
        
        descriptions = {
            'elite': "plus-plus power, legitimate threat to go deep",
            'good': "above-average power, can drive the ball",
            'average': "moderate pop, gap-to-gap power",
            'below_avg': "limited power projection",
            'poor': "minimal power output"
        }
        return descriptions.get(rating, "average power")
    
    def _describe_overall_hitting(self, wrc_plus: int) -> str:
        """Generate description of overall offensive production."""
        rating = self._get_rating(wrc_plus, 'wrc_plus', self.hitter_thresholds)
        
        descriptions = {
            'elite': "elite offensive producer, impacts the game daily",
            'good': "above-average hitter, consistent contributor",
            'average': "league-average production at the plate",
            'below_avg': "below-average offensive output",
            'poor': "struggles offensively"
        }
        return descriptions.get(rating, "average production")
    
    def generate_starter_explanation(self, row: pd.Series) -> str:
        """
        Generate a comprehensive explanation for a starting pitcher.
        
        Emphasizes: Control (BB/9) > ERA > K/9 > WHIP
        """
        name = row['name']
        team = row['team']
        era = row['era']
        k_per_9 = row['k_per_9']
        bb_per_9 = row['bb_per_9']
        whip = row['whip']
        ip = row['ip']
        
        # Build explanation based on strengths
        parts = []
        
        # Lead with control (most important for starters)
        control_desc = self._describe_control(bb_per_9)
        parts.append(f"Demonstrates {control_desc} with a {bb_per_9:.2f} BB/9")
        
        # ERA assessment
        era_desc = self._describe_era(era)
        parts.append(f"{era_desc} ({era:.2f} ERA)")
        
        # Strikeout ability (velocity proxy)
        k_desc = self._describe_strikeouts(k_per_9, is_reliever=False)
        if self._get_rating(k_per_9, 'k_per_9', self.pitcher_thresholds) in ['elite', 'good']:
            parts.append(f"{k_desc} ({k_per_9:.1f} K/9)")
        
        # Workload note
        if ip >= 80:
            parts.append(f"proven workhorse with {ip:.0f} innings")
        elif ip >= 60:
            parts.append(f"solid workload of {ip:.0f} innings")
        
        # Compile explanation
        explanation = ". ".join(parts) + "."
        
        # Add projection
        control_rating = self._get_rating(bb_per_9, 'bb_per_9', self.pitcher_thresholds, True)
        era_rating = self._get_rating(era, 'era', self.pitcher_thresholds, True)
        
        if control_rating in ['elite', 'good'] and era_rating in ['elite', 'good']:
            explanation += " Projects as a potential weekend starter at the next level."
        elif control_rating in ['elite', 'good']:
            explanation += " Command-first profile that could develop into a quality arm."
        
        return explanation
    
    def generate_reliever_explanation(self, row: pd.Series) -> str:
        """
        Generate a comprehensive explanation for a relief pitcher.
        
        Emphasizes: K/9 (stuff/velocity) > ERA > WHIP
        """
        name = row['name']
        team = row['team']
        era = row['era']
        k_per_9 = row['k_per_9']
        bb_per_9 = row['bb_per_9']
        whip = row['whip']
        saves = row.get('saves', 0)
        
        parts = []
        
        # Lead with strikeout ability (most important for relievers)
        k_desc = self._describe_strikeouts(k_per_9, is_reliever=True)
        parts.append(f"Features {k_desc} with {k_per_9:.1f} K/9")
        
        # ERA
        era_desc = self._describe_era(era)
        if self._get_rating(era, 'era', self.pitcher_thresholds, True) in ['elite', 'good']:
            parts.append(f"{era_desc} ({era:.2f} ERA)")
        
        # Saves note if applicable
        if saves >= 5:
            parts.append(f"proven closer experience with {int(saves)} saves")
        
        # Control note (secondary for relievers but still relevant)
        control_rating = self._get_rating(bb_per_9, 'bb_per_9', self.pitcher_thresholds, True)
        if control_rating in ['elite', 'good']:
            parts.append(f"pairs stuff with solid control ({bb_per_9:.2f} BB/9)")
        
        explanation = ". ".join(parts) + "."
        
        # Projection
        k_rating = self._get_rating(k_per_9, 'k_per_9', self.pitcher_thresholds)
        era_rating = self._get_rating(era, 'era', self.pitcher_thresholds, True)
        
        if k_rating == 'elite':
            explanation += " High-leverage reliever profile with late-inning upside."
        elif k_rating == 'good' and era_rating in ['elite', 'good']:
            explanation += " Setup man potential with ability to pitch in key situations."
        
        return explanation
    
    def generate_hitter_explanation(self, row: pd.Series) -> str:
        """
        Generate a comprehensive explanation for a hitter.
        
        Emphasizes: K:BB Ratio > wRC+ > wOBA > OBP > SLG > OPS
        """
        name = row['name']
        team = row['team']
        position = row.get('position', 'N/A')
        k_bb_ratio = row['k_bb_ratio']
        obp = row['obp']
        slg = row['slg']
        ops = row['ops']
        wrc_plus = row['wrc_plus']
        woba = row['woba']
        
        parts = []
        
        # Lead with plate discipline (most important)
        discipline_desc = self._describe_plate_discipline(k_bb_ratio)
        parts.append(f"{discipline_desc} ({k_bb_ratio:.2f} K:BB)")
        
        # Overall production
        production_desc = self._describe_overall_hitting(wrc_plus)
        parts.append(f"{production_desc} ({wrc_plus} wRC+)")
        
        # Power assessment
        power_rating = self._get_rating(slg, 'slg', self.hitter_thresholds)
        if power_rating in ['elite', 'good']:
            power_desc = self._describe_power(slg)
            parts.append(f"{power_desc} ({slg:.3f} SLG)")
        
        # On-base ability
        obp_rating = self._get_rating(obp, 'obp', self.hitter_thresholds)
        if obp_rating in ['elite', 'good']:
            parts.append(f"high on-base percentage ({obp:.3f} OBP)")
        
        explanation = ". ".join(parts) + "."
        
        # Projection based on profile
        discipline_rating = self._get_rating(k_bb_ratio, 'k_bb_ratio', self.hitter_thresholds, True)
        wrc_rating = self._get_rating(wrc_plus, 'wrc_plus', self.hitter_thresholds)
        
        if discipline_rating == 'elite' and wrc_rating in ['elite', 'good']:
            explanation += " Premium bat with advanced approach, strong next-level projection."
        elif discipline_rating in ['elite', 'good']:
            explanation += " Patient hitter whose approach should translate well to higher levels."
        elif wrc_rating == 'elite':
            explanation += " Impact bat with offensive upside despite some swing-and-miss."
        
        return explanation
    
    def generate_batch_explanations(self, df: pd.DataFrame, player_type: str) -> list[str]:
        """
        Generate explanations for all players in a dataframe.
        
        Args:
            df: DataFrame with player data
            player_type: 'starter', 'reliever', or 'hitter'
            
        Returns:
            List of explanation strings
        """
        explanations = []
        
        for _, row in df.iterrows():
            if player_type == 'starter':
                explanation = self.generate_starter_explanation(row)
            elif player_type == 'reliever':
                explanation = self.generate_reliever_explanation(row)
            elif player_type == 'hitter':
                explanation = self.generate_hitter_explanation(row)
            else:
                explanation = ""
            
            explanations.append(explanation)
        
        return explanations


def main():
    """Test explanation generation."""
    from src.data_collection import DataCollector
    from src.draft_filter import filter_all_data
    from src.metrics import process_all_metrics
    from src.ranking import generate_all_rankings
    
    # Get data
    collector = DataCollector()
    pitching, batting = collector.collect_all_data(use_cache=False)
    pitching, batting = filter_all_data(pitching, batting)
    pitching, batting = process_all_metrics(pitching, batting)
    top_starters, top_relievers, top_hitters = generate_all_rankings(pitching, batting)
    
    # Generate explanations
    gen = ExplanationGenerator()
    
    print("\n" + "="*70)
    print("SAMPLE STARTING PITCHER EXPLANATIONS")
    print("="*70)
    for _, row in top_starters.head(3).iterrows():
        print(f"\n#{int(row['rank'])} {row['name']} ({row['team']})")
        print(f"   ERA: {row['era']:.2f} | K/9: {row['k_per_9']:.1f} | BB/9: {row['bb_per_9']:.1f}")
        print(f"   → {gen.generate_starter_explanation(row)}")
    
    print("\n" + "="*70)
    print("SAMPLE RELIEF PITCHER EXPLANATIONS")
    print("="*70)
    for _, row in top_relievers.head(3).iterrows():
        print(f"\n#{int(row['rank'])} {row['name']} ({row['team']})")
        print(f"   ERA: {row['era']:.2f} | K/9: {row['k_per_9']:.1f} | BB/9: {row['bb_per_9']:.1f}")
        print(f"   → {gen.generate_reliever_explanation(row)}")
    
    print("\n" + "="*70)
    print("SAMPLE HITTER EXPLANATIONS")
    print("="*70)
    for _, row in top_hitters.head(3).iterrows():
        print(f"\n#{int(row['rank'])} {row['name']} ({row['team']}) - {row['position']}")
        print(f"   K:BB: {row['k_bb_ratio']:.2f} | OBP: {row['obp']:.3f} | wRC+: {row['wrc_plus']}")
        print(f"   → {gen.generate_hitter_explanation(row)}")


if __name__ == "__main__":
    main()

