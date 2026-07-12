from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
IN_FILE = PROJECT_DIR / "data_clean" / "ladesaeulen_clean_for_analysis.csv"
OUT_DIR = PROJECT_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --------------------------------------------------
# Load and filter data
# --------------------------------------------------

df = pd.read_csv(IN_FILE, encoding="utf-8-sig")

for col in ["state", "area_type", "operator"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["", "nan", "None", "NaN"], np.nan)

# valid rows only
df = df[df["state"].notna()]
df = df[df["charging_points"].notna()]
df = df[df["charging_points"] > 0]
df = df[df["installed_power_kw"].notna()]
df = df[df["installed_power_kw"] >= 0]

# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def safe_divide(a, b):
    return np.where(b == 0, 0, a / b)


def minmax_score(series):
    mn = series.min()
    mx = series.max()
    if mx == mn:
        return pd.Series(0, index=series.index)
    return ((series - mn) / (mx - mn)) * 100

# --------------------------------------------------
# State level KPIs
# --------------------------------------------------

state = df.groupby("state").agg(
    facilities=("charging_facility_id", "count"),
    charging_points=("charging_points", "sum"),
    normal_charging_points=("normal_charging_points", "sum"),
    fast_charging_points=("fast_charging_points", "sum"),
    installed_power_kw=("installed_power_kw", "sum"),
).reset_index()

state["installed_power_mw"] = state["installed_power_kw"] / 1000
state["avg_kw_per_point"] = safe_divide(state["installed_power_kw"], state["charging_points"])
state["fast_point_share_pct"] = safe_divide(state["fast_charging_points"], state["charging_points"]) * 100
state["normal_point_share_pct"] = safe_divide(state["normal_charging_points"], state["charging_points"]) * 100

# share-based comparison: power share vs charging point share
state["charging_point_share_pct"] = state["charging_points"] / state["charging_points"].sum() * 100
state["installed_power_share_pct"] = state["installed_power_kw"] / state["installed_power_kw"].sum() * 100
state["power_premium_pct_points"] = state["installed_power_share_pct"] - state["charging_point_share_pct"]

# recent rollout: how much of today's installed power was commissioned from 2024 onwards
recent = df[df["commissioning_year"] >= 2024].groupby("state").agg(
    recent_charging_points=("charging_points", "sum"),
    recent_installed_power_kw=("installed_power_kw", "sum"),
).reset_index()

state = state.merge(recent, on="state", how="left")
state[["recent_charging_points", "recent_installed_power_kw"]] = state[["recent_charging_points", "recent_installed_power_kw"]].fillna(0)
state["recent_power_share_pct"] = safe_divide(state["recent_installed_power_kw"], state["installed_power_kw"]) * 100

# --------------------------------------------------
# Quality Index v2 - not a size score
# --------------------------------------------------
# This score measures power-intensity and fast-charging readiness.
# It does NOT measure population coverage or EV demand yet.

state["avg_kw_score"] = minmax_score(state["avg_kw_per_point"])
state["fast_share_score"] = minmax_score(state["fast_point_share_pct"])
state["power_premium_score"] = minmax_score(state["power_premium_pct_points"])
state["recent_rollout_score"] = minmax_score(state["recent_power_share_pct"])

state["quality_index_v2"] = (
    0.35 * state["avg_kw_score"] +
    0.25 * state["fast_share_score"] +
    0.25 * state["power_premium_score"] +
    0.15 * state["recent_rollout_score"]
)

# --------------------------------------------------
# Strategy quadrant
# --------------------------------------------------

quantity_median = state["charging_points"].median()
quality_median = state["quality_index_v2"].median()

conditions = [
    (state["charging_points"] >= quantity_median) & (state["quality_index_v2"] >= quality_median),
    (state["charging_points"] >= quantity_median) & (state["quality_index_v2"] < quality_median),
    (state["charging_points"] < quantity_median) & (state["quality_index_v2"] >= quality_median),
    (state["charging_points"] < quantity_median) & (state["quality_index_v2"] < quality_median),
]

labels = [
    "Balanced leader: high quantity + high power quality",
    "Quantity-heavy: many points but lower power quality",
    "Power-focused: fewer points but stronger fast-charging quality",
    "Improvement area: lower quantity + lower power quality",
]

state["strategy_quadrant"] = np.select(conditions, labels, default="Unclassified")

# --------------------------------------------------
# Export
# --------------------------------------------------

final_cols = [
    "state",
    "facilities",
    "charging_points",
    "normal_charging_points",
    "fast_charging_points",
    "installed_power_kw",
    "installed_power_mw",
    "avg_kw_per_point",
    "fast_point_share_pct",
    "normal_point_share_pct",
    "charging_point_share_pct",
    "installed_power_share_pct",
    "power_premium_pct_points",
    "recent_charging_points",
    "recent_installed_power_kw",
    "recent_power_share_pct",
    "quality_index_v2",
    "strategy_quadrant",
]

state[final_cols].sort_values("quality_index_v2", ascending=False).to_csv(
    OUT_DIR / "kpi_06_state_quality_index_v2.csv",
    index=False,
    encoding="utf-8-sig"
)

state[final_cols].sort_values("charging_points", ascending=False).to_csv(
    OUT_DIR / "kpi_07_state_quantity_vs_quality.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Quality Index v2 files saved:")
print("- outputs/kpi_06_state_quality_index_v2.csv")
print("- outputs/kpi_07_state_quantity_vs_quality.csv")
