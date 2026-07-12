from pathlib import Path
import pandas as pd
import numpy as np

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = PROJECT_DIR / "data_raw" / "Ladesaeulenregister_BNetzA_2026-07-07.xlsx"
OUT_DIR = PROJECT_DIR / "data_clean"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_FILE = OUT_DIR / "ladesaeulen_clean_for_analysis.csv"

# --------------------------------------------------
# Load Excel and detect header row automatically
# --------------------------------------------------

raw = pd.read_excel(RAW_FILE, header=None)

header_row = None

for i in range(min(30, len(raw))):
    row_text = " ".join(map(str, raw.iloc[i].tolist()))
    if "Betreiber" in row_text and "Anzahl Ladepunkte" in row_text:
        header_row = i
        break

if header_row is None:
    raise ValueError("Header row not found. Check the Excel file format.")

df = pd.read_excel(RAW_FILE, header=header_row)

# Clean column names
df.columns = df.columns.astype(str).str.strip()

# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def find_col(possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    raise ValueError(f"Column not found. Tried: {possible_names}")

def to_number(series):
    return (
        series.astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
        .replace(["nan", "None", ""], np.nan)
        .astype(float)
    )

# --------------------------------------------------
# Column mapping
# --------------------------------------------------

operator_col = find_col(["Betreiber"])
status_col = find_col(["Status"])
type_col = find_col(["Art der Ladeeinrichtung"])
points_col = find_col(["Anzahl Ladepunkte"])
power_col = find_col(["Nennleistung Ladeeinrichtung [kW]"])
date_col = find_col(["Inbetriebnahmedatum"])
postcode_col = find_col(["Postleitzahl"])
city_col = find_col(["Ort"])
district_col = find_col(["Kreis/kreisfreie Stadt"])
state_col = find_col(["Bundesland"])
lat_col = find_col(["Breitengrad"])
lon_col = find_col(["Längengrad"])

clean = pd.DataFrame()

clean["charging_facility_id"] = range(1, len(df) + 1)
clean["operator"] = df[operator_col].astype(str).str.strip()
clean["status"] = df[status_col].astype(str).str.strip()
clean["charger_type"] = df[type_col].astype(str).str.strip()
clean["charging_points"] = to_number(df[points_col])
clean["installed_power_kw"] = to_number(df[power_col])
clean["commissioning_date"] = pd.to_datetime(df[date_col], errors="coerce")
clean["commissioning_year"] = clean["commissioning_date"].dt.year

clean["postcode"] = df[postcode_col].astype(str).str.strip()
clean["city"] = df[city_col].astype(str).str.strip()
clean["district"] = df[district_col].astype(str).str.strip()
clean["state"] = df[state_col].astype(str).str.strip()

clean["latitude"] = to_number(df[lat_col])
clean["longitude"] = to_number(df[lon_col])

# --------------------------------------------------
# Charger type split
# --------------------------------------------------

clean["fast_charging_points"] = np.where(
    clean["charger_type"].str.lower().str.contains("schnell", na=False),
    clean["charging_points"],
    0
)

clean["normal_charging_points"] = np.where(
    clean["charger_type"].str.lower().str.contains("normal", na=False),
    clean["charging_points"],
    0
)

# Simple area type
clean["area_type"] = np.where(
    clean["district"].str.lower().str.contains("kreisfreie", na=False),
    "Urban / Kreisfreie Stadt",
    "District / Landkreis"
)

# --------------------------------------------------
# Final cleaning
# --------------------------------------------------

clean = clean[clean["charging_points"].notna()]
clean = clean[clean["charging_points"] > 0]
clean = clean[clean["installed_power_kw"].notna()]
clean = clean[clean["installed_power_kw"] > 0]
clean = clean[clean["state"].notna()]
clean = clean[clean["state"].astype(str).str.strip() != ""]

clean.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")

print("Clean file saved:")
print(OUT_FILE)
print("Rows:", len(clean))
print("Charging points:", clean["charging_points"].sum())
print("Installed power MW:", clean["installed_power_kw"].sum() / 1000)