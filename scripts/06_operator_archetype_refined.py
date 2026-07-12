from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
IN_FILE = PROJECT_DIR / "outputs" / "kpi_10_operator_strategy_grouped.csv"
OUT_DIR = PROJECT_DIR / "outputs"

df = pd.read_csv(IN_FILE, encoding="utf-8-sig")

def classify_archetype(row):
    avg_kw = row["avg_kw_per_point"]
    fast_share = row["fast_point_share_pct"]
    points = row["charging_points"]

    if avg_kw >= 150 and fast_share >= 70:
        return "Ultra-fast / HPC network"

    elif avg_kw >= 50 and fast_share >= 40:
        return "Fast-charging focused"

    elif points >= 500 and fast_share < 10:
        return "Large AC destination network"

    elif avg_kw >= 30 and fast_share >= 15:
        return "Mixed charging network"

    elif points < 200 and avg_kw >= 30:
        return "Small high-power specialist"

    else:
        return "Local / AC-focused network"

df["operator_archetype"] = df.apply(classify_archetype, axis=1)

# Power intensity score
df["power_intensity_score"] = (
    0.6 * df["avg_kw_per_point"] +
    0.4 * df["fast_point_share_pct"]
)

df.sort_values(
    "power_intensity_score",
    ascending=False
).to_csv(
    OUT_DIR / "kpi_13_operator_archetype_refined.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Refined operator archetype file saved.")
