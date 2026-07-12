from pathlib import Path
import pandas as pd

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
df = df[df["state"].notna()]
df["state"] = df["state"].astype(str).str.strip()

# Average power per point at facility level
df["kw_per_point_facility"] = df["installed_power_kw"] / df["charging_points"]

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

# Total state summary
state_total = df.groupby("state").agg(
    total_facilities=("charging_facility_id", "count"),
    total_charging_points=("charging_points", "sum"),
    total_installed_power_kw=("installed_power_kw", "sum")
).reset_index()

# HPC-only summary
hpc = df[df["power_class"] == "HPC / Ultra-fast"].groupby("state").agg(
    hpc_facilities=("charging_facility_id", "count"),
    hpc_charging_points=("charging_points", "sum"),
    hpc_installed_power_kw=("installed_power_kw", "sum")
).reset_index()

# Merge
result = state_total.merge(hpc, on="state", how="left").fillna(0)

result["total_installed_power_mw"] = result["total_installed_power_kw"] / 1000
result["hpc_installed_power_mw"] = result["hpc_installed_power_kw"] / 1000

result["hpc_point_share_pct"] = (
    result["hpc_charging_points"] / result["total_charging_points"] * 100
)

result["hpc_power_share_pct"] = (
    result["hpc_installed_power_kw"] / result["total_installed_power_kw"] * 100
)

result["hpc_power_premium"] = (
    result["hpc_power_share_pct"] - result["hpc_point_share_pct"]
)

# Readiness category
def readiness(row):
    if row["hpc_power_share_pct"] >= 60 and row["hpc_point_share_pct"] >= 10:
        return "HPC-heavy infrastructure"
    elif row["hpc_power_share_pct"] >= 50:
        return "Power capacity driven by HPC"
    elif row["hpc_power_share_pct"] >= 35:
        return "Moderate HPC role"
    else:
        return "AC / lower-power dominated"

result["hpc_readiness_category"] = result.apply(readiness, axis=1)

result.sort_values(
    "hpc_power_share_pct",
    ascending=False
).to_csv(
    OUT_DIR / "kpi_17_state_hpc_readiness.csv",
    index=False,
    encoding="utf-8-sig"
)

print("State HPC readiness file saved.")