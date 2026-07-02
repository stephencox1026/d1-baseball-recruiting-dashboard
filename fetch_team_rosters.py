"""
Team Roster Fetcher

Fetches complete team rosters from official team websites for Power 4 conferences.
This gets ALL players, not just top performers from leaderboards.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import sys
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.draft_filter import DraftFilter
from src.data_collection import NCAADataCollector
from src.metrics import MetricsCalculator
from config import POWER_4_CONFERENCES, STARTER_IP_PER_APP_THRESHOLD

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# Team website URL patterns
TEAM_URLS = {
    # SEC
    'Tennessee': 'https://utsports.com/sports/baseball/roster',
    'LSU': 'https://lsusports.net/sports/baseball/roster/',
    'Arkansas': 'https://arkansasrazorbacks.com/sport/baseball/',
    'Florida': 'https://floridagators.com/sports/baseball/roster',
    'Vanderbilt': 'https://vucommodores.com/sports/baseball/roster/',
    'Texas A&M': 'https://12thman.com/sports/baseball/roster',
    'Auburn': 'https://auburntigers.com/sports/baseball/roster',
    'Alabama': 'https://rolltide.com/sports/baseball/roster',
    'Georgia': 'https://georgiadogs.com/sports/baseball/roster',
    'South Carolina': 'https://gamecocksonline.com/sports/baseball/roster',
    'Mississippi State': 'https://hailstate.com/sports/baseball/roster',
    'Ole Miss': 'https://olemisssports.com/sports/baseball/roster',
    'Kentucky': 'https://ukathletics.com/sports/baseball/roster',
    'Missouri': 'https://mutigers.com/sports/baseball/roster',
    
    # ACC
    'Florida State': 'https://seminoles.com/sports/baseball/roster/',
    'North Carolina': 'https://goheels.com/sports/baseball/roster',
    'Clemson': 'https://clemsontigers.com/sports/baseball/roster/',
    'Virginia': 'https://virginiasports.com/sports/baseball/roster/',
    'Duke': 'https://goduke.com/sports/baseball/roster',
    'Wake Forest': 'https://godeacs.com/sports/baseball/roster',
    'NC State': 'https://gopack.com/sports/baseball/roster',
    'Louisville': 'https://gocards.com/sports/baseball/roster',
    'Miami': 'https://miamihurricanes.com/sports/baseball/roster/',
    'Georgia Tech': 'https://ramblinwreck.com/sports/baseball/roster',
    'Virginia Tech': 'https://hokiesports.com/sports/baseball/roster',
    'Boston College': 'https://bceagles.com/sports/baseball/roster',
    'Notre Dame': 'https://und.com/sports/baseball/roster/',
    'Pittsburgh': 'https://pittsburghpanthers.com/sports/baseball/roster',
    'Syracuse': 'https://cuse.com/sports/baseball/roster',
    
    # Big Ten
    'Michigan': 'https://mgoblue.com/sports/baseball/roster',
    'Nebraska': 'https://huskers.com/sports/baseball/roster',
    'Iowa': 'https://hawkeyesports.com/sports/baseball/roster',
    'Maryland': 'https://umterps.com/sports/baseball/roster',
    'Indiana': 'https://iuhoosiers.com/sports/baseball/roster',
    'Illinois': 'https://fightingillini.com/sports/baseball/roster',
    'Minnesota': 'https://gophersports.com/sports/baseball/roster',
    'Ohio State': 'https://ohiostatebuckeyes.com/sports/baseball/roster',
    'Purdue': 'https://purduesports.com/sports/baseball/roster',
    'Rutgers': 'https://scarletknights.com/sports/baseball/roster',
    'Michigan State': 'https://msuspartans.com/sports/baseball/roster',
    'Northwestern': 'https://nusports.com/sports/baseball/roster',
    'Wisconsin': 'https://uwbadgers.com/sports/baseball/roster',
    
    # Big 12
    'Texas Tech': 'https://texastech.com/sports/baseball/roster',
    'Oklahoma State': 'https://okstate.com/sports/baseball/roster',
    'TCU': 'https://gofrogs.com/sports/baseball/roster',
    'Oklahoma': 'https://soonersports.com/sports/baseball/roster',
    'Baylor': 'https://baylorbears.com/sports/baseball/roster',
    'Kansas State': 'https://www.kstatesports.com/sports/baseball/roster',
    'Kansas': 'https://kuathletics.com/sports/baseball/roster',
    'West Virginia': 'https://wvusports.com/sports/baseball/roster',
    'Arizona': 'https://arizonawildcats.com/sports/baseball/roster',
    'Arizona State': 'https://thesundevils.com/sports/baseball/roster',
    'Cincinnati': 'https://gobearcats.com/sports/baseball/roster',
    'Houston': 'https://uhcougars.com/sports/baseball/roster',
    'UCF': 'https://ucfknights.com/sports/baseball/roster',
    'BYU': 'https://byucougars.com/sports/baseball/roster',
    'Utah': 'https://utahutes.com/sports/baseball/roster',
    'Colorado': 'https://cubuffs.com/sports/baseball/roster',
}

def get_conference(team_name):
    """Get conference for a team."""
    for conf, teams in POWER_4_CONFERENCES.items():
        for team in teams:
            if team.lower() in team_name.lower() or team_name.lower() in team.lower():
                return conf
    return None

def scrape_team_roster(team_name, url):
    """Scrape roster from a team website."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            return pd.DataFrame()
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Try to find roster table
        tables = soup.find_all('table')
        roster_data = []
        
        for table in tables:
            try:
                from io import StringIO
                df = pd.read_html(StringIO(str(table)))[0]
                # Check if this looks like a roster (has name, position, class columns)
                cols = [str(c).lower() for c in df.columns]
                if any(x in ' '.join(cols) for x in ['name', 'player', 'position', 'pos', 'class', 'year']):
                    # Try to extract player info
                    for _, row in df.iterrows():
                        player = {}
                        # Find name column
                        for col in df.columns:
                            col_lower = str(col).lower()
                            col_val = str(row[col]).strip()
                            
                            if 'name' in col_lower or 'player' in col_lower:
                                if col_val and col_val != 'nan' and len(col_val) > 2:
                                    player['name'] = col_val
                            elif 'position' in col_lower or 'pos' in col_lower:
                                if col_val and col_val != 'nan':
                                    player['position'] = col_val
                            elif 'class' in col_lower or 'year' in col_lower or 'elig' in col_lower:
                                if col_val and col_val != 'nan':
                                    player['class_year'] = col_val
                        
                        if 'name' in player and player['name'] and len(player['name']) > 2:
                            player['team'] = team_name
                            player['conference'] = get_conference(team_name)
                            if 'class_year' not in player:
                                player['class_year'] = ''
                            if 'position' not in player:
                                player['position'] = ''
                            roster_data.append(player)
                    
                    if roster_data:
                        break
            except Exception as e:
                continue
        
        if roster_data:
            return pd.DataFrame(roster_data)
        
        return pd.DataFrame()
        
    except Exception as e:
        print(f"    Error scraping {team_name}: {e}")
        return pd.DataFrame()

