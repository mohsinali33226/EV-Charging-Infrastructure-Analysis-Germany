from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
IN_FILE = PROJECT_DIR / "outputs" / "kpi_22_yearly_rollout_summary.csv"
OUT_DIR = PROJECT_DIR / "outputs"

df = pd.read_csv(IN_FILE, encoding="utf-8-sig")

# Rename only the columns we need
clean = pd.DataFrame()

clean["year"] = df["commissioning_year"]
clean["new_charging_points"] = df["total_new_charging_points"]
clean["new_installed_power_mw"] = df["total_new_installed_power_mw"]

clean["ac_point_share_pct"] = df.get("charging_point_share_pct_AC__Destination", 0)
clean["ac_power_share_pct"] = df.get("installed_power_share_pct_AC__Destination", 0)

clean["hpc_point_share_pct"] = df.get("charging_point_share_pct_HPC__Ultra_fast", 0)
clean["hpc_power_share_pct"] = df.get("installed_power_share_pct_HPC__Ultra_fast", 0)

clean["dc_fast_point_share_pct"] = df.get("charging_point_share_pct_DC_Fast", 0)
clean["dc_fast_power_share_pct"] = df.get("installed_power_share_pct_DC_Fast", 0)

# Do not use incomplete/latest year for main conclusion
clean["data_note"] = clean["year"].apply(
    lambda y: "Use carefully - recent/incomplete year" if y >= 2025 else "Usable for trend"
)

clean.to_csv(
    OUT_DIR / "kpi_23_clean_rollout_trend.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Clean rollout trend file saved.")