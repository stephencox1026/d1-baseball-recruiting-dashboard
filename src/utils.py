"""
Utility functions for D1 Baseball Recruitment Dashboard
"""

import os
import json
import pandas as pd
from datetime import datetime
from pathlib import Path


def ensure_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "data/raw",
        "data/processed",
        "data/cache"
    ]
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def save_dataframe(df: pd.DataFrame, filename: str, directory: str = "data/processed"):
    """Save a DataFrame to CSV with timestamp."""
    ensure_directories()
    filepath = os.path.join(directory, filename)
    df.to_csv(filepath, index=False)
    print(f"Saved {len(df)} records to {filepath}")
    return filepath


def load_dataframe(filename: str, directory: str = "data/processed") -> pd.DataFrame:
    """Load a DataFrame from CSV."""
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    return pd.DataFrame()


def get_cache_timestamp(cache_file: str) -> datetime | None:
    """Get the timestamp of when cache was last updated."""
    if os.path.exists(cache_file):
        return datetime.fromtimestamp(os.path.getmtime(cache_file))
    return None


def is_cache_valid(cache_file: str, max_age_hours: int = 24) -> bool:
    """Check if cache file exists and is recent enough."""
    timestamp = get_cache_timestamp(cache_file)
    if timestamp is None:
        return False
    age = datetime.now() - timestamp
    return age.total_seconds() < (max_age_hours * 3600)


def normalize_team_name(name: str) -> str:
    """Normalize team names for consistent matching."""
    # Common abbreviations and variations
    name_mappings = {
        "lsu": "LSU",
        "louisiana state": "LSU",
        "ole miss": "Ole Miss",
        "mississippi": "Ole Miss",
        "nc state": "NC State",
        "north carolina state": "NC State",
        "unc": "North Carolina",
        "usc": "South Carolina",
        "osu": "Ohio State",
        "penn st": "Penn State",
        "penn state": "Penn State",
        "mich st": "Michigan State",
        "michigan st": "Michigan State",
        "fsu": "Florida State",
        "fla st": "Florida State",
        "va tech": "Virginia Tech",
        "vt": "Virginia Tech",
        "bc": "Boston College",
        "gt": "Georgia Tech",
        "texas a&m": "Texas A&M",
        "tamu": "Texas A&M",
        "byu": "BYU",
        "brigham young": "BYU",
        "ucf": "UCF",
        "central florida": "UCF",
        "tcu": "TCU",
        "texas christian": "TCU",
    }
    
    normalized = name.strip().lower()
    return name_mappings.get(normalized, name.title())


def format_era(era: float) -> str:
    """Format ERA for display."""
    if pd.isna(era):
        return "N/A"
    return f"{era:.2f}"


def format_ratio(ratio: float) -> str:
    """Format ratios for display."""
    if pd.isna(ratio):
        return "N/A"
    return f"{ratio:.2f}"


def format_percentage(pct: float) -> str:
    """Format percentages for display."""
    if pd.isna(pct):
        return "N/A"
    return f"{pct:.3f}"


def calculate_percentile(value: float, series: pd.Series, lower_is_better: bool = False) -> int:
    """Calculate percentile rank for a value within a series."""
    if pd.isna(value) or len(series.dropna()) == 0:
        return 50
    
    if lower_is_better:
        # For stats where lower is better (ERA, BB/9, etc.)
        percentile = (series.dropna() >= value).mean() * 100
    else:
        # For stats where higher is better (K/9, OBP, etc.)
        percentile = (series.dropna() <= value).mean() * 100
    
    return int(percentile)


def get_grade(percentile: int) -> str:
    """Convert percentile to letter grade."""
    if percentile >= 90:
        return "A+"
    elif percentile >= 80:
        return "A"
    elif percentile >= 70:
        return "B+"
    elif percentile >= 60:
        return "B"
    elif percentile >= 50:
        return "C+"
    elif percentile >= 40:
        return "C"
    elif percentile >= 30:
        return "D"
    else:
        return "F"

