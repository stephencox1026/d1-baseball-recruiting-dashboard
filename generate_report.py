"""
Generate a simple text report of all compiled players
"""

import pandas as pd
import os

output_dir = "output"

print("="*80)
print("SENIOR UNDRAFTED PLAYERS - POWER 4 CONFERENCES")
print("="*80)

conferences = ['SEC', 'ACC', 'Big Ten', 'Big 12']
positions = ['Starters', 'Relievers', 'PositionPlayers']

for conf in conferences:
    print(f"\n{'='*80}")
    print(f"{conf} CONFERENCE")
    print(f"{'='*80}")
    
    for pos in positions:
        filename = f"{output_dir}/{conf}_{pos}.csv"
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            if len(df) > 0:
                pos_name = pos.replace('PositionPlayers', 'Position Players')
                print(f"\n{pos_name} ({len(df)}):")
                print("-" * 80)
                for idx, row in df.iterrows():
                    if pos == 'PositionPlayers':
                        print(f"  {row['name']:30} | {row['team']:20} | {row['position']:5} | BA: {row['BA']:.3f}")
                    else:
                        print(f"  {row['name']:30} | {row['team']:20} | ERA: {row['ERA']:.2f} | IP: {row['IP']:.1f}")

# Summary
print(f"\n{'='*80}")
print("SUMMARY")
print(f"{'='*80}")

all_starters = pd.read_csv(f"{output_dir}/All_Starters.csv") if os.path.exists(f"{output_dir}/All_Starters.csv") else pd.DataFrame()
all_relievers = pd.read_csv(f"{output_dir}/All_Relievers.csv") if os.path.exists(f"{output_dir}/All_Relievers.csv") else pd.DataFrame()
all_hitters = pd.read_csv(f"{output_dir}/All_PositionPlayers.csv") if os.path.exists(f"{output_dir}/All_PositionPlayers.csv") else pd.DataFrame()

print(f"\nTotal Starting Pitchers: {len(all_starters)}")
print(f"Total Relief Pitchers: {len(all_relievers)}")
print(f"Total Position Players: {len(all_hitters)}")
print(f"\nGrand Total: {len(all_starters) + len(all_relievers) + len(all_hitters)} players")

# By conference summary
print(f"\nBy Conference:")
for conf in conferences:
    conf_starters = len(all_starters[all_starters['conference'] == conf]) if 'conference' in all_starters.columns else 0
    conf_relievers = len(all_relievers[all_relievers['conference'] == conf]) if 'conference' in all_relievers.columns else 0
    conf_hitters = len(all_hitters[all_hitters['conference'] == conf]) if 'conference' in all_hitters.columns else 0
    total = conf_starters + conf_relievers + conf_hitters
    print(f"  {conf:12}: {conf_starters} SP, {conf_relievers} RP, {conf_hitters} H = {total} total")

