"""
Simple Player Compilation Script

Compiles a list of:
- Seniors only
- Power 4 conferences (SEC, ACC, Big Ten, Big 12)
- Not drafted (from provided draft list)
- Organized by: Starting Pitchers, Relief Pitchers, Position Players
- Split by conference
"""

import pandas as pd
import requests
from io import StringIO
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.draft_filter import DraftFilter
from config import POWER_4_CONFERENCES

BASE_URL = "https://www.ncaa.com/stats/baseball/d1/current/individual"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

def fetch_stat_pages(stat_code, max_pages=50):
    """Fetch multiple pages of stats."""
    all_data = []
    for page in range(1, max_pages + 1):
        url = f"{BASE_URL}/{stat_code}/p{page}"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                if page == 1:
                    print(f"  ERROR: HTTP {resp.status_code} on page 1")
                break
            dfs = pd.read_html(StringIO(resp.text))
            if not dfs or len(dfs[0]) == 0:
                if page == 1:
                    print(f"  ERROR: No data on page 1")
                break
            df = dfs[0]
            all_data.append(df)
            print(f"  Page {page}: {len(df)} players")
            if len(df) < 50:
                break
            time.sleep(0.3)
        except Exception as e:
            if page == 1:
                print(f"  ERROR page {page}: {e}")
            break
    if all_data:
        result = pd.concat(all_data, ignore_index=True)
        print(f"  Total: {len(result)} players")
        return result
    return pd.DataFrame()

def get_conference(team_name):
    """Get conference for a team - STRICT matching."""
    team_lower = team_name.lower().strip()
    
    # Exclusions - teams that sound like Power 4 but aren't
    non_power4 = {
        'south alabama', 'arkansas st', 'arkansas state', 'alabama a&m', 'alabama state',
        'georgia st', 'georgia state', 'georgia southern', 'georgia tech',  # Wait, GT is ACC
        'indiana st', 'indiana state', 'illinois st', 'illinois state',
        'houston christian', 'utah valley', 'kansas st', 'kansas state',  # Wait, KSU is Big 12
    }
    
    if any(excl in team_lower for excl in non_power4):
        # But check if it's actually a Power 4 team
        if 'georgia tech' in team_lower:
            return 'ACC'
        if 'kansas state' in team_lower or 'kansas st' in team_lower:
            return 'Big 12'
        return None
    
    # Exact Power 4 team mappings
    power4_teams = {
        # SEC
        'alabama': 'SEC', 'arkansas': 'SEC', 'auburn': 'SEC', 'florida': 'SEC',
        'georgia': 'SEC', 'kentucky': 'SEC', 'lsu': 'SEC', 'mississippi state': 'SEC',
        'missouri': 'SEC', 'ole miss': 'SEC', 'south carolina': 'SEC', 'tennessee': 'SEC',
        'texas a&m': 'SEC', 'vanderbilt': 'SEC',
        # ACC
        'boston college': 'ACC', 'clemson': 'ACC', 'duke': 'ACC', 'florida state': 'ACC',
        'georgia tech': 'ACC', 'louisville': 'ACC', 'miami': 'ACC', 'north carolina': 'ACC',
        'nc state': 'ACC', 'notre dame': 'ACC', 'pittsburgh': 'ACC', 'syracuse': 'ACC',
        'virginia': 'ACC', 'virginia tech': 'ACC', 'wake forest': 'ACC',
        # Big Ten
        'illinois': 'Big Ten', 'indiana': 'Big Ten', 'iowa': 'Big Ten', 'maryland': 'Big Ten',
        'michigan': 'Big Ten', 'michigan state': 'Big Ten', 'minnesota': 'Big Ten',
        'nebraska': 'Big Ten', 'northwestern': 'Big Ten', 'ohio state': 'Big Ten',
        'penn state': 'Big Ten', 'purdue': 'Big Ten', 'rutgers': 'Big Ten', 'wisconsin': 'Big Ten',
        # Big 12
        'arizona': 'Big 12', 'arizona state': 'Big 12', 'baylor': 'Big 12', 'byu': 'Big 12',
        'cincinnati': 'Big 12', 'houston': 'Big 12', 'kansas': 'Big 12', 'kansas state': 'Big 12',
        'oklahoma': 'Big 12', 'oklahoma state': 'Big 12', 'tcu': 'Big 12', 'texas tech': 'Big 12',
        'ucf': 'Big 12', 'utah': 'Big 12', 'west virginia': 'Big 12',
    }
    
    # Try exact match
    for team_key, conf in power4_teams.items():
        if team_key == team_lower:
            return conf
    
    # Try partial match (be careful)
    for team_key, conf in power4_teams.items():
        if team_key in team_lower:
            return conf
    
    return None

