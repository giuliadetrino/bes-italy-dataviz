"""
Normalize the 14 ISTAT BES indicators to a common 0-100 scale.

Input:
    data/elaborati/bes_2023.csv

Output:
    data/elaborati/bes_2023_normalizzato.csv

Method:
    Min-Max normalization applied independently to each indicator.

    Positive indicators (+):
        score = 100 * (x - min) / (max - min)

    Negative indicators (-):
        score = 100 * (max - x) / (max - min)

Missing values remain NaN.

If min == max, normalization is undefined and scores remain NaN.
"""

from pathlib import Path

import pandas as pd


# ------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = ROOT / "data" / "elaborati" / "bes_2023.csv"

OUTPUT_FILE = (
    ROOT / "data" / "elaborati" / "bes_2023_normalizzato.csv"
)

EXPECTED_ROWS = 1498
EXPECTED_INDICATORS = 14
EXPECTED_PROVINCES = 107


# ------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------

def normalizza_indicatori(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize each indicator independently to a 0-100 score.

    Required columns:
        provincia_id, indicatore_id, valore, verso

    Returns:
        A copy of the input DataFrame with an additional
        column named 'punteggio'.
    """

    required = {
        "provincia_id",
        "indicatore_id",
        "valore",
        "verso",
    }

    missing_columns = required - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    result = df.copy()

    result["punteggio"] = float("nan")

    for indicator, group in result.groupby("indicatore_id"):

        directions = group["verso"].dropna().unique()

        if len(directions) != 1:
            raise ValueError(
                f"Inconsistent directions for {indicator}"
            )

        direction = directions[0]

        if direction not in {"+", "-"}:
            raise ValueError(
                f"Invalid direction for {indicator}: {direction}"
            )

        values = pd.to_numeric(
            group["valore"],
            errors="raise",
        )

        minimum = values.min()
        maximum = values.max()

        # All values missing or constant indicator.
        if pd.isna(minimum) or pd.isna(maximum):
            print(
                f"WARNING: {indicator} has no valid values."
            )
            continue

        if minimum == maximum:
            print(
                f"WARNING: {indicator} has constant values."
            )
            continue

        if direction == "+":
            scores = (
                100 * (values - minimum)
                / (maximum - minimum)
            )
        else:
            scores = (
                100 * (maximum - values)
                / (maximum - minimum)
            )

        result.loc[group.index, "punteggio"] = scores

    return result


# ------------------------------------------------------------
# DATA QUALITY CHECKS
# ------------------------------------------------------------

def verifica_normalizzazione(df: pd.DataFrame):

    print("\nNORMALIZATION QUALITY REPORT")
    print("-" * 55)

    print("Rows:", len(df))
    print("Provinces:", df["provincia_id"].nunique())
    print("Indicators:", df["indicatore_id"].nunique())

    print(
        "Missing original values:",
        df["valore"].isna().sum(),
    )

    print(
        "Missing normalized scores:",
        df["punteggio"].isna().sum(),
    )

    print("\nNormalized score ranges:")

    ranges = (
        df.groupby("indicatore_id")["punteggio"]
        .agg(["min", "max", "count"])
    )

    print(ranges.to_string())

    # Structural checks
    assert len(df) == EXPECTED_ROWS
    assert df["provincia_id"].nunique() == EXPECTED_PROVINCES
    assert df["indicatore_id"].nunique() == EXPECTED_INDICATORS

    assert df.duplicated(
        ["provincia_id", "indicatore_id"]
    ).sum() == 0

    # Scores must stay within 0-100.
    valid_scores = df["punteggio"].dropna()

    assert valid_scores.between(
        -1e-9, 100 + 1e-9
    ).all()

    # Missing original values must remain missing.
    assert df.loc[
        df["valore"].isna(), "punteggio"
    ].isna().all()

    # All indicators in this dataset have non-constant values.
    assert (
        df["punteggio"].isna().sum()
        == df["valore"].isna().sum()
    )

    # Each indicator must reach approximately 0 and 100.
    assert (ranges["min"].abs() < 1e-8).all()

    assert (
        (ranges["max"] - 100).abs() < 1e-8
    ).all()

    print("\nAll normalization checks passed!")


# ------------------------------------------------------------
# TESTS
# ------------------------------------------------------------

def test_normalizzazione():

    print("\nRUNNING NORMALIZATION TESTS")
    print("-" * 55)

    test_data = pd.DataFrame({
        "provincia_id": [
            "P1", "P2", "P3",
            "P1", "P2", "P3",
        ],
        "indicatore_id": [
            "POS", "POS", "POS",
            "NEG", "NEG", "NEG",
        ],
        "valore": [
            10, 20, 30,
            10, 20, 30,
        ],
        "verso": [
            "+", "+", "+",
            "-", "-", "-",
        ],
    })

    result = normalizza_indicatori(test_data)

    positive = result.loc[
        result["indicatore_id"] == "POS",
        "punteggio",
    ].tolist()

    negative = result.loc[
        result["indicatore_id"] == "NEG",
        "punteggio",
    ].tolist()

    assert positive == [0.0, 50.0, 100.0]

    assert negative == [100.0, 50.0, 0.0]

    print("Positive indicator test: PASSED")
    print("Negative indicator test: PASSED")

    # Missing value test
    missing_test = pd.DataFrame({
        "provincia_id": ["P1", "P2", "P3"],
        "indicatore_id": ["MISS"] * 3,
        "valore": [10.0, None, 30.0],
        "verso": ["+"] * 3,
    })

    missing_result = normalizza_indicatori(missing_test)

    assert pd.isna(
        missing_result.loc[1, "punteggio"]
    )

    print("Missing value test: PASSED")

    # Constant values test
    constant_test = pd.DataFrame({
        "provincia_id": ["P1", "P2", "P3"],
        "indicatore_id": ["CONST"] * 3,
        "valore": [10, 10, 10],
        "verso": ["+"] * 3,
    })

    constant_result = normalizza_indicatori(
        constant_test
    )

    assert constant_result["punteggio"].isna().all()

    print("Constant indicator test: PASSED")

    print("\nAll unit tests passed!")


# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------

if __name__ == "__main__":

    test_normalizzazione()

    print("\nLOADING BES 2023 DATASET")
    print("=" * 55)

    dataset = pd.read_csv(
        INPUT_FILE,
        dtype={"provincia_id": str},
    )

    normalized = normalizza_indicatori(dataset)

    verifica_normalizzazione(normalized)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    normalized.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"\nSaved: {OUTPUT_FILE.relative_to(ROOT)}"
    )