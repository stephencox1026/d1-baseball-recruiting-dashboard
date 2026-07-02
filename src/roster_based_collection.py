"""
Roster-Based Data Collection

Fetches stats for players from our compiled roster list by matching them
against NCAA.com leaderboard data.
"""

import pandas as pd
import numpy as np
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection import NCAADataCollector
from src.metrics import MetricsCalculator
from src.draft_filter import DraftFilter
from config import (
    POWER_4_CONFERENCES,
    MIN_IP_STARTER,
    MIN_IP_RELIEVER,
    MIN_PA_HITTERS,
    STARTER_IP_PER_APP_THRESHOLD
)


def clean_name(name):
    """Clean player name for matching."""
    if pd.isna(name):
        return ""
    name = str(name).strip()
    # Remove common suffixes
    name = re.sub(r'\s+[JS]r\.?$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+III?$', '', name, flags=re.IGNORECASE)
    return name.lower()


def clean_team(team):
    """Clean team name for matching."""
    if pd.isna(team):
        return ""
    team = str(team).strip()
    # Remove common suffixes
    team = re.sub(r'\s+St\.?$', ' State', team, flags=re.IGNORECASE)
    team = re.sub(r'\s+St$', ' State', team, flags=re.IGNORECASE)
    return team.lower()


def load_roster_list():
    """Load the compiled roster list of undrafted seniors."""
    roster_path = "output/All_Seniors.csv"
    if not os.path.exists(roster_path):
        raise FileNotFoundError(f"Roster file not found: {roster_path}. Please run fetch_team_rosters.py first.")
    
    roster = pd.read_csv(roster_path)
    roster['name_clean'] = roster['name'].apply(clean_name)
    roster['team_clean'] = roster['team'].apply(clean_team)
    
    return roster


def match_roster_to_stats(roster_df, stats_df, stats_name_col='Player', stats_team_col='Team'):
    """
    Match roster players to stats by name and team.
    
    Returns:
        DataFrame with roster players matched to their stats
    """
    stats_df = stats_df.copy()
    stats_df['name_clean'] = stats_df[stats_name_col].apply(clean_name)
    stats_df['team_clean'] = stats_df[stats_team_col].apply(clean_team)
    
    # Merge on cleaned names and teams
    matched = roster_df.merge(
        stats_df,
        on=['name_clean', 'team_clean'],
        how='inner',
        suffixes=('', '_stats')
    )
    
    return matched