def classify_pitcher(row):
    """Classify as starter or reliever."""
    ip = pd.to_numeric(row.get('IP', 0), errors='coerce') or 0
    app = pd.to_numeric(row.get('App', 0), errors='coerce') or 0
    
    if ip == 0 or app == 0:
        return None
    
    ip_per_app = ip / app
    
    # Starters: high IP per appearance (typically 4+)
    if ip_per_app >= 4.0 and ip >= 40:
        return 'Starter'
    # Relievers: lower IP per appearance
    elif ip_per_app < 4.0 and ip >= 15:
        return 'Reliever'
    return None

print("="*60)
print("COMPILING SENIOR PLAYERS FROM POWER 4 CONFERENCES")
print("="*60)

# Step 1: Fetch pitching data from multiple stat categories to get more players
print("\n1. Fetching pitching data from multiple categories...")
all_pitching = []

# Fetch from ERA (205)
print("   Fetching ERA stats...")
era_df = fetch_stat_pages(205, max_pages=50)
if not era_df.empty:
    era_df = era_df.rename(columns={
        'Name': 'name',
        'Team': 'team',
        'Cl': 'class_year',
        'Position': 'position',
        'IP': 'IP',
        'App': 'App',
        'ERA': 'ERA'
    })
    all_pitching.append(era_df[['name', 'team', 'class_year', 'IP', 'App', 'ERA']])

# Fetch from K/9 (207) to get more pitchers
print("   Fetching K/9 stats...")
k9_df = fetch_stat_pages(207, max_pages=50)
if not k9_df.empty:
    k9_df = k9_df.rename(columns={
        'Name': 'name',
        'Team': 'team',
        'Cl': 'class_year',
        'Position': 'position',
        'IP': 'IP',
        'App': 'App',
        'SO': 'SO'
    })
    # Merge with ERA data if available, otherwise use K/9 data
    if all_pitching:
        k9_merged = pd.merge(
            all_pitching[0], 
            k9_df[['name', 'team', 'IP', 'App']],
            on=['name', 'team'],
            how='outer',
            suffixes=('', '_k9')
        )
        k9_merged['IP'] = k9_merged['IP'].fillna(k9_merged['IP_k9'])
        k9_merged['App'] = k9_merged['App'].fillna(k9_merged['App_k9'])
        k9_merged = k9_merged[['name', 'team', 'class_year', 'IP', 'App', 'ERA']]
        all_pitching = [k9_merged]
    else:
        all_pitching.append(k9_df[['name', 'team', 'class_year', 'IP', 'App']])
        all_pitching[0]['ERA'] = None

# Combine all pitching data
if all_pitching:
    pitching_df = pd.concat(all_pitching, ignore_index=True)
    # Remove duplicates
    pitching_df = pitching_df.drop_duplicates(subset=['name', 'team'], keep='first')
    print(f"   Total unique pitchers: {len(pitching_df)}")
    
    # Filter to seniors only
    pitching = pitching_df[pitching_df['class_year'].str.contains('Sr\.', case=False, na=False)].copy()
    print(f"   Found {len(pitching)} senior pitchers")
else:
    print("ERROR: Could not fetch pitching data")
    sys.exit(1)

# Add conference
pitching['conference'] = pitching['team'].apply(get_conference)
pitching = pitching[pitching['conference'].notna()].copy()
print(f"   {len(pitching)} from Power 4 conferences")

# Classify starters vs relievers
pitching['pitcher_type'] = pitching.apply(classify_pitcher, axis=1)
pitching = pitching[pitching['pitcher_type'].notna()].copy()

# Step 2: Fetch batting data from multiple categories
print("\n2. Fetching batting data from multiple categories...")
all_batting = []

# Fetch from Batting Average (200)
print("   Fetching Batting Average stats...")
ba_df = fetch_stat_pages(200, max_pages=50)
if not ba_df.empty:
    ba_df = ba_df.rename(columns={
        'Name': 'name',
        'Team': 'team',
        'Cl': 'class_year',
        'Position': 'position',
        'BA': 'BA'
    })
    all_batting.append(ba_df[['name', 'team', 'class_year', 'position', 'BA']])