print("="*80)
print("FETCHING TEAM ROSTERS FROM OFFICIAL TEAM WEBSITES")
print("="*80)

all_rosters = []

# Scrape all Power 4 teams
print(f"\nScraping rosters from all Power 4 teams ({len(TEAM_URLS)} teams)...\n")

successful = 0
failed = 0

for team, url in TEAM_URLS.items():
    print(f"Scraping {team}...", end=' ')
    roster = scrape_team_roster(team, url)
    if not roster.empty:
        print(f"✓ {len(roster)} players")
        all_rosters.append(roster)
        successful += 1
    else:
        print(f"✗ No data")
        failed += 1
    time.sleep(0.5)  # Be nice to servers

print(f"\n✓ Successfully scraped {successful} teams")
print(f"✗ Failed to scrape {failed} teams")

if all_rosters:
    combined = pd.concat(all_rosters, ignore_index=True)
    print(f"\n✓ Total players found: {len(combined)}")
    
    # Filter to seniors only
    print("\nFiltering to seniors only...")
    # Look for Sr., Senior, 5th, etc.
    senior_pattern = r'Sr\.|Senior|5th|Fifth|GR|Graduate'
    combined['is_senior'] = combined['class_year'].astype(str).str.contains(senior_pattern, case=False, na=False, regex=True)
    seniors = combined[combined['is_senior']].copy()
    print(f"  Found {len(seniors)} seniors")
    
    # Filter to Power 4 conferences only
    seniors = seniors[seniors['conference'].notna()].copy()
    print(f"  {len(seniors)} from Power 4 conferences")
    
    # Filter out drafted players
    print("\nFiltering out drafted players...")
    draft_filter = DraftFilter()
    draft_filter.fetch_draft_data()
    seniors = draft_filter.filter_drafted_players(seniors)
    print(f"  {len(seniors)} undrafted seniors")
    
    # Classify pitchers vs position players
    print("\nClassifying players...")
    seniors['is_pitcher'] = seniors['position'].astype(str).str.contains('P|Pitcher', case=False, na=False)
    seniors['is_position_player'] = ~seniors['is_pitcher']
    
    pitchers = seniors[seniors['is_pitcher']].copy()
    position_players = seniors[seniors['is_position_player']].copy()
    
    print(f"  Pitchers: {len(pitchers)}")
    print(f"  Position Players: {len(position_players)}")
    
    # Fetch stats for all players
    print("\n" + "="*80)
    print("FETCHING STATISTICS FROM NCAA.COM")
    print("="*80)
    
    collector = NCAADataCollector()
    pitching_stats = pd.DataFrame()
    batting_stats = pd.DataFrame()
    
    try:
        print("\nFetching pitching stats...")
        collector.fetch_pitching_stats(max_pages=20)
        pitching_stats = collector.pitching_data.copy()
        print(f"  ✓ Fetched {len(pitching_stats)} pitcher records")
    except Exception as e:
        print(f"  ⚠ Could not fetch pitching stats: {e}")
        print("  Continuing with roster data only...")
    
    try:
        print("\nFetching batting stats...")
        collector.fetch_batting_stats(max_pages=20)
        batting_stats = collector.batting_data.copy()
        print(f"  ✓ Fetched {len(batting_stats)} batter records")
    except Exception as e:
        print(f"  ⚠ Could not fetch batting stats: {e}")
        print("  Continuing with roster data only...")
    
    # Merge stats with roster data
    print("\nMerging stats with roster data...")
    
    # Initialize empty dataframes if no stats
    starters = pd.DataFrame()
    relievers = pd.DataFrame()
    hitters_with_stats = pd.DataFrame()
    
    # For pitchers: merge by name and team
    if not pitching_stats.empty and not pitchers.empty:
        # Clean names for matching
        pitching_stats['name_clean'] = pitching_stats['Player'].str.strip().str.lower()
        pitchers['name_clean'] = pitchers['name'].str.strip().str.lower()
        pitching_stats['team_clean'] = pitching_stats['Team'].str.strip().str.lower()
        pitchers['team_clean'] = pitchers['team'].str.strip().str.lower()
        
        pitchers_with_stats = pitchers.merge(
            pitching_stats,
            left_on=['name_clean', 'team_clean'],
            right_on=['name_clean', 'team_clean'],
            how='left',
            suffixes=('', '_stats')
        )
        
        # Calculate metrics for pitchers with stats
        metrics_calc = MetricsCalculator()
        pitchers_with_stats = metrics_calc.calculate_pitching_metrics(pitchers_with_stats)
        
        # Classify as starter vs reliever
        pitchers_with_stats['is_starter'] = (
            pitchers_with_stats['ip_per_app'] >= STARTER_IP_PER_APP_THRESHOLD
        ) | (
            pitchers_with_stats['ip_per_app'].isna() & 
            (pitchers_with_stats['ip'].fillna(0) >= 40)  # Fallback: high IP = likely starter
        )
        
        starters = pitchers_with_stats[pitchers_with_stats['is_starter']].copy()
        relievers = pitchers_with_stats[~pitchers_with_stats['is_starter']].copy()
        
        print(f"  Starters: {len(starters)}")
        print(f"  Relievers: {len(relievers)}")
    else:
        # If no stats, classify by position description
        print("  No pitching stats available, classifying by position...")
        starters = pitchers[pitchers['position'].str.contains('Starting|SP', case=False, na=False)].copy()
        relievers = pitchers[~pitchers['position'].str.contains('Starting|SP', case=False, na=False)].copy()
        print(f"  Starters: {len(starters)}")
        print(f"  Relievers: {len(relievers)}")
    
    # For hitters: merge by name and team
    if not batting_stats.empty and not position_players.empty:
        batting_stats['name_clean'] = batting_stats['Player'].str.strip().str.lower()
        position_players['name_clean'] = position_players['name'].str.strip().str.lower()
        batting_stats['team_clean'] = batting_stats['Team'].str.strip().str.lower()
        position_players['team_clean'] = position_players['team'].str.strip().str.lower()
        
        hitters_with_stats = position_players.merge(
            batting_stats,
            left_on=['name_clean', 'team_clean'],
            right_on=['name_clean', 'team_clean'],
            how='left',
            suffixes=('', '_stats')
        )
        
        # Calculate metrics for hitters with stats
        metrics_calc = MetricsCalculator()
        hitters_with_stats = metrics_calc.calculate_batting_metrics(hitters_with_stats)
        
        print(f"  Hitters with stats: {hitters_with_stats['Player'].notna().sum()}")
    else:
        # If no stats, use roster data
        print("  No batting stats available, using roster data...")
        hitters_with_stats = position_players.copy()
    
    # Save results
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save by conference and position type
    for conf in ['SEC', 'ACC', 'Big Ten', 'Big 12']:
        # Starting pitchers
        conf_starters = starters[starters['conference'] == conf].copy()
        if len(conf_starters) > 0:
            cols_to_save = ['name', 'team', 'position', 'class_year']
            stat_cols = ['era', 'k_per_9', 'bb_per_9', 'ip', 'w', 'l', 'sv']
            available_cols = [c for c in cols_to_save + stat_cols if c in conf_starters.columns]
            conf_starters[available_cols].to_csv(
                f"{output_dir}/{conf}_StartingPitchers.csv", index=False
            )
        
        # Relief pitchers
        conf_relievers = relievers[relievers['conference'] == conf].copy()
        if len(conf_relievers) > 0:
            cols_to_save = ['name', 'team', 'position', 'class_year']
            stat_cols = ['era', 'k_per_9', 'bb_per_9', 'ip', 'w', 'l', 'sv']
            available_cols = [c for c in cols_to_save + stat_cols if c in conf_relievers.columns]
            conf_relievers[available_cols].to_csv(
                f"{output_dir}/{conf}_ReliefPitchers.csv", index=False
            )
        
        # Position players
        conf_hitters = hitters_with_stats[hitters_with_stats['conference'] == conf].copy()
        if len(conf_hitters) > 0:
            cols_to_save = ['name', 'team', 'position', 'class_year']
            stat_cols = ['avg', 'obp', 'slg', 'ops', 'hr', 'rbi', 'r', 'k_bb_ratio']
            available_cols = [c for c in cols_to_save + stat_cols if c in conf_hitters.columns]
            conf_hitters[available_cols].to_csv(
                f"{output_dir}/{conf}_PositionPlayers.csv", index=False
            )
    
    # Save combined lists
    if not starters.empty:
        cols_to_save = ['name', 'team', 'conference', 'position', 'class_year']
        stat_cols = ['era', 'k_per_9', 'bb_per_9', 'ip']
        available_cols = [c for c in cols_to_save + stat_cols if c in starters.columns]
        starters[available_cols].to_csv(f"{output_dir}/All_StartingPitchers.csv", index=False)
    
    if not relievers.empty:
        cols_to_save = ['name', 'team', 'conference', 'position', 'class_year']
        stat_cols = ['era', 'k_per_9', 'bb_per_9', 'ip', 'sv']
        available_cols = [c for c in cols_to_save + stat_cols if c in relievers.columns]
        relievers[available_cols].to_csv(f"{output_dir}/All_ReliefPitchers.csv", index=False)
    
    if not hitters_with_stats.empty:
        cols_to_save = ['name', 'team', 'conference', 'position', 'class_year']
        stat_cols = ['avg', 'obp', 'slg', 'ops', 'hr', 'rbi']
        available_cols = [c for c in cols_to_save + stat_cols if c in hitters_with_stats.columns]
        hitters_with_stats[available_cols].to_csv(f"{output_dir}/All_PositionPlayers.csv", index=False)
    
    print(f"\n✓ Saved to {output_dir}/")
    print(f"\nSummary by Conference:")
    for conf in ['SEC', 'ACC', 'Big Ten', 'Big 12']:
        conf_starters = len(starters[starters['conference'] == conf]) if not starters.empty else 0
        conf_relievers = len(relievers[relievers['conference'] == conf]) if not relievers.empty else 0
        conf_hitters = len(hitters_with_stats[hitters_with_stats['conference'] == conf]) if not hitters_with_stats.empty else 0
        conf_total = conf_starters + conf_relievers + conf_hitters
        print(f"  {conf:12}: {conf_total} total ({conf_starters} SP, {conf_relievers} RP, {conf_hitters} H)")
    
else:
    print("\n✗ Could not scrape rosters from team websites")
    print("Trying alternative approach...")

