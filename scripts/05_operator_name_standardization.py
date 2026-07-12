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


# --------------------------------------------------
# Operator grouping
# --------------------------------------------------

def clean_operator_name(name):
    n = str(name).lower()

    if "tesla" in n:
        return "Tesla"

    if "ionity" in n:
        return "IONITY"

    if "enbw" in n:
        return "EnBW"

    if "ewe go" in n or "ewe" in n:
        return "EWE / EWE Go"

    if "e.on" in n or "eon" in n:
        return "E.ON Drive"

    if "allego" in n:
        return "Allego"

    if "aral" in n or "bp europa" in n:
        return "Aral / BP"

    if "shell" in n:
        return "Shell"

    if "mercedes" in n:
        return "Mercedes-Benz"

    if "volkswagen" in n or "vw" in n:
        return "Volkswagen"

    if "lidl" in n or "kaufland" in n:
        return "Lidl / Kaufland"

    if "aldi" in n:
        return "ALDI"

    if "bosch" in n:
        return "Bosch"

    if "pfalzwerke" in n:
        return "Pfalzwerke"

    if "westenergie" in n:
        return "Westenergie"

    if "maingau" in n:
        return "MAINGAU Energie"

    if "mainova" in n:
        return "Mainova"

    if "entega" in n:
        return "ENTEGA"

    if "enercity" in n:
        return "enercity"

    if "swm" in n or "stadtwerke münchen" in n:
        return "SWM / Stadtwerke München"

    if "n-ergie" in n or "n ergie" in n:
        return "N-ERGIE"

    if "rewag" in n:
        return "REWAG"

    if "team-emobility" in n or "team emobility" in n:
        return "Team-Emobility"

    if "deer" in n:
        return "deer"

    if "lew" in n:
        return "LEW"

    if "eswe" in n:
        return "ESWE"

    if "new niederrhein" in n:
        return "NEW Niederrhein Energie"

    if "tanke" in n:
        return "TankE"

    if "stadtwerke düsseldorf" in n:
        return "Stadtwerke Düsseldorf"

    if "stadtwerke stuttgart" in n:
        return "Stadtwerke Stuttgart"

    if "stadtwerke bielefeld" in n:
        return "Stadtwerke Bielefeld"

    if "mainzer stadtwerke" in n:
        return "Mainzer Stadtwerke"

    # If no rule matches, keep original name
    return name


df["operator_group"] = df["operator"].apply(clean_operator_name)


# --------------------------------------------------
# Operator KPIs after grouping
# --------------------------------------------------

operator_kpi = df.groupby("operator_group").agg(
    facilities=("charging_facility_id", "count"),
    charging_points=("charging_points", "sum"),
    normal_charging_points=("normal_charging_points", "sum"),
    fast_charging_points=("fast_charging_points", "sum"),
    installed_power_kw=("installed_power_kw", "sum")
).reset_index()

operator_kpi["installed_power_mw"] = operator_kpi["installed_power_kw"] / 1000
operator_kpi["avg_kw_per_point"] = operator_kpi["installed_power_kw"] / operator_kpi["charging_points"]
operator_kpi["fast_point_share_pct"] = (
    operator_kpi["fast_charging_points"] / operator_kpi["charging_points"]
) * 100

# Keep meaningful operators only
operator_kpi = operator_kpi[operator_kpi["charging_points"] >= 50].copy()

# Ranking
operator_kpi["power_rank"] = operator_kpi["installed_power_mw"].rank(
    ascending=False, method="dense"
)

operator_kpi["points_rank"] = operator_kpi["charging_points"].rank(
    ascending=False, method="dense"
)

operator_kpi["power_vs_points_rank_gap"] = (
    operator_kpi["points_rank"] - operator_kpi["power_rank"]
)


# --------------------------------------------------
# Strategy classification
# --------------------------------------------------

points_median = operator_kpi["charging_points"].median()
power_median = operator_kpi["avg_kw_per_point"].median()

def classify_operator(row):
    if row["charging_points"] >= points_median and row["avg_kw_per_point"] >= power_median:
        return "Scale + Power"
    elif row["charging_points"] >= points_median and row["avg_kw_per_point"] < power_median:
        return "Scale-focused"
    elif row["charging_points"] < points_median and row["avg_kw_per_point"] >= power_median:
        return "Power-focused"
    else:
        return "Small / local network"

operator_kpi["operator_strategy"] = operator_kpi.apply(classify_operator, axis=1)


# --------------------------------------------------
# Export
# --------------------------------------------------

operator_kpi.sort_values(
    "installed_power_mw",
    ascending=False
).to_csv(
    OUT_DIR / "kpi_10_operator_strategy_grouped.csv",
    index=False,
    encoding="utf-8-sig"
)

operator_kpi.sort_values(
    "power_vs_points_rank_gap",
    ascending=False
).head(30).to_csv(
    OUT_DIR / "kpi_11_power_outperformers.csv",
    index=False,
    encoding="utf-8-sig"
)

operator_kpi.sort_values(
    "avg_kw_per_point",
    ascending=False
).head(30).to_csv(
    OUT_DIR / "kpi_12_high_power_intensity_operators.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Grouped operator strategy files saved.")
print(f"Operator groups analyzed: {len(operator_kpi)}")