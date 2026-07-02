"""
Configuration settings for D1 Baseball Recruitment Dashboard
"""

# =============================================================================
# POWER 4 CONFERENCES
# =============================================================================
POWER_4_CONFERENCES = {
    "SEC": [
        "Alabama", "Arkansas", "Auburn", "Florida", "Georgia",
        "Kentucky", "LSU", "Mississippi State", "Missouri", "Ole Miss",
        "South Carolina", "Tennessee", "Texas A&M", "Vanderbilt"
    ],
    "ACC": [
        "Boston College", "Clemson", "Duke", "Florida State", "Georgia Tech",
        "Louisville", "Miami", "North Carolina", "NC State", "Notre Dame",
        "Pittsburgh", "Syracuse", "Virginia", "Virginia Tech", "Wake Forest"
    ],
    "Big Ten": [
        "Illinois", "Indiana", "Iowa", "Maryland", "Michigan",
        "Michigan State", "Minnesota", "Nebraska", "Northwestern", "Ohio State",
        "Penn State", "Purdue", "Rutgers", "Wisconsin"
    ],
    "Big 12": [
        "Arizona", "Arizona State", "Baylor", "BYU", "Cincinnati",
        "Colorado", "Houston", "Iowa State", "Kansas", "Kansas State",
        "Oklahoma State", "TCU", "Texas Tech", "UCF", "Utah", "West Virginia"
    ]
}

# Flatten to list of all Power 4 teams
ALL_POWER_4_TEAMS = []
for teams in POWER_4_CONFERENCES.values():
    ALL_POWER_4_TEAMS.extend(teams)

# =============================================================================
# RANKING WEIGHTS
# =============================================================================

# Starting Pitchers (50 players)
# Priority: Strike Rate > ERA > K/9
# NOTE: WHIP excluded - hits allowed not available on NCAA.com
STARTING_PITCHER_WEIGHTS = {
    "bb_per_9": 0.50,      # Strike rate (lower is better) - MOST IMPORTANT
    "era": 0.30,           # ERA (lower is better)
    "k_per_9": 0.20,       # Strikeout rate (higher is better) - velocity proxy
}

# Relief Pitchers (25 players)
# Priority: K/9 > ERA > IP/App ratio
# NOTE: WHIP excluded - hits allowed not available on NCAA.com
RELIEF_PITCHER_WEIGHTS = {
    "k_per_9": 0.50,       # Strikeout rate - MOST IMPORTANT for relievers
    "era": 0.35,           # ERA
    "ip_per_app": 0.15     # Innings per appearance (identifies relievers)
}

# Hitters (50 players)
# Priority: K:BB Ratio > wRC+ > wOBA > OBP > SLG > OPS
HITTER_WEIGHTS = {
    "k_bb_ratio": 0.35,    # K:BB Ratio (lower is better) - MOST IMPORTANT
    "wrc_plus": 0.20,      # wRC+ (higher is better)
    "woba": 0.15,          # wOBA (higher is better)
    "obp": 0.15,           # OBP (higher is better)
    "slg": 0.10,           # SLG (higher is better)
    "ops": 0.05            # OPS (higher is better)
}

# =============================================================================
# PLAYER THRESHOLDS
# =============================================================================

# Minimum innings pitched to qualify
MIN_IP_STARTER = 40.0      # Starters need significant innings
MIN_IP_RELIEVER = 15.0     # Relievers can have fewer innings

# Starter vs Reliever classification
# If IP/Appearances > this threshold, likely a starter
STARTER_IP_PER_APP_THRESHOLD = 4.0

# Minimum plate appearances for hitters
MIN_PA_HITTERS = 100

# =============================================================================
# DATA SETTINGS
# =============================================================================

# Current season (or most recent complete season)
CURRENT_SEASON = 2024

# Cache settings
CACHE_DIR = "data/raw"
PROCESSED_DIR = "data/processed"

# Number of players to display
NUM_STARTING_PITCHERS = 30
NUM_RELIEF_PITCHERS = 15
NUM_HITTERS = 50

# =============================================================================
# DATABASE SETTINGS
# =============================================================================

DATABASE_PATH = "data/recruitment.db"

