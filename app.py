"""
D1 Baseball Recruitment Dashboard

Interactive Streamlit dashboard for scouting Division 1 college baseball players
from Power 4 conferences who have not been drafted in the MLB Draft.
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    POWER_4_CONFERENCES,
    CURRENT_SEASON,
    NUM_STARTING_PITCHERS,
    NUM_RELIEF_PITCHERS,
    NUM_HITTERS,
    STARTING_PITCHER_WEIGHTS,
    RELIEF_PITCHER_WEIGHTS,
    HITTER_WEIGHTS
)
from src.roster_based_collection import collect_roster_player_stats
from src.metrics import MetricsCalculator
from src.ranking import PlayerRanker
from src.explanations import ExplanationGenerator
from config import STARTER_IP_PER_APP_THRESHOLD

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="D1 Baseball Recruitment",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# DATA LOADING (with caching)
# =============================================================================

@st.cache_data(ttl=3600)
def load_and_process_data():
    """Load roster players, fetch their stats, and rank them."""
    # Collect stats for roster players
    pitching_df, batting_df = collect_roster_player_stats()
    
    if pitching_df.empty and batting_df.empty:
        raise ValueError("No player data found. Please ensure roster file exists and stats can be fetched.")
    
    # Separate starters and relievers
    metrics_calc = MetricsCalculator()
    ranker = PlayerRanker()
    
    starters = pd.DataFrame()
    relievers = pd.DataFrame()
    hitters = pd.DataFrame()
    
    if not pitching_df.empty:
        # Classify starters vs relievers
        pitching_df['is_starter'] = (
            pitching_df['ip_per_app'] >= STARTER_IP_PER_APP_THRESHOLD
        ) | (
            pitching_df['ip_per_app'].isna() & 
            (pitching_df['ip'].fillna(0) >= 40)
        )
        
        starters_df = pitching_df[pitching_df['is_starter']].copy()
        relievers_df = pitching_df[~pitching_df['is_starter']].copy()
        
        # Rank them
        if not starters_df.empty:
            starters = ranker.rank_starting_pitchers(starters_df).head(NUM_STARTING_PITCHERS)
        if not relievers_df.empty:
            relievers = ranker.rank_relief_pitchers(relievers_df).head(NUM_RELIEF_PITCHERS)
    
    if not batting_df.empty:
        # Rank hitters
        hitters = ranker.rank_hitters(batting_df).head(NUM_HITTERS)
    
    return starters, relievers, hitters

# =============================================================================
# SIDEBAR
# =============================================================================

with st.sidebar:
    st.title("⚾ D1 Recruitment")
    st.markdown("---")
    
    st.subheader("Filters")
    
    # Conference filter
    selected_conferences = st.multiselect(
        "Conferences",
        options=list(POWER_4_CONFERENCES.keys()),
        default=list(POWER_4_CONFERENCES.keys())
    )
    
    # Tier filter
    selected_tiers = st.multiselect(
        "Tiers",
        options=['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5'],
        default=['Tier 1', 'Tier 2', 'Tier 3', 'Tier 4', 'Tier 5']
    )
    
    st.markdown("---")
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Weights information
    with st.expander("📐 Ranking Weights"):
        st.markdown("**Starting Pitchers:**")
        for stat, weight in STARTING_PITCHER_WEIGHTS.items():
            st.markdown(f"- {stat}: {int(weight*100)}%")
        
        st.markdown("**Relief Pitchers:**")
        for stat, weight in RELIEF_PITCHER_WEIGHTS.items():
            st.markdown(f"- {stat}: {int(weight*100)}%")
        
        st.markdown("**Hitters:**")
        for stat, weight in HITTER_WEIGHTS.items():
            st.markdown(f"- {stat}: {int(weight*100)}%")

# =============================================================================
# MAIN CONTENT
# =============================================================================

# Header
st.title("🏟️ D1 Baseball Recruitment Dashboard")
st.markdown(f"**Power 4 Conferences | {CURRENT_SEASON} Season | Undrafted Players Only**")
st.markdown("---")

# Load data
with st.spinner("Loading player data from NCAA.com..."):
    try:
        top_starters, top_relievers, top_hitters = load_and_process_data()
        explanation_gen = ExplanationGenerator()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Apply filters
def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Apply sidebar filters to dataframe."""
    filtered = df.copy()
    
    if selected_conferences and 'conference' in filtered.columns:
        filtered = filtered[filtered['conference'].isin(selected_conferences)]
    
    if selected_tiers and 'tier' in filtered.columns:
        filtered = filtered[filtered['tier'].isin(selected_tiers)]
    
    return filtered

filtered_starters = apply_filters(top_starters)
filtered_relievers = apply_filters(top_relievers)
filtered_hitters = apply_filters(top_hitters)

# Summary metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Starting Pitchers", len(filtered_starters))

with col2:
    st.metric("Relief Pitchers", len(filtered_relievers))

with col3:
    st.metric("Hitters", len(filtered_hitters))

with col4:
    total = len(filtered_starters) + len(filtered_relievers) + len(filtered_hitters)
    st.metric("Total Prospects", total)


# Tabs for each category
tab1, tab2, tab3 = st.tabs(["🎯 Starting Pitchers", "🔥 Relief Pitchers", "💪 Hitters"])

# =============================================================================
# STARTING PITCHERS TAB
# =============================================================================

