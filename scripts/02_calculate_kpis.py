from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
IN_FILE = PROJECT_DIR / "data_clean" / "ladesaeulen_clean_for_analysis.csv"
OUT_DIR = PROJECT_DIR / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load cleaned data
df = pd.read_csv(IN_FILE, encoding="utf-8-sig")

# --------------------------------------------------
# Basic data filtering
# --------------------------------------------------

# Keep only valid charging rows
df = df[df["charging_points"].notna()]
df = df[df["charging_points"] > 0]

# Clean important text fields
for col in ["state", "area_type", "operator"]:
    if col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace(["", "nan", "None", "NaN"], np.nan)

# Remove rows without valid federal state
df = df[df["state"].notna()]

# --------------------------------------------------
# KPI functions
# --------------------------------------------------

def safe_divide(a, b):
    return np.where(b == 0, 0, a / b)

def add_kpi_fields(kpi):
    kpi = kpi.copy()

    kpi["avg_kw_per_point"] = safe_divide(
        kpi["installed_power_kw"],
        kpi["charging_points"]
    )

    kpi["fast_point_share_pct"] = safe_divide(
        kpi["fast_charging_points"],
        kpi["charging_points"]
    ) * 100

    kpi["normal_point_share_pct"] = safe_divide(
        kpi["normal_charging_points"],
        kpi["charging_points"]
    ) * 100

    kpi["installed_power_mw"] = kpi["installed_power_kw"] / 1000

    return kpi

def make_kpis(frame, group_cols=None):
    if group_cols is None:
        kpi = frame.agg({
            "charging_facility_id": "count",
            "charging_points": "sum",
            "normal_charging_points": "sum",
            "fast_charging_points": "sum",
            "installed_power_kw": "sum",
        }).to_frame().T.rename(columns={"charging_facility_id": "facilities"})

    else:
        kpi = frame.groupby(group_cols, dropna=True).agg(
            facilities=("charging_facility_id", "count"),
            charging_points=("charging_points", "sum"),
            normal_charging_points=("normal_charging_points", "sum"),
            fast_charging_points=("fast_charging_points", "sum"),
            installed_power_kw=("installed_power_kw", "sum"),
        ).reset_index()

    return add_kpi_fields(kpi)

# --------------------------------------------------
# Export KPI files
# --------------------------------------------------

make_kpis(df).to_csv(
    OUT_DIR / "kpi_00_overview.csv",
    index=False,
    encoding="utf-8-sig"
)

make_kpis(df, ["state"]).sort_values(
    "charging_points",
    ascending=False
).to_csv(
    OUT_DIR / "kpi_01_by_state.csv",
    index=False,
    encoding="utf-8-sig"
)

make_kpis(df, ["area_type"]).sort_values(
    "charging_points",
    ascending=False
).to_csv(
    OUT_DIR / "kpi_02_by_area_type.csv",
    index=False,
    encoding="utf-8-sig"
)

make_kpis(
    df.dropna(subset=["commissioning_year"]),
    ["commissioning_year"]
).sort_values(
    "commissioning_year"
).to_csv(
    OUT_DIR / "kpi_03_by_commissioning_year.csv",
    index=False,
    encoding="utf-8-sig"
)

make_kpis(df, ["operator"]).sort_values(
    "installed_power_kw",
    ascending=False
).head(50).to_csv(
    OUT_DIR / "kpi_04_top_operators_by_power.csv",
    index=False,
    encoding="utf-8-sig"
)

# --------------------------------------------------
# First draft infrastructure quality score
# --------------------------------------------------

score = make_kpis(df, ["state"])

score_columns = [
    "charging_points",
    "installed_power_kw",
    "avg_kw_per_point",
    "fast_point_share_pct"
]

for col in score_columns:
    mn = score[col].min()
    mx = score[col].max()

    if mx == mn:
        score[col + "_score"] = 0
    else:
        score[col + "_score"] = ((score[col] - mn) / (mx - mn)) * 100

score["infrastructure_quality_score"] = (
    0.25 * score["charging_points_score"] +
    0.35 * score["installed_power_kw_score"] +
    0.25 * score["avg_kw_per_point_score"] +
    0.15 * score["fast_point_share_pct_score"]
)

score.sort_values(
    "infrastructure_quality_score",
    ascending=False
).to_csv(
    OUT_DIR / "kpi_05_state_quality_score_first_draft.csv",
    index=False,
    encoding="utf-8-sig"
)

print("KPI files saved in outputs folder.")
print(f"Rows used: {len(df):,}")
print(f"Total charging points: {df['charging_points'].sum():,.0f}")
print(f"Total installed power MW: {df['installed_power_kw'].sum() / 1000:,.1f}")