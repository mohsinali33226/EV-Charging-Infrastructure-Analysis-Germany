from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
IN_FILE = PROJECT_DIR / "outputs" / "kpi_21_yearly_power_class_trend.csv"
OUT_DIR = PROJECT_DIR / "outputs"

df = pd.read_csv(IN_FILE, encoding="utf-8-sig")

# Pivot power class shares into columns
summary = df.pivot_table(
    index="commissioning_year",
    columns="power_class",
    values=[
        "charging_point_share_pct",
        "installed_power_share_pct",
        "charging_points",
        "installed_power_mw"
    ],
    aggfunc="sum",
    fill_value=0
)

# Flatten column names
summary.columns = [
    f"{metric}_{power_class}".replace(" ", "_").replace("/", "").replace("-", "_")
    for metric, power_class in summary.columns
]

summary = summary.reset_index()

# Add total yearly values
year_total = df.groupby("commissioning_year").agg(
    total_new_charging_points=("charging_points", "sum"),
    total_new_installed_power_mw=("installed_power_mw", "sum")
).reset_index()

summary = summary.merge(year_total, on="commissioning_year", how="left")

# Export
summary.to_csv(
    OUT_DIR / "kpi_22_yearly_rollout_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Yearly rollout summary saved.")