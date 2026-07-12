from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_DIR / "outputs"

supply = pd.read_csv(OUT_DIR / "kpi_19_supply_demand_score_v2.csv", encoding="utf-8-sig")
power = pd.read_csv(OUT_DIR / "kpi_14_power_class_overall.csv", encoding="utf-8-sig")
operators = pd.read_csv(OUT_DIR / "kpi_13_operator_archetype_refined.csv", encoding="utf-8-sig")

insights = []

# Insight 1: AC vs HPC power imbalance
ac = power[power["power_class"] == "AC / Destination"].iloc[0]
hpc = power[power["power_class"] == "HPC / Ultra-fast"].iloc[0]

insights.append({
    "insight_area": "Power class",
    "finding": "AC chargers dominate by number of points, but HPC dominates installed power.",
    "evidence": f"AC/Destination = {ac['charging_point_share_pct']:.1f}% of points but {ac['installed_power_share_pct']:.1f}% of power. HPC = {hpc['charging_point_share_pct']:.1f}% of points but {hpc['installed_power_share_pct']:.1f}% of power.",
    "industry_meaning": "Charging infrastructure should not be judged only by charger count. Installed power gives a better view of real charging capacity."
})

# Insight 2: strongest relative supply
top_state = supply.iloc[0]
insights.append({
    "insight_area": "Supply vs BEV demand",
    "finding": f"{top_state['state']} shows the strongest relative charging supply in this analysis.",
    "evidence": f"{top_state['bevs_per_charging_point']:.1f} BEVs per charging point, {top_state['installed_kw_per_bev']:.2f} kW per BEV.",
    "industry_meaning": "Some smaller states may look stronger after adjusting charging supply by BEV stock."
})

# Insight 3: highest demand pressure
bottom_state = supply.iloc[-1]
insights.append({
    "insight_area": "Supply vs BEV demand",
    "finding": f"{bottom_state['state']} shows the highest relative demand pressure.",
    "evidence": f"{bottom_state['bevs_per_charging_point']:.1f} BEVs per charging point, {bottom_state['installed_kw_per_bev']:.2f} kW per BEV.",
    "industry_meaning": "Dense urban states may require more targeted charging expansion despite having existing infrastructure."
})

# Insight 4: operator strategy
top_operator = operators.iloc[0]
insights.append({
    "insight_area": "Operator strategy",
    "finding": f"{top_operator['operator_group']} has the highest power intensity profile.",
    "evidence": f"{top_operator['avg_kw_per_point']:.1f} kW per point and {top_operator['fast_point_share_pct']:.1f}% fast-charging share.",
    "industry_meaning": "Operators differ strongly: some focus on network scale, others on high-power charging."
})

insights_df = pd.DataFrame(insights)

insights_df.to_csv(
    OUT_DIR / "kpi_20_project_insight_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Project insight summary created.")