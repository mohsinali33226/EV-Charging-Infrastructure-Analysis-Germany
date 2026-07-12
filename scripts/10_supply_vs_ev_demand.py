from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent

CHARGING_FILE = PROJECT_DIR / "outputs" / "kpi_17_state_hpc_readiness.csv"
KBA_FILE = PROJECT_DIR / "data_raw" / "kba_bev_by_state.csv"
OUT_DIR = PROJECT_DIR / "outputs"

# Load files
charging = pd.read_csv(CHARGING_FILE, encoding="utf-8-sig")
kba = pd.read_csv(KBA_FILE, encoding="utf-8-sig")

# Clean KBA columns
kba["Bundesland"] = kba["Bundesland"].astype(str).str.strip()

# Keep latest reporting period
latest_period = kba["Berichtszeitpunkt"].max()
kba_latest = kba[kba["Berichtszeitpunkt"] == latest_period].copy()

# Keep useful KBA columns
kba_latest = kba_latest[
    [
        "Bundesland",
        "Berichtszeitpunkt",
        "Pkw BEV",
        "Pkw Elektro",
        "Pkw Plug In Hybrid"
    ]
].copy()

# Rename columns
kba_latest = kba_latest.rename(columns={
    "Bundesland": "state",
    "Berichtszeitpunkt": "reporting_period",
    "Pkw BEV": "bev_stock",
    "Pkw Elektro": "electric_vehicle_stock",
    "Pkw Plug In Hybrid": "plug_in_hybrid_stock"
})

# Merge charging + BEV stock
result = charging.merge(kba_latest, on="state", how="left")

# Demand-adjusted KPIs
result["bevs_per_charging_point"] = (
    result["bev_stock"] / result["total_charging_points"]
)

result["installed_kw_per_bev"] = (
    result["total_installed_power_kw"] / result["bev_stock"]
)

result["hpc_kw_per_bev"] = (
    result["hpc_installed_power_kw"] / result["bev_stock"]
)

# Classification
def classify_supply(row):
    if row["installed_kw_per_bev"] >= 3 and row["hpc_kw_per_bev"] >= 1.5:
        return "Strong supply relative to BEV stock"
    elif row["installed_kw_per_bev"] >= 2:
        return "Moderate supply relative to BEV stock"
    else:
        return "Higher demand pressure"

result["supply_demand_category"] = result.apply(classify_supply, axis=1)

# Sort by BEVs per charging point
result = result.sort_values("bevs_per_charging_point", ascending=False)

# Export
result.to_csv(
    OUT_DIR / "kpi_18_state_supply_vs_ev_demand.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Supply vs EV demand file saved.")
print("Latest KBA reporting period:", latest_period)