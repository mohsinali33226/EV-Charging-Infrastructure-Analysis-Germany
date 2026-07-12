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
df = df[df["commissioning_year"].notna()]

df["commissioning_year"] = df["commissioning_year"].astype(int)

# Keep realistic years
df = df[(df["commissioning_year"] >= 2015) & (df["commissioning_year"] <= 2026)]

# kW per charging point
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

# Year + power class summary
trend = df.groupby(["commissioning_year", "power_class"]).agg(
    facilities=("charging_facility_id", "count"),
    charging_points=("charging_points", "sum"),
    installed_power_kw=("installed_power_kw", "sum")
).reset_index()

trend["installed_power_mw"] = trend["installed_power_kw"] / 1000

# Add yearly total
year_total = trend.groupby("commissioning_year").agg(
    year_charging_points=("charging_points", "sum"),
    year_installed_power_kw=("installed_power_kw", "sum")
).reset_index()

trend = trend.merge(year_total, on="commissioning_year", how="left")

trend["charging_point_share_pct"] = (
    trend["charging_points"] / trend["year_charging_points"] * 100
)

trend["installed_power_share_pct"] = (
    trend["installed_power_kw"] / trend["year_installed_power_kw"] * 100
)

trend.to_csv(
    OUT_DIR / "kpi_21_yearly_power_class_trend.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Yearly power class trend saved.")