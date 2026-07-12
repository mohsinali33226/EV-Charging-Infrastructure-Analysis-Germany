from pathlib import Path
import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
IN_FILE = PROJECT_DIR / "data_raw" / "kba_bev_by_state.csv"

# Try common encodings/separators
try:
    df = pd.read_csv(IN_FILE, sep=",", encoding="utf-8-sig")
except:
    df = pd.read_csv(IN_FILE, sep=";", encoding="utf-8-sig")

print("\nColumns in KBA file:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())

print("\nShape:")
print(df.shape)