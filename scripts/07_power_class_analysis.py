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
df = df[df["installed_power_kw"].notna()]
df = df[df["installed_power_kw"] > 0]

# Average power per charging point at facility level
df["kw_per_point_facility"] = df["installed_power_kw"] / df["charging_points"]

# Power class
def classify_power_class(kw):
    if kw <= 22:
        return "AC / Destination"
    elif kw <= 49:
        return "Urban fast"
    elif kw < 150:
        return "DC Fast"
    else:
        return "HPC / Ultra-fast"

df["power_class"] = df["kw_per_point_facility"].apply(classify_power_class)

# Overall power class summary
overall = df.groupby("power_class").agg(
    facilities=("charging_facility_id", "count"),
    charging_points=("charging_points", "sum"),
    installed_power_kw=("installed_power_kw", "sum")
).reset_index()

overall["installed_power_mw"] = overall["installed_power_kw"] / 1000
overall["charging_point_share_pct"] = overall["charging_points"] / overall["charging_points"].sum() * 100
overall["installed_power_share_pct"] = overall["installed_power_kw"] / overall["installed_power_kw"].sum() * 100

overall.to_csv(
    OUT_DIR / "kpi_14_power_class_overall.csv",
    index=False,
    encoding="utf-8-sig"
)

# Power class by state
state_power = df.groupby(["state", "power_class"]).agg(
    facilities=("charging_facility_id", "count"),
    charging_points=("charging_points", "sum"),
    installed_power_kw=("installed_power_kw", "sum")
).reset_index()

state_power["installed_power_mw"] = state_power["installed_power_kw"] / 1000

state_power.to_csv(
    OUT_DIR / "kpi_15_power_class_by_state.csv",
    index=False,
    encoding="utf-8-sig"
)

# Power class by operator
operator_power = df.groupby(["operator", "power_class"]).agg(
    facilities=("charging_facility_id", "count"),
    charging_points=("charging_points", "sum"),
    installed_power_kw=("installed_power_kw", "sum")
).reset_index()

operator_power["installed_power_mw"] = operator_power["installed_power_kw"] / 1000

operator_power.sort_values(
    "installed_power_kw",
    ascending=False
).to_csv(
    OUT_DIR / "kpi_16_power_class_by_operator.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Power class analysis files saved.")