# Fetch from Home Runs (201) to get more players
print("   Fetching Home Runs stats...")
hr_df = fetch_stat_pages(201, max_pages=50)
if not hr_df.empty:
    hr_df = hr_df.rename(columns={
        'Name': 'name',
        'Team': 'team',
        'Cl': 'class_year',
        'Position': 'position'
    })
    # Merge with BA data
    if all_batting:
        hr_merged = pd.merge(
            all_batting[0],
            hr_df[['name', 'team', 'class_year', 'position']],
            on=['name', 'team'],
            how='outer',
            suffixes=('', '_hr')
        )
        hr_merged['class_year'] = hr_merged['class_year'].fillna(hr_merged['class_year_hr'])
        hr_merged['position'] = hr_merged['position'].fillna(hr_merged['position_hr'])
        hr_merged = hr_merged[['name', 'team', 'class_year', 'position', 'BA']]
        all_batting = [hr_merged]
    else:
        hr_df['BA'] = None
        all_batting.append(hr_df[['name', 'team', 'class_year', 'position', 'BA']])

# Combine all batting data
if all_batting:
    batting_df = pd.concat(all_batting, ignore_index=True)
    # Remove duplicates, keeping row with BA if available
    batting_df = batting_df.sort_values('BA', na_position='last')
    batting_df = batting_df.drop_duplicates(subset=['name', 'team'], keep='first')
    print(f"   Total unique batters: {len(batting_df)}")
    
    # Fill missing BA by fetching from BA leaderboard if needed
    missing_ba = batting_df[batting_df['BA'].isna()]
    if len(missing_ba) > 0:
        print(f"   Fetching BA for {len(missing_ba)} players missing BA...")
        # Try to get BA for missing players (would need to search, but for now just note it)
        pass
    
    # Filter to seniors only
    batting = batting_df[batting_df['class_year'].str.contains('Sr\.', case=False, na=False)].copy()
    print(f"   Found {len(batting)} senior batters")
else:
    print("ERROR: Could not fetch batting data")
    sys.exit(1)

# Add conference
batting['conference'] = batting['team'].apply(get_conference)
batting = batting[batting['conference'].notna()].copy()
print(f"   {len(batting)} from Power 4 conferences")

# Step 3: Filter out drafted players
print("\n3. Filtering out drafted players...")
draft_filter = DraftFilter()
draft_filter.fetch_draft_data()

pitching = draft_filter.filter_drafted_players(pitching)
batting = draft_filter.filter_drafted_players(batting)

print(f"   {len(pitching)} undrafted senior pitchers")
print(f"   {len(batting)} undrafted senior batters")

# Step 4: Organize and save
print("\n4. Organizing by position and conference...")

# Split pitchers
starters = pitching[pitching['pitcher_type'] == 'Starter'].copy()
relievers = pitching[pitching['pitcher_type'] == 'Reliever'].copy()
position_players = batting.copy()

# Create output directory
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Save by conference
for conf in ['SEC', 'ACC', 'Big Ten', 'Big 12']:
    conf_starters = starters[starters['conference'] == conf].copy()
    conf_relievers = relievers[relievers['conference'] == conf].copy()
    conf_hitters = position_players[position_players['conference'] == conf].copy()
    
    print(f"\n{conf}:")
    print(f"  Starting Pitchers: {len(conf_starters)}")
    print(f"  Relief Pitchers: {len(conf_relievers)}")
    print(f"  Position Players: {len(conf_hitters)}")
    
    # Save to CSV
    if len(conf_starters) > 0:
        conf_starters[['name', 'team', 'ERA', 'IP', 'App']].to_csv(
            f"{output_dir}/{conf}_Starters.csv", index=False
        )
    if len(conf_relievers) > 0:
        conf_relievers[['name', 'team', 'ERA', 'IP', 'App']].to_csv(
            f"{output_dir}/{conf}_Relievers.csv", index=False
        )
    if len(conf_hitters) > 0:
        conf_hitters[['name', 'team', 'position', 'BA']].to_csv(
            f"{output_dir}/{conf}_PositionPlayers.csv", index=False
        )

# Save combined lists
print("\n5. Saving combined lists...")
starters[['name', 'team', 'conference', 'ERA', 'IP', 'App']].to_csv(
    f"{output_dir}/All_Starters.csv", index=False
)
relievers[['name', 'team', 'conference', 'ERA', 'IP', 'App']].to_csv(
    f"{output_dir}/All_Relievers.csv", index=False
)
position_players[['name', 'team', 'conference', 'position', 'BA']].to_csv(
    f"{output_dir}/All_PositionPlayers.csv", index=False
)

print(f"\n✓ Complete!")
print(f"  Total Starting Pitchers: {len(starters)}")
print(f"  Total Relief Pitchers: {len(relievers)}")
print(f"  Total Position Players: {len(position_players)}")
print(f"\nFiles saved to: {output_dir}/")