def collect_roster_player_stats():
    """
    Main function to collect stats for roster players.
    
    Returns:
        Tuple of (pitching_df, batting_df) with stats for roster players only
    """
    print("="*80)
    print("COLLECTING STATS FOR ROSTER PLAYERS")
    print("="*80)
    
    # Load roster
    print("\n1. Loading roster list...")
    roster = load_roster_list()
    print(f"   ✓ Loaded {len(roster)} players from roster")
    
    # Separate pitchers and hitters
    roster['is_pitcher'] = roster['position'].astype(str).str.contains('P|Pitcher', case=False, na=False)
    roster_pitchers = roster[roster['is_pitcher']].copy()
    roster_hitters = roster[~roster['is_pitcher']].copy()
    
    print(f"   - Pitchers: {len(roster_pitchers)}")
    print(f"   - Position Players: {len(roster_hitters)}")
    
    # Fetch stats from NCAA.com
    print("\n2. Fetching stats from NCAA.com...")
    collector = NCAADataCollector()
    
    pitching_stats = pd.DataFrame()
    batting_stats = pd.DataFrame()
    
    try:
        print("   Fetching pitching stats (this may take a minute)...")
        collector.fetch_pitching_stats(max_pages=15)  # Fetch enough pages to get good coverage
        pitching_stats = collector.pitching_data.copy()
        if not pitching_stats.empty:
            print(f"   ✓ Fetched {len(pitching_stats)} pitcher records")
        else:
            print("   ⚠ No pitching stats retrieved")
    except Exception as e:
        print(f"   ⚠ Error fetching pitching stats: {str(e)[:100]}")
        # Try to continue with partial data if available
        if hasattr(collector, 'pitching_data') and not collector.pitching_data.empty:
            pitching_stats = collector.pitching_data.copy()
            print(f"   Using partial data: {len(pitching_stats)} records")
    
    try:
        print("   Fetching batting stats (this may take a minute)...")
        collector.fetch_batting_stats(max_pages=15)  # Fetch enough pages to get good coverage
        batting_stats = collector.batting_data.copy()
        if not batting_stats.empty:
            print(f"   ✓ Fetched {len(batting_stats)} batter records")
        else:
            print("   ⚠ No batting stats retrieved")
    except Exception as e:
        print(f"   ⚠ Error fetching batting stats: {str(e)[:100]}")
        # Try to continue with partial data if available
        if hasattr(collector, 'batting_data') and not collector.batting_data.empty:
            batting_stats = collector.batting_data.copy()
            print(f"   Using partial data: {len(batting_stats)} records")
    
    # Match roster players to stats
    print("\n3. Matching roster players to stats...")
    
    matched_pitchers = pd.DataFrame()
    matched_hitters = pd.DataFrame()
    
    if not pitching_stats.empty and not roster_pitchers.empty:
        matched_pitchers = match_roster_to_stats(roster_pitchers, pitching_stats)
        print(f"   ✓ Matched {len(matched_pitchers)} pitchers to stats")
    else:
        print("   ⚠ No pitching stats to match")
    
    if not batting_stats.empty and not roster_hitters.empty:
        matched_hitters = match_roster_to_stats(roster_hitters, batting_stats)
        print(f"   ✓ Matched {len(matched_hitters)} hitters to stats")
    else:
        print("   ⚠ No batting stats to match")
    
    # Calculate metrics
    print("\n4. Calculating metrics...")
    metrics_calc = MetricsCalculator()
    
    if not matched_pitchers.empty:
        matched_pitchers = metrics_calc.calculate_pitching_metrics(matched_pitchers)
        print(f"   ✓ Calculated metrics for {len(matched_pitchers)} pitchers")
    
    if not matched_hitters.empty:
        matched_hitters = metrics_calc.calculate_batting_metrics(matched_hitters)
        print(f"   ✓ Calculated metrics for {len(matched_hitters)} hitters")
    
    # Filter to qualified players
    print("\n5. Filtering to qualified players...")
    
    if not matched_pitchers.empty:
        # Classify starters vs relievers
        matched_pitchers['is_starter'] = (
            matched_pitchers['ip_per_app'] >= STARTER_IP_PER_APP_THRESHOLD
        ) | (
            matched_pitchers['ip_per_app'].isna() & 
            (matched_pitchers['ip'].fillna(0) >= MIN_IP_STARTER)
        )
        
        starters = matched_pitchers[matched_pitchers['is_starter'] & (matched_pitchers['ip'] >= MIN_IP_STARTER)].copy()
        relievers = matched_pitchers[~matched_pitchers['is_starter'] & (matched_pitchers['ip'] >= MIN_IP_RELIEVER)].copy()
        
        print(f"   - Qualified Starters: {len(starters)}")
        print(f"   - Qualified Relievers: {len(relievers)}")
        
        # Combine for return (will be separated later)
        matched_pitchers = pd.concat([starters, relievers], ignore_index=True)
    else:
        matched_pitchers = pd.DataFrame()
    
    if not matched_hitters.empty:
        # Filter by minimum plate appearances
        # Estimate PA from AB + BB if PA not available
        if 'pa' not in matched_hitters.columns:
            if 'ab' in matched_hitters.columns and 'bb' in matched_hitters.columns:
                matched_hitters['pa'] = matched_hitters['ab'].fillna(0) + matched_hitters['bb'].fillna(0)
            else:
                matched_hitters['pa'] = 0
        
        qualified_hitters = matched_hitters[matched_hitters['pa'] >= MIN_PA_HITTERS].copy()
        print(f"   - Qualified Hitters: {len(qualified_hitters)}")
        matched_hitters = qualified_hitters
    else:
        matched_hitters = pd.DataFrame()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total roster players: {len(roster)}")
    print(f"Pitchers with stats: {len(matched_pitchers)}")
    print(f"Hitters with stats: {len(matched_hitters)}")
    
    return matched_pitchers, matched_hitters


if __name__ == "__main__":
    pitching, batting = collect_roster_player_stats()
    print(f"\nFinal counts:")
    print(f"  Pitchers: {len(pitching)}")
    print(f"  Hitters: {len(batting)}")

