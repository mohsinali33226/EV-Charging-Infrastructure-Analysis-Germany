from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
IN_FILE = PROJECT_DIR / "data_clean" / "ladesaeulen_clean_for_analysis.csv"
OUT_DIR = PROJECT_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(IN_FILE, encoding="utf-8-sig")

# Basic cleaning
df = df[df["charging_points"].notna()]
df = df[df["charging_points"] > 0]
df = df[df["operator"].notna()]
df["operator"] = df["operator"].astype(str).str.strip()

# Operator-level KPIs
operator_kpi = df.groupby("operator").agg(
    facilities=("charging_facility_id", "count"),
    charging_points=("charging_points", "sum"),
    normal_charging_points=("normal_charging_points", "sum"),
    fast_charging_points=("fast_charging_points", "sum"),
    installed_power_kw=("installed_power_kw", "sum")
).reset_index()

# Derived KPIs
operator_kpi["installed_power_mw"] = operator_kpi["installed_power_kw"] / 1000
operator_kpi["avg_kw_per_point"] = operator_kpi["installed_power_kw"] / operator_kpi["charging_points"]
operator_kpi["fast_point_share_pct"] = (
    operator_kpi["fast_charging_points"] / operator_kpi["charging_points"]
) * 100

# Keep only meaningful operators
operator_kpi = operator_kpi[operator_kpi["charging_points"] >= 50]

# Operator strategy classification
def classify_operator(row):
    if row["charging_points"] >= operator_kpi["charging_points"].median() and row["avg_kw_per_point"] >= operator_kpi["avg_kw_per_point"].median():
        return "Scale + Power"
    elif row["charging_points"] >= operator_kpi["charging_points"].median() and row["avg_kw_per_point"] < operator_kpi["avg_kw_per_point"].median():
        return "Scale-focused"
    elif row["charging_points"] < operator_kpi["charging_points"].median() and row["avg_kw_per_point"] >= operator_kpi["avg_kw_per_point"].median():
        return "Power-focused"
    else:
        return "Small / local network"

operator_kpi["operator_strategy"] = operator_kpi.apply(classify_operator, axis=1)

# Rank operators
operator_kpi["power_rank"] = operator_kpi["installed_power_mw"].rank(ascending=False, method="dense")
operator_kpi["points_rank"] = operator_kpi["charging_points"].rank(ascending=False, method="dense")

# Export files
operator_kpi.sort_values(
    "installed_power_mw",
    ascending=False
).to_csv(
    OUT_DIR / "kpi_08_operator_strategy_analysis.csv",
    index=False,
    encoding="utf-8-sig"
)

operator_kpi.sort_values(
    "avg_kw_per_point",
    ascending=False
).head(30).to_csv(
    OUT_DIR / "kpi_09_top_power_focused_operators.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Operator strategy files saved.")
print(f"Operators analyzed: {len(operator_kpi)}")