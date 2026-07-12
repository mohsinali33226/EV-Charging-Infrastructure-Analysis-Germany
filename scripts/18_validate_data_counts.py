from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent

clean_file = PROJECT_DIR / "data_clean" / "ladesaeulen_clean_for_analysis.csv"
power_file = PROJECT_DIR / "outputs" / "kpi_14_power_class_overall.csv"
state_file = PROJECT_DIR / "outputs" / "kpi_07_state_quantity_vs_quality.csv"

clean = pd.read_csv(clean_file, encoding="utf-8-sig")
power = pd.read_csv(power_file, encoding="utf-8-sig")
state = pd.read_csv(state_file, encoding="utf-8-sig")

print("Clean data rows:", len(clean))
print("Clean data charging points:", clean["charging_points"].sum())
print("Clean data installed power MW:", clean["installed_power_kw"].sum() / 1000)

print("\nPower class charging points:", power["charging_points"].sum())
print("Power class installed power MW:", power["installed_power_kw"].sum() / 1000)

print("\nState charging points:", state["charging_points"].sum())
print("State installed power MW:", state["installed_power_kw"].sum() / 1000)