from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
IN_FILE = PROJECT_DIR / "outputs" / "kpi_18_state_supply_vs_ev_demand.csv"
OUT_DIR = PROJECT_DIR / "outputs"

df = pd.read_csv(IN_FILE, encoding="utf-8-sig")

# Helper function: min-max score
def minmax_score(series, higher_is_better=True):
    min_val = series.min()
    max_val = series.max()

    if max_val == min_val:
        return 50

    score = (series - min_val) / (max_val - min_val) * 100

    if higher_is_better:
        return score
    else:
        return 100 - score

# Score components
df["bev_pressure_score"] = minmax_score(
    df["bevs_per_charging_point"],
    higher_is_better=False
)

df["installed_kw_per_bev_score"] = minmax_score(
    df["installed_kw_per_bev"],
    higher_is_better=True
)

df["hpc_kw_per_bev_score"] = minmax_score(
    df["hpc_kw_per_bev"],
    higher_is_better=True
)

# Final supply-demand adequacy score
df["supply_demand_score_v2"] = (
    0.30 * df["bev_pressure_score"] +
    0.40 * df["installed_kw_per_bev_score"] +
    0.30 * df["hpc_kw_per_bev_score"]
)

# Category based on relative score
def category(score):
    if score >= 70:
        return "Relatively strong supply"
    elif score >= 45:
        return "Moderate supply"
    elif score >= 25:
        return "Demand pressure"
    else:
        return "High demand pressure"

df["supply_demand_category_v2"] = df["supply_demand_score_v2"].apply(category)

# Sort from strongest to weakest
df = df.sort_values("supply_demand_score_v2", ascending=False)

df.to_csv(
    OUT_DIR / "kpi_19_supply_demand_score_v2.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Supply-demand score v2 saved.")