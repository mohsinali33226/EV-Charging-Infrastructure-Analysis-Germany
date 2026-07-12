from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = PROJECT_DIR / "outputs"

insights = pd.read_csv(
    OUT_DIR / "kpi_20_project_insight_summary.csv",
    encoding="utf-8-sig"
)

trend = pd.read_csv(
    OUT_DIR / "kpi_23_clean_rollout_trend.csv",
    encoding="utf-8-sig"
)

# Use only reliable trend years
trend_use = trend[(trend["year"] >= 2018) & (trend["year"] <= 2024)]

# Pick strongest recent HPC power year
best_hpc_year = trend_use.sort_values(
    "hpc_power_share_pct",
    ascending=False
).iloc[0]

new_insight = {
    "insight_area": "Rollout trend",
    "finding": "Recent charging rollout is becoming more power-capacity focused.",
    "evidence": (
        f"In {int(best_hpc_year['year'])}, HPC / Ultra-fast charging represented "
        f"{best_hpc_year['hpc_point_share_pct']:.1f}% of new charging points but "
        f"{best_hpc_year['hpc_power_share_pct']:.1f}% of newly installed power."
    ),
    "industry_meaning": (
        "New infrastructure should be assessed by installed power and charging speed, "
        "not only by the number of charging points."
    )
}

insights = pd.concat(
    [insights, pd.DataFrame([new_insight])],
    ignore_index=True
)

insights.to_csv(
    OUT_DIR / "kpi_24_final_project_insights.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Final project insights file created.")