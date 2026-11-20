"""
Extract Economy and Services indicators from ISTAT BES dei territori,
2025 edition, using 2023 data.

Run from the repository root:
    python src/economia_servizi.py

Output:
    data/estratti/economia_servizi.csv
"""

from pathlib import Path

import pandas as pd
from lettura_istat import leggi_istat


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "data" / "estratti" / "economia_servizi.csv"

YEAR = 2023

INDICATORS = {
    "04BEC001P": ("Economia", "+"),
    "04BEC002P": ("Economia", "+"),
    "12SER002P": ("Servizi", "+"),
    "12SER020": ("Servizi", "+"),
}

COLUMNS = [
    "provincia_id",
    "provincia",
    "area",
    "indicatore_id",
    "valore",
    "unita",
    "verso",
    "anno",
]


# ------------------------------------------------------------
# NUMERIC CONVERSION
# ------------------------------------------------------------

def to_number(series):
    """Convert ISTAT numeric values to numbers."""

    values = series.astype("string").str.strip()

    values = values.replace(
        ["....", "-", ""],
        pd.NA,
    )

    # Remove thousands separators when a decimal comma is present.
    has_comma = values.str.contains(",", regex=False, na=False)

    values = values.mask(
        has_comma,
        values.str.replace(".", "", regex=False),
    )

    values = values.str.replace(",", ".", regex=False)

    return pd.to_numeric(values, errors="coerce")


# ------------------------------------------------------------
# EXTRACTION
# ------------------------------------------------------------

def extract():

    # Common ISTAT loading and geographical filtering.
    dati, _ = leggi_istat()

    # Select the four assigned indicators.
    rows = dati.loc[
        dati["CODICE"].isin(INDICATORS)
    ].copy()

    # Convert 2023 values.
    rows["valore"] = to_number(rows["V2023"])

    # Assign macro-area and direction.
    rows["area"] = rows["CODICE"].map(
        {code: info[0] for code, info in INDICATORS.items()}
    )

    rows["verso"] = rows["CODICE"].map(
        {code: info[1] for code, info in INDICATORS.items()}
    )

    # Rename columns according to the common schema.
    rows = rows.rename(
        columns={
            "W_GEO": "provincia_id",
            "TERRITORIO": "provincia",
            "CODICE": "indicatore_id",
            "UNITA_MISURA": "unita",
        }
    )

    rows["anno"] = YEAR

    out = rows[COLUMNS].copy()

    out = out.sort_values(
        ["indicatore_id", "provincia_id"]
    ).reset_index(drop=True)

    return out


# ------------------------------------------------------------
# QUALITY CHECKS
# ------------------------------------------------------------

def report(df):

    rows = len(df)
    provinces = df["provincia_id"].nunique()
    indicators = df["indicatore_id"].nunique()

    duplicates = df.duplicated(
        ["provincia_id", "indicatore_id"]
    ).sum()

    missing = df["valore"].isna().sum()
    missing_units = df["unita"].isna().sum()

    print("\nECONOMY AND SERVICES EXTRACTION")
    print("-" * 50)

    print("Rows:", rows)
    print("Provinces:", provinces)
    print("Indicators:", indicators)
    print("Years:", df["anno"].unique().tolist())
    print("Missing values:", missing)
    print("Missing units:", missing_units)
    print("Duplicate province-indicator keys:", duplicates)

    print("\nCoverage per indicator:")
    print(
        df.groupby("indicatore_id")["valore"]
        .agg(present="count", total="size")
        .to_string()
    )

    if missing:
        print("\nRows with missing values:")
        print(
            df.loc[
                df["valore"].isna(),
                ["provincia_id", "provincia", "indicatore_id"],
            ].to_string(index=False)
        )

    # Automatic validation.
    assert rows == 428, f"Expected 428 rows, found {rows}"
    assert provinces == 107, f"Expected 107 provinces, found {provinces}"
    assert indicators == 4, f"Expected 4 indicators, found {indicators}"
    assert duplicates == 0, f"Found {duplicates} duplicate keys"
    assert set(df["anno"]) == {YEAR}
    assert set(df["indicatore_id"]) == set(INDICATORS)
    assert missing_units == 0, f"Found {missing_units} missing units"

    coverage = df.groupby("indicatore_id")["provincia_id"].nunique()

    assert (coverage == 107).all(), (
        "Some indicators do not cover all 107 provinces"
    )

    print("\nAll data quality checks passed!")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":

    df = extract()
    report(df)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"\nCSV saved successfully: {OUT_FILE.relative_to(ROOT)}")