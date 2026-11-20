"""
Prepare the shared ISTAT BES 2023 dataset.

Inputs:
    data/estratti/ambiente_sicurezza.csv
    data/estratti/economia_servizi.csv
    data/estratti/lavoro.csv
    data/estratti/salute_istruzione.csv

Outputs:
    data/elaborati/bes_2023.csv
    data/elaborati/copertura.csv

The script:
1. Combines the four extraction files.
2. Validates the common schema.
3. Checks indicators, provinces and duplicates.
4. Calculates data coverage for each indicator.
5. Preserves missing values.
"""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INPUT_DIR = ROOT / "data" / "estratti"
OUTPUT_DIR = ROOT / "data" / "elaborati"

FILES = [
    "ambiente_sicurezza.csv",
    "economia_servizi.csv",
    "lavoro.csv",
    "salute_istruzione.csv",
]

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

EXPECTED_PROVINCES = 107
EXPECTED_INDICATORS = 14
EXPECTED_ROWS = 1498
YEAR = 2023

# ------------------------------------------------------------
# METHODOLOGICAL NOTE: URBAN GREEN
# ------------------------------------------------------------

# Indicator 10AMB008 measures urban green space (m² per inhabitant)
# in provincial/metropolitan capital municipalities, not in the
# entire province.
#
# Inclusion criterion:
# We retain the indicator as a capital-city proxy associated with
# the corresponding province, preserving the original ISTAT values.
#
# Interpretation:
# The indicator describes urban environmental conditions in the
# provincial capital. It must not be interpreted as province-wide
# green-space availability.
#
# Limitations:
# - Capital-city conditions may not represent the entire province.
# - Extreme values may influence min-max normalization.
# - The province-to-capital association must be verified.
#
# The indicator is retained for the environmental dimension,
# with these limitations explicitly documented.
# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

def load_data():

    datasets = []

    for filename in FILES:

        path = INPUT_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Missing input file: {path}"
            )

        df = pd.read_csv(
            path,
            dtype={"provincia_id": str}
        )

        if list(df.columns) != COLUMNS:
            raise ValueError(
                f"Unexpected columns in {filename}: "
                f"{df.columns.tolist()}"
            )

        datasets.append(df)

        print(
            f"Loaded {filename}: "
            f"{len(df)} rows, "
            f"{df['indicatore_id'].nunique()} indicators"
        )

    return pd.concat(
        datasets,
        ignore_index=True
    )


# ------------------------------------------------------------
# DATA QUALITY
# ------------------------------------------------------------

def validate_data(df):

    print("\nDATA QUALITY REPORT")
    print("-" * 55)

    rows = len(df)
    provinces = df["provincia_id"].nunique()
    indicators = df["indicatore_id"].nunique()
    areas = df["area"].nunique()

    duplicates = df.duplicated(
        ["provincia_id", "indicatore_id"]
    ).sum()

    missing = df["valore"].isna().sum()

    print("Rows:", rows)
    print("Provinces:", provinces)
    print("Indicators:", indicators)
    print("Macroareas:", areas)
    print("Missing values:", missing)
    print("Duplicate province-indicator keys:", duplicates)

    print("\nMacroareas:")
    print(sorted(df["area"].unique().tolist()))

    print("\nMissing values by indicator:")

    print(
        df.groupby("indicatore_id")["valore"]
        .apply(lambda x: x.isna().sum())
        .to_string()
    )

    assert rows == EXPECTED_ROWS
    assert provinces == EXPECTED_PROVINCES
    assert indicators == EXPECTED_INDICATORS
    assert areas == 7
    assert duplicates == 0
    assert set(df["anno"]) == {YEAR}

    # Ensure each indicator covers all 107 provinces.
    coverage_rows = df.groupby(
        "indicatore_id"
    )["provincia_id"].nunique()

    assert (coverage_rows == EXPECTED_PROVINCES).all()

    # Verify that all indicators use exactly the same province IDs.
    province_sets = {
        code: set(group["provincia_id"])
        for code, group in df.groupby("indicatore_id")
    }

    reference_provinces = next(iter(province_sets.values()))

    for code, provinces in province_sets.items():
        assert provinces == reference_provinces, (
            f"Inconsistent province IDs for indicator {code}"
        )

    print("\nAll data quality checks passed!")


# ------------------------------------------------------------
# COVERAGE REPORT
# ------------------------------------------------------------

def create_coverage(df):

    coverage = (
        df.groupby(
            ["area", "indicatore_id"],
            as_index=False
        )
        .agg(
            province_totali=("provincia_id", "nunique"),
            province_con_dato=("valore", "count"),
        )
    )

    coverage["province_senza_dato"] = (
        coverage["province_totali"]
        - coverage["province_con_dato"]
    )

    coverage["copertura_pct"] = (
        coverage["province_con_dato"]
        / coverage["province_totali"]
        * 100
    ).round(2)

    return coverage.sort_values(
        ["area", "indicatore_id"]
    ).reset_index(drop=True)


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":

    print("PREPARING SHARED BES 2023 DATASET")
    print("=" * 55)

    dataset = load_data()

    dataset = dataset.sort_values(
        ["provincia_id", "indicatore_id"]
    ).reset_index(drop=True)

    validate_data(dataset)

    coverage = create_coverage(dataset)

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    dataset.to_csv(
        OUTPUT_DIR / "bes_2023.csv",
        index=False
    )

    coverage.to_csv(
        OUTPUT_DIR / "copertura.csv",
        index=False
    )

    print("\nCOVERAGE REPORT")
    print("-" * 55)
    print(coverage.to_string(index=False))

    print("\nFiles saved:")
    print("data/elaborati/bes_2023.csv")
    print("data/elaborati/copertura.csv")