with tab1:
    st.header("Top Starting Pitchers")
    st.markdown("""
    **Ranking Criteria:** Strike Rate (BB/9) 50% → ERA 30% → K/9 (velocity proxy) 20%
    
    *Control is most important for starters - we want strike throwers who can go deep into games.*
    *Note: WHIP excluded - hits allowed not available on NCAA.com*
    """)
    
    if len(filtered_starters) == 0:
        st.warning("No starting pitchers match the current filters.")
    else:
        for idx, (_, row) in enumerate(filtered_starters.iterrows()):
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.markdown(f"### #{idx + 1}")
                    if 'tier' in row and pd.notna(row['tier']):
                        st.caption(f"**{row['tier']}**")
                
                with col2:
                    st.markdown(f"### {row['name']}")
                    st.markdown(f"**{row['team']}** | {row.get('conference', 'N/A')} | {row.get('class_year', 'N/A')}")
                    
                    # Stats in columns
                    stat_cols = st.columns(5)
                    with stat_cols[0]:
                        st.metric("ERA", f"{row['era']:.2f}")
                    with stat_cols[1]:
                        st.metric("K/9", f"{row['k_per_9']:.1f}")
                    with stat_cols[2]:
                        st.metric("BB/9", f"{row['bb_per_9']:.2f}")
                    with stat_cols[3]:
                        st.metric("IP", f"{row['ip']:.1f}")
                    with stat_cols[4]:
                        st.metric("K", f"{int(row['strikeouts'])}")
                    
                    # Score bar
                    score = row.get('composite_score', 50)
                    st.progress(score / 100, text=f"Composite Score: {score:.1f}")
                    
                    # Explanation
                    explanation = explanation_gen.generate_starter_explanation(row)
                    st.info(explanation)
                
                st.markdown("---")

# =============================================================================
# RELIEF PITCHERS TAB
# =============================================================================

with tab2:
    st.header("Top Relief Pitchers")
    st.markdown("""
    **Ranking Criteria:** K/9 (stuff/velocity) 50% → ERA 35% → IP/App 15%
    
    *For relievers, we want power arms who can dominate in short stints - strikeout rate indicates swing-and-miss stuff.*
    *Note: WHIP excluded - hits allowed not available on NCAA.com*
    """)
    
    if len(filtered_relievers) == 0:
        st.warning("No relief pitchers match the current filters.")
    else:
        for idx, (_, row) in enumerate(filtered_relievers.iterrows()):
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.markdown(f"### #{idx + 1}")
                    if 'tier' in row and pd.notna(row['tier']):
                        st.caption(f"**{row['tier']}**")
                
                with col2:
                    st.markdown(f"### {row['name']}")
                    st.markdown(f"**{row['team']}** | {row.get('conference', 'N/A')} | {row.get('class_year', 'N/A')}")
                    
                    # Stats in columns
                    stat_cols = st.columns(5)
                    with stat_cols[0]:
                        st.metric("ERA", f"{row['era']:.2f}")
                    with stat_cols[1]:
                        st.metric("K/9", f"{row['k_per_9']:.1f}")
                    with stat_cols[2]:
                        st.metric("BB/9", f"{row['bb_per_9']:.2f}")
                    with stat_cols[3]:
                        st.metric("IP", f"{row['ip']:.1f}")
                    with stat_cols[4]:
                        saves = row.get('saves', 0)
                        st.metric("SV", f"{int(saves)}")
                    
                    # Score bar
                    score = row.get('composite_score', 50)
                    st.progress(score / 100, text=f"Composite Score: {score:.1f}")
                    
                    # Explanation
                    explanation = explanation_gen.generate_reliever_explanation(row)
                    st.info(explanation)
                
                st.markdown("---")

# =============================================================================
# HITTERS TAB
# =============================================================================

with tab3:
    st.header("Top Hitters")
    st.markdown("""
    **Ranking Criteria:** K:BB Ratio 35% → wRC+ 20% → wOBA 15% → OBP 15% → SLG 10% → OPS 5%
    
    *Plate discipline (K:BB ratio) is most important - we want hitters who control the strike zone.*
    """)
    
    if len(filtered_hitters) == 0:
        st.warning("No hitters match the current filters.")
    else:
        for idx, (_, row) in enumerate(filtered_hitters.iterrows()):
            with st.container():
                col1, col2 = st.columns([1, 4])
                
                with col1:
                    st.markdown(f"### #{idx + 1}")
                    if 'tier' in row and pd.notna(row['tier']):
                        st.caption(f"**{row['tier']}**")
                
                with col2:
                    st.markdown(f"### {row['name']}")
                    pos = row.get('position', 'N/A')
                    st.markdown(f"**{row['team']}** | {row.get('conference', 'N/A')} | {pos} | {row.get('class_year', 'N/A')}")
                    
                    # Stats in columns
                    stat_cols = st.columns(6)
                    with stat_cols[0]:
                        st.metric("K:BB", f"{row['k_bb_ratio']:.2f}")
                    with stat_cols[1]:
                        st.metric("OBP", f"{row['obp']:.3f}")
                    with stat_cols[2]:
                        st.metric("SLG", f"{row['slg']:.3f}")
                    with stat_cols[3]:
                        st.metric("OPS", f"{row['ops']:.3f}")
                    with stat_cols[4]:
                        st.metric("wRC+", f"{int(row['wrc_plus'])}")
                    with stat_cols[5]:
                        st.metric("wOBA", f"{row['woba']:.3f}")
                    
                    # Score bar
                    score = row.get('composite_score', 50)
                    st.progress(score / 100, text=f"Composite Score: {score:.1f}")
                    
                    # Explanation
                    explanation = explanation_gen.generate_hitter_explanation(row)
                    st.info(explanation)
                
                st.markdown("---")

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
**D1 Baseball Recruitment Dashboard** | Power 4 Conferences (SEC, ACC, Big Ten, Big 12) | Data from NCAA.com

*Players who have been drafted in the MLB Draft are automatically excluded.*
""")
