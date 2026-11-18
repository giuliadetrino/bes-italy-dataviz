"""Extract the Economy and Quality of services indicators (ISTAT BES dei territori, ed. 2025, year 2023).

Run from the repository root:
    python src/economia_servizi.py

Output: data/estratti/economia_servizi.csv
Columns: provincia_id, provincia, area, indicatore_id, valore, unita, verso, anno

Notes
- provincia_id is the ISTAT W_GEO code (e.g. "01-01-001"), kept as text. The last three
  digits alone are NOT unique (Torino, Bolzano and Trento are all "001").
- Only provinces are kept: regions/Italy ("...-000") and macro-areas ("10-00-000a" etc.)
  are dropped, as are the four Sardinian provinces abolished in 2016, which have no 2023 data.
- ISTAT placeholders ("....", "-") become missing values and are kept as missing.
- unita comes from the metadata file, so it carries the denominator (e.g. "Per 10.000 abitanti").
- TODO: when Giulia pushes src/lettura_istat.py, replace read_istat() with her shared function.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "raw" / "Indicatori_per_provincia_sesso_ed.2025.xlsx"
META_FILE = ROOT / "data" / "raw" / "Metadati_IT_ed.2025.xlsx"
OUT_FILE = ROOT / "data" / "estratti" / "economia_servizi.csv"

YEAR = 2023
SEX = "Totale"
COLUMNS = ["provincia_id", "provincia", "area", "indicatore_id", "valore", "unita", "verso", "anno"]

# indicatore_id -> verso (+ = higher is better)
INDICATORS = {
    "04BEC001P": "+",  # Reddito medio disponibile pro capite
    "04BEC002P": "+",  # Retribuzione media annua dei lavoratori dipendenti
    "12SER002P": "+",  # Medici specialisti
    "12SER020": "+",   # Copertura della rete fissa di accesso ultra veloce a internet
}

# Provinces abolished in 2016 (still listed for some indicators, no 2023 values)
ABOLISHED = {"05-21-107", "05-21-108", "05-21-109", "05-21-110"}

PROVINCE_CODE = r"^\d{2}-\d{2}-\d{3}$"


def read_istat():
    """Read the BES data and metadata Excel files as text."""
    data = pd.read_excel(DATA_FILE, dtype=str)
    meta = pd.read_excel(META_FILE, dtype=str)
    meta.columns = [" ".join(str(c).split()) for c in meta.columns]
    return data, meta


def to_number(series):
    """'24218,2' -> 24218.2; ISTAT placeholders ('....', '-') -> NaN."""
    clean = series.str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(clean, errors="coerce")


def extract():
    data, meta = read_istat()

    rows = data[data["CODICE"].isin(INDICATORS) & (data["SESSO"] == SEX)]
    is_province = rows["W_GEO"].str.match(PROVINCE_CODE) & ~rows["W_GEO"].str.endswith("000")
    rows = rows[is_province & ~rows["W_GEO"].isin(ABOLISHED)]

    meta_sel = meta[meta["Cod. indicatore"].isin(INDICATORS)].drop_duplicates("Cod. indicatore")
    units = meta_sel.set_index("Cod. indicatore")["Unità di misura"]
    raw_2023 = rows[f"V{YEAR}"]

    out = pd.DataFrame({
        "provincia_id": rows["W_GEO"].astype(str),
        "provincia": rows["TERRITORIO"],
        "area": rows["DOMINIO"],
        "indicatore_id": rows["CODICE"],
        "valore": to_number(raw_2023.fillna("")),
        "unita": rows["CODICE"].map(units),
        "verso": rows["CODICE"].map(INDICATORS),
        "anno": YEAR,
    })[COLUMNS].sort_values(["indicatore_id", "provincia_id"]).reset_index(drop=True)

    # Print metadata used, so unit and denominator can be checked against the definitions
    print("Indicators (from metadata):")
    for code in INDICATORS:
        m = meta[meta["Cod. indicatore"] == code].iloc[0]
        print(f"  {code} | {m['Indicatore']} | unit: {m['Unità di misura']}")
        print(f"      {m['Definizione']}")
    return out


def report(df):
    dup = df.duplicated(["provincia_id", "indicatore_id"]).sum()
    print(f"\nRows: {len(df)} | provinces: {df['provincia_id'].nunique()} | "
          f"indicators: {df['indicatore_id'].nunique()} | years: {sorted(int(y) for y in df['anno'].unique())}")
    print(f"Duplicate province-indicator keys: {dup}")
    print("\nCoverage per indicator (provinces with a 2023 value):")
    print(df.groupby("indicatore_id")["valore"].agg(present="count", total="size").to_string())
    missing = df[df["valore"].isna()]
    print(f"\nMissing values: {len(missing)}")
    if len(missing):
        print(missing[["provincia_id", "provincia", "indicatore_id"]].to_string(index=False))


if __name__ == "__main__":
    df = extract()
    report(df)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"\nSaved {OUT_FILE.relative_to(ROOT)}")
