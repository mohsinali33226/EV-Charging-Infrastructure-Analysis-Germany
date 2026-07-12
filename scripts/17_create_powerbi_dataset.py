from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_DIR / "outputs"

files = {
    "State_Quality_Index": "kpi_07_state_quantity_vs_quality.csv",
    "State_HPC_Readiness": "kpi_17_state_hpc_readiness.csv",
    "Supply_vs_BEV_Demand": "kpi_19_supply_demand_score_v2.csv",
    "Power_Class_Overall": "kpi_14_power_class_overall.csv",
    "Rollout_Trend": "kpi_23_clean_rollout_trend.csv",
    "Operator_Archetypes": "kpi_13_operator_archetype_refined.csv",
    "Final_Insights": "kpi_24_final_project_insights.csv"
}

out_file = OUT_DIR / "EV_charging_final_powerbi_dataset.xlsx"

with pd.ExcelWriter(out_file, engine="openpyxl") as writer:
    for sheet_name, file_name in files.items():
        df = pd.read_csv(OUT_DIR / file_name, encoding="utf-8-sig")
        df.to_excel(writer, sheet_name=sheet_name, index=False)

print("Final Power BI dataset created:")
print(out_file)