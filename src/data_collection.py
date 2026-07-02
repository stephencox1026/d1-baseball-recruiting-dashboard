"""
Data Collection Module for D1 Baseball Recruitment Dashboard

Fetches REAL player statistics from NCAA.com using VERIFIED stat codes.
"""

import pandas as pd
import numpy as np
import os
import sys
import time
import requests
from io import StringIO
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    POWER_4_CONFERENCES, 
    ALL_POWER_4_TEAMS, 
    CURRENT_SEASON,
    CACHE_DIR,
    MIN_IP_STARTER,
    MIN_IP_RELIEVER,
    MIN_PA_HITTERS
)
from src.utils import ensure_directories, save_dataframe


class NCAADataCollector:
    """
    Collects real baseball statistics from NCAA.com using verified stat codes.
    """
    
    BASE_URL = "https://www.ncaa.com/stats/baseball/d1/current/individual"
    
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    def __init__(self, season: int = CURRENT_SEASON):
        self.season = season
        self.pitching_data = pd.DataFrame()
        self.batting_data = pd.DataFrame()
        ensure_directories()
    
    def _fetch_stat_pages(self, stat_code: int, max_pages: int = 10, 
                          min_delay: float = 0.5, required: bool = True) -> pd.DataFrame:
        """
        Fetch multiple pages of a stat category from NCAA.com
        
        Args:
            stat_code: NCAA stat code (e.g., 200 for batting avg, 205 for ERA)
            max_pages: Maximum number of pages to fetch
            min_delay: Minimum delay between requests (be nice to server)
            required: If True, raise error if no data found
            
        Returns:
            DataFrame with all players from all pages
            
        Raises:
            ValueError: If required=True and no data was fetched
        """
        all_data = []
        
        for page in range(1, max_pages + 1):
            url = f"{self.BASE_URL}/{stat_code}/p{page}"
            
            try:
                resp = requests.get(url, headers=self.HEADERS, timeout=15)
                
                if resp.status_code != 200:
                    if required and page == 1:
                        raise ValueError(f"Failed to fetch stat code {stat_code}: HTTP {resp.status_code}")
                    print(f"  Page {page}: Status {resp.status_code}, stopping")
                    break
                
                try:
                    dfs = pd.read_html(StringIO(resp.text))
                except ValueError as ve:
                    # No tables found - might be last page or structure changed
                    if required and page == 1:
                        raise ValueError(f"No tables found for stat code {stat_code} on NCAA.com")
                    print(f"  Page {page}: No tables found, stopping")
                    break
                
                if not dfs or len(dfs[0]) == 0:
                    if required and page == 1:
                        raise ValueError(f"No data found for stat code {stat_code} on NCAA.com")
                    print(f"  Page {page}: No data, stopping")
                    break
                
                df = dfs[0]
                all_data.append(df)
                print(f"  Page {page}: {len(df)} players (ranks {df.iloc[0]['Rank']}-{df.iloc[-1]['Rank']})")
                
                # Stop if we got fewer than 50 (last page)
                if len(df) < 50:
                    break
                    
                time.sleep(min_delay)
                
            except ValueError:
                raise  # Re-raise validation errors
            except Exception as e:
                if required and page == 1:
                    raise ValueError(f"Error fetching stat code {stat_code}: {e}")
                print(f"  Page {page}: Error - {e}")
                break
        
        if all_data:
            result = pd.concat(all_data, ignore_index=True)
            if len(result) == 0 and required:
                raise ValueError(f"No data returned for stat code {stat_code}")
            return result
        
        if required:
            raise ValueError(f"Failed to fetch any data for stat code {stat_code} from NCAA.com")
        return pd.DataFrame()
    
    def fetch_pitching_stats(self, max_pages: int = 10) -> pd.DataFrame:
        """
        Fetch all pitching statistics from NCAA.com
        
        Collects: ERA, K/9, IP, Strikeouts, Walks (using verified stat codes)
        """
        print("\n" + "="*60)
        print("FETCHING PITCHING DATA FROM NCAA.COM")
        print("="*60)
        
        # Start with ERA (205) - VERIFIED WORKING
        print("\nFetching ERA stats (code 205)...")
        try:
            era_df = self._fetch_stat_pages(205, max_pages, required=True)
            if era_df.empty:
                raise ValueError("ERA data is empty")
        except Exception as e:
            raise ValueError(f"CRITICAL: Cannot fetch ERA data. Error: {e}")
        
        print(f"Total ERA records: {len(era_df)}")
        
        # Rename columns for clarity
        era_df = era_df.rename(columns={
            'Name': 'name',
            'Team': 'team', 
            'Cl': 'class_year',
            'Position': 'position',
            'App': 'appearances',
            'IP': 'ip',
            'R': 'runs',
            'ER': 'earned_runs',
            'ERA': 'era'
        })
        
        # Fetch K/9 stats (207) - VERIFIED WORKING - has SO column
        print("\nFetching K/9 stats (code 207)...")
        try:
            k9_df = self._fetch_stat_pages(207, max_pages, required=True)
            print(f"Total K/9 records: {len(k9_df)}")
            k9_df = k9_df.rename(columns={
                'Name': 'name',
                'Team': 'team',
                'SO': 'strikeouts',
                'K/9': 'k_per_9'
            })
            # Merge K/9 data
            era_df = era_df.merge(
                k9_df[['name', 'team', 'strikeouts', 'k_per_9']],
                on=['name', 'team'],
                how='inner'  # Only keep pitchers with real strikeout data
            )
            era_df['strikeouts'] = pd.to_numeric(era_df['strikeouts'], errors='coerce').fillna(0).astype(int)
            era_df['k_per_9'] = pd.to_numeric(era_df['k_per_9'], errors='coerce')
            print(f"  ✓ Successfully merged {len(era_df)} pitchers with real strikeout data")
        except Exception as e:
            raise ValueError(f"CRITICAL: Cannot proceed without real strikeout data. Error: {e}")
        
        # Fetch Saves stats (209) - VERIFIED WORKING
        print("\nFetching Saves stats (code 209)...")
        saves_df = self._fetch_stat_pages(209, max_pages=5, required=False)  # Not critical
        
        if not saves_df.empty:
            print(f"Total Saves records: {len(saves_df)}")
            saves_df = saves_df.rename(columns={
                'Name': 'name',
                'Team': 'team',
                'SV': 'saves'
            })
            # Merge saves data
            era_df = era_df.merge(
                saves_df[['name', 'team', 'saves']],
                on=['name', 'team'],
                how='left'
            )
            era_df['saves'] = pd.to_numeric(era_df['saves'], errors='coerce').fillna(0).astype(int)
        else:
            era_df['saves'] = 0
        
        # Search for Walks (BB) for pitching - need to find correct code
        print("\nSearching for Pitching Walks (BB) stat code...")
        walks_found = False
        for code in [206, 208, 210, 211, 212, 213, 214, 216, 217, 218, 219, 220]:
            try:
                walks_df = self._fetch_stat_pages(code, max_pages=1, required=False)
                if not walks_df.empty and 'BB' in walks_df.columns:
                    print(f"  ✓ Found walks at code {code}")
                    walks_df = self._fetch_stat_pages(code, max_pages, required=True)
                    walks_df = walks_df.rename(columns={
                        'Name': 'name',
                        'Team': 'team',
                        'BB': 'walks'
                    })
                    era_df = era_df.merge(
                        walks_df[['name', 'team', 'walks']],
                        on=['name', 'team'],
                        how='inner'
                    )
                    era_df['walks'] = pd.to_numeric(era_df['walks'], errors='coerce').fillna(0).astype(int)
                    if (era_df['walks'] > 0).any():
                        walks_found = True
                        print(f"  ✓ Successfully merged {len(era_df)} pitchers with real walk data")
                        break
            except:
                continue
        
        if not walks_found:
            print(f"  ⚠ WARNING: Cannot find pitching walks (BB) stat code on NCAA.com.")
            print(f"  ⚠ BB/9 will be estimated as 0 (cannot calculate without walks data)")
            era_df['walks'] = 0
            era_df['bb_per_9'] = 0.0
        
        # Add derived columns
        era_df['ip'] = pd.to_numeric(era_df['ip'].astype(str).str.replace('.1', '.33').str.replace('.2', '.67'), errors='coerce')
        era_df['appearances'] = pd.to_numeric(era_df['appearances'], errors='coerce').fillna(0).astype(int)
        
        # Calculate BB/9 from REAL walks data
        era_df['bb_per_9'] = np.where(
            era_df['ip'] > 0,
            (era_df['walks'] / era_df['ip'] * 9).round(2),
            0
        )
        
        # NOTE: Hits allowed and WHIP are NOT available on NCAA.com as separate stats
        # We cannot calculate WHIP without real hits data, so it's excluded from rankings
        # All rankings use ONLY real data: ERA, K/9, BB/9, IP
        era_df['whip'] = np.nan  # Not available - cannot calculate without hits
        print(f"  ⚠ WHIP not available (hits allowed not on NCAA.com - excluded from rankings)")
        
        # Add player ID
        era_df['player_id'] = range(1, len(era_df) + 1)
        
        # Add conference
        era_df['conference'] = era_df['team'].apply(self._get_conference)
        
        # Mark as not drafted
        era_df['is_drafted'] = False
        
        self.pitching_data = era_df
        print(f"\nTotal pitchers collected: {len(era_df)}")
        
        return era_df
    
    def fetch_batting_stats(self, max_pages: int = 10) -> pd.DataFrame:
        """
        Fetch all batting statistics from NCAA.com using VERIFIED stat codes.
        
        Collects: BA, AB, H, HR, 2B, 3B, SLG, and calculates OBP, Walks from available data
        """
        print("\n" + "="*60)
        print("FETCHING BATTING DATA FROM NCAA.COM")
        print("="*60)
        
        # Start with Batting Average (200) - VERIFIED WORKING - has AB, H, BA
        print("\nFetching Batting Average stats (code 200)...")
        try:
            batting_df = self._fetch_stat_pages(200, max_pages, required=True)
            if batting_df.empty:
                raise ValueError("Batting average data is empty")
        except Exception as e:
            raise ValueError(f"CRITICAL: Cannot fetch batting average data. Error: {e}")
        
        print(f"Total batting records: {len(batting_df)}")
        
        # Rename base columns
        batting_df = batting_df.rename(columns={
            'Name': 'name',
            'Team': 'team',
            'Cl': 'class_year',
            'Position': 'position',
            'G': 'games',
            'AB': 'at_bats',
            'H': 'hits',
            'BA': 'avg'
        })
        
        # Fetch Home Runs (201) - VERIFIED WORKING
        print("\nFetching Home Runs stats (code 201)...")
        try:
            hr_df = self._fetch_stat_pages(201, max_pages, required=True)
            hr_df = hr_df.rename(columns={
                'Name': 'name',
                'Team': 'team',
                'HR': 'home_runs'
            })
            batting_df = batting_df.merge(
                hr_df[['name', 'team', 'home_runs']],
                on=['name', 'team'],
                how='inner'
            )
            batting_df['home_runs'] = pd.to_numeric(batting_df['home_runs'], errors='coerce').fillna(0).astype(int)
            print(f"  ✓ Merged {len(batting_df)} players with real HR data")
        except Exception as e:
            raise ValueError(f"CRITICAL: Cannot fetch home runs. Error: {e}")
        
        # Fetch Doubles (203) - VERIFIED WORKING
        print("\nFetching Doubles stats (code 203)...")
        try:
            doubles_df = self._fetch_stat_pages(203, max_pages, required=True)
            doubles_df = doubles_df.rename(columns={
                'Name': 'name',
                'Team': 'team',
                '2B': 'doubles'
            })
            batting_df = batting_df.merge(
                doubles_df[['name', 'team', 'doubles']],
                on=['name', 'team'],
                how='inner'
            )
            batting_df['doubles'] = pd.to_numeric(batting_df['doubles'], errors='coerce').fillna(0).astype(int)
            print(f"  ✓ Merged {len(batting_df)} players with real doubles data")
        except Exception as e:
            raise ValueError(f"CRITICAL: Cannot fetch doubles. Error: {e}")
        
        # Fetch Triples (204) - VERIFIED WORKING
        print("\nFetching Triples stats (code 204)...")
        try:
            triples_df = self._fetch_stat_pages(204, max_pages, required=True)
            triples_df = triples_df.rename(columns={
                'Name': 'name',
                'Team': 'team',
                '3B': 'triples'
            })
            batting_df = batting_df.merge(
                triples_df[['name', 'team', 'triples']],
                on=['name', 'team'],
                how='inner'
            )
            batting_df['triples'] = pd.to_numeric(batting_df['triples'], errors='coerce').fillna(0).astype(int)
            print(f"  ✓ Merged {len(batting_df)} players with real triples data")
        except Exception as e:
            raise ValueError(f"CRITICAL: Cannot fetch triples. Error: {e}")
        
        # Fetch Slugging (321) - VERIFIED WORKING
        print("\nFetching Slugging Percentage stats (code 321)...")
        try:
            slg_df = self._fetch_stat_pages(321, max_pages, required=True)
            slg_df = slg_df.rename(columns={
                'Name': 'name',
                'Team': 'team',
                'SLG PCT': 'slg'
            })
            batting_df = batting_df.merge(
                slg_df[['name', 'team', 'slg']],
                on=['name', 'team'],
                how='inner'
            )
            batting_df['slg'] = pd.to_numeric(batting_df['slg'], errors='coerce')
            print(f"  ✓ Merged {len(batting_df)} players with real SLG data")
        except Exception as e:
            raise ValueError(f"CRITICAL: Cannot fetch slugging. Error: {e}")
        
        # Search for Walks (BB) and Strikeouts (SO) - need to find correct codes
        print("\nSearching for Walks (BB) stat code...")
        walks_found = False
        for code in range(200, 400):
            try:
                test_df = self._fetch_stat_pages(code, max_pages=1, required=False)
                if not test_df.empty and 'BB' in test_df.columns:
                    print(f"  ✓ Found walks at code {code}")
                    walks_df = self._fetch_stat_pages(code, max_pages, required=True)
                    walks_df = walks_df.rename(columns={
                        'Name': 'name',
                        'Team': 'team',
                        'BB': 'walks'
                    })
                    batting_df = batting_df.merge(
                        walks_df[['name', 'team', 'walks']],
                        on=['name', 'team'],
                        how='inner'
                    )
                    batting_df['walks'] = pd.to_numeric(batting_df['walks'], errors='coerce').fillna(0).astype(int)
                    if (batting_df['walks'] > 0).any():
                        walks_found = True
                        print(f"  ✓ Merged {len(batting_df)} players with real walk data")
                        break
            except:
                continue
        
        if not walks_found:
            raise ValueError("CRITICAL: Cannot find walks (BB) stat code. K:BB ratio is 35% weight!")
        
        print("\nSearching for Strikeouts (SO) stat code...")
        so_found = False
        for code in range(200, 400):
            try:
                test_df = self._fetch_stat_pages(code, max_pages=1, required=False)
                if not test_df.empty and 'SO' in test_df.columns and code != 207:  # 207 is pitching SO
                    print(f"  ✓ Found strikeouts at code {code}")
                    so_df = self._fetch_stat_pages(code, max_pages, required=True)
                    so_df = so_df.rename(columns={
                        'Name': 'name',
                        'Team': 'team',
                        'SO': 'strikeouts'
                    })
                    batting_df = batting_df.merge(
                        so_df[['name', 'team', 'strikeouts']],
                        on=['name', 'team'],
                        how='inner'
                    )
                    batting_df['strikeouts'] = pd.to_numeric(batting_df['strikeouts'], errors='coerce').fillna(0).astype(int)
                    if (batting_df['strikeouts'] > 0).any():
                        so_found = True
                        print(f"  ✓ Merged {len(batting_df)} players with real strikeout data")
                        break
            except:
                continue
        
        if not so_found:
            print(f"  ⚠ WARNING: Cannot find strikeouts (SO) stat code on NCAA.com.")
            print(f"  ⚠ K:BB ratio will be estimated (cannot calculate without strikeout data)")
            batting_df['strikeouts'] = 0
            batting_df['k_bb_ratio'] = 999.0  # High value indicates poor ratio
        
        # Calculate singles from real data
        batting_df['singles'] = batting_df['hits'] - batting_df['doubles'] - batting_df['triples'] - batting_df['home_runs']
        batting_df['singles'] = batting_df['singles'].clip(lower=0)
        
        # Calculate OBP from real data: OBP = (H + BB) / (AB + BB)
        # Note: HBP not available, so this is slightly lower than true OBP
        batting_df['plate_appearances'] = (batting_df['at_bats'] + batting_df['walks']).astype(int)
        batting_df['obp'] = ((batting_df['hits'] + batting_df['walks']) / batting_df['plate_appearances']).round(3)
        
        # Calculate K:BB ratio from REAL data
        batting_df['k_bb_ratio'] = np.where(
            batting_df['walks'] > 0,
            (batting_df['strikeouts'] / batting_df['walks']).round(2),
            np.where(batting_df['strikeouts'] > 0, batting_df['strikeouts'], 999)
        )
        
        # Calculate OPS from real OBP and SLG
        batting_df['ops'] = (batting_df['obp'] + batting_df['slg']).round(3)
        
        # Calculate wOBA using ONLY REAL data (NO HBP)
        woba_num = (0.69*batting_df['walks'] + 0.89*batting_df['singles'] + 
                   1.27*batting_df['doubles'] + 1.62*batting_df['triples'] + 2.10*batting_df['home_runs'])
        woba_denom = batting_df['at_bats'] + batting_df['walks']
        batting_df['woba'] = np.where(
            woba_denom > 0,
            (woba_num / woba_denom).round(3),
            0
        )
        
        # Calculate wRC+ from wOBA
        league_woba = 0.320
        woba_scale = 1.25
        batting_df['wrc_plus'] = ((batting_df['woba'] - league_woba) / woba_scale * 100 + 100).astype(int)
        batting_df['wrc_plus'] = batting_df['wrc_plus'].clip(50, 200)
        
        # Add player ID
        batting_df['player_id'] = range(1, len(batting_df) + 1)
        
        # Add conference
        batting_df['conference'] = batting_df['team'].apply(self._get_conference)
        
        # Mark as not drafted
        batting_df['is_drafted'] = False
        
        self.batting_data = batting_df
        print(f"\nTotal batters collected: {len(batting_df)}")
        print(f"  With real K:BB data: {len(batting_df[batting_df['walks'] > 0])}")
        
        return batting_df
    
    def _get_conference(self, team_name: str) -> str:
        """Determine conference for a team."""
        team_lower = team_name.lower().strip()
        
        # Exclusions - teams that sound like Power 4 but aren't
        non_power4 = [
            'alabama st', 'alabama a&m', 'alabama state',
            'florida a&m', 'florida atlantic', 'florida gulf', 'fgcu', 'fiu', 'florida int',
            'georgia st', 'georgia state', 'georgia southern',
            'missouri st', 'missouri state',
            'northwestern st', 'northwestern state',
            'utah valley', 'utah tech', 'southern utah',
            'michigan tech',
            'indiana st', 'indiana state',
            'miami (oh)', 'miami ohio',
            'louisiana tech', 'la tech',
        ]
        
        for exclusion in non_power4:
            if exclusion in team_lower:
                return 'Other'
        
        # Exact team mappings for Power 4
        team_conference_map = {
            # SEC
            'alabama': 'SEC', 'arkansas': 'SEC', 'auburn': 'SEC', 
            'florida': 'SEC',
            'georgia': 'SEC',
            'kentucky': 'SEC', 'lsu': 'SEC',
            'mississippi st.': 'SEC', 'miss. state': 'SEC', 'mississippi state': 'SEC',
            'missouri': 'SEC',
            'ole miss': 'SEC',
            'south carolina': 'SEC', 'tennessee': 'SEC',
            'texas a&m': 'SEC', 'vanderbilt': 'SEC',
            
            # ACC  
            'boston college': 'ACC', 'clemson': 'ACC', 'duke': 'ACC',
            'florida st.': 'ACC', 'florida state': 'ACC',
            'georgia tech': 'ACC',
            'louisville': 'ACC', 
            'miami (fl)': 'ACC', 'miami': 'ACC',
            'north carolina': 'ACC', 'nc state': 'ACC',
            'notre dame': 'ACC', 'pittsburgh': 'ACC', 'pitt': 'ACC',
            'syracuse': 'ACC', 'virginia': 'ACC',
            'virginia tech': 'ACC', 'wake forest': 'ACC',
            
            # Big Ten
            'illinois': 'Big Ten', 'indiana': 'Big Ten', 'iowa': 'Big Ten',
            'maryland': 'Big Ten', 'michigan': 'Big Ten', 
            'michigan st.': 'Big Ten', 'michigan state': 'Big Ten',
            'minnesota': 'Big Ten', 'nebraska': 'Big Ten', 
            'northwestern': 'Big Ten',
            'ohio st.': 'Big Ten', 'ohio state': 'Big Ten',
            'penn st.': 'Big Ten', 'penn state': 'Big Ten', 
            'purdue': 'Big Ten', 'rutgers': 'Big Ten', 'wisconsin': 'Big Ten',
            
            # Big 12
            'arizona': 'Big 12', 'arizona st.': 'Big 12', 'arizona state': 'Big 12',
            'baylor': 'Big 12', 'byu': 'Big 12',
            'cincinnati': 'Big 12', 'colorado': 'Big 12', 'houston': 'Big 12',
            'iowa st.': 'Big 12', 'iowa state': 'Big 12',
            'kansas': 'Big 12', 'kansas st.': 'Big 12', 'kansas state': 'Big 12',
            'oklahoma st.': 'Big 12', 'oklahoma state': 'Big 12',
            'oklahoma': 'Big 12',
            'tcu': 'Big 12', 'texas tech': 'Big 12', 
            'ucf': 'Big 12', 'utah': 'Big 12',
            'west virginia': 'Big 12',
        }
        
        # Try exact match first
        for team_key, conf in team_conference_map.items():
            if team_key == team_lower:
                return conf
        
        # Try partial match
        for team_key, conf in team_conference_map.items():
            if team_key in team_lower:
                return conf
        
        return 'Other'
    
    def filter_power_4(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter to only Power 4 conference players."""
        return df[df['conference'].isin(['SEC', 'ACC', 'Big Ten', 'Big 12'])].copy()
    
    def collect_all_data(self, use_cache: bool = True, max_pages: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Collect all pitching and batting data.
        
        Args:
            use_cache: If True, use cached data if available and recent
            max_pages: Maximum pages to fetch per stat (50 players/page) - default 20 for ~1000 players
            
        Returns:
            Tuple of (pitching_df, batting_df)
        """
        pitching_cache = os.path.join(CACHE_DIR, f"pitching_{self.season}_real.csv")
        batting_cache = os.path.join(CACHE_DIR, f"batting_{self.season}_real.csv")
        
        # Check cache age (use cache if less than 24 hours old)
        cache_valid = False
        if use_cache and os.path.exists(pitching_cache) and os.path.exists(batting_cache):
            cache_age = datetime.now().timestamp() - os.path.getmtime(pitching_cache)
            if cache_age < 86400:  # 24 hours
                cache_valid = True
        
        if cache_valid:
            print("Loading data from cache...")
            self.pitching_data = pd.read_csv(pitching_cache)
            self.batting_data = pd.read_csv(batting_cache)
        else:
            print("Fetching fresh data from NCAA.com...")
            self.fetch_pitching_stats(max_pages)
            self.fetch_batting_stats(max_pages)
            
            # Save to cache
            if not self.pitching_data.empty:
                save_dataframe(self.pitching_data, f"pitching_{self.season}_real.csv", CACHE_DIR)
            if not self.batting_data.empty:
                save_dataframe(self.batting_data, f"batting_{self.season}_real.csv", CACHE_DIR)
        
        print(f"\nLoaded {len(self.pitching_data)} pitchers and {len(self.batting_data)} batters")
        
        # Show Power 4 breakdown
        p4_pitchers = self.filter_power_4(self.pitching_data)
        p4_batters = self.filter_power_4(self.batting_data)
        print(f"Power 4 conference players: {len(p4_pitchers)} pitchers, {len(p4_batters)} batters")
        
        return self.pitching_data, self.batting_data
    
    def refresh_data(self, max_pages: int = 20) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Force refresh data from NCAA.com."""
        return self.collect_all_data(use_cache=False, max_pages=max_pages)


# Backward compatibility alias
DataCollector = NCAADataCollector


def main():
    """Test data collection."""
    collector = NCAADataCollector()
    pitching, batting = collector.collect_all_data(use_cache=False, max_pages=5)
    
    print("\n" + "="*60)
    print("PITCHING DATA SAMPLE")
    print("="*60)
    print(pitching[['name', 'team', 'conference', 'era', 'k_per_9', 'bb_per_9', 'ip']].head(10))
    
    print("\n" + "="*60)
    print("BATTING DATA SAMPLE")
    print("="*60)
    print(batting[['name', 'team', 'conference', 'avg', 'obp', 'slg', 'k_bb_ratio']].head(10))
    
    # Power 4 only
    print("\n" + "="*60)
    print("POWER 4 PITCHERS")
    print("="*60)
    p4_pitching = collector.filter_power_4(pitching)
    print(p4_pitching[['name', 'team', 'conference', 'era', 'k_per_9', 'bb_per_9']].head(10))


if __name__ == "__main__":
    main()
