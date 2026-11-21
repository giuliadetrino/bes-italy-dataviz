"""
Turn the weighted index into a ranking of the provinces.

Rules (from the project plan):
- order by index, highest first, at full precision (no rounding before ranking);
- provinces with exactly the same index share the same position and the next
  one skips ahead ("competition" ranking): 1, 1, 3;
- provinces without an index (NaN) get no position and are left out.

Input:  DataFrame from src/indice.py with provincia_id, provincia, indice.
Output: rows with a non-missing index, sorted by position, with an extra integer
        column 'posizione'.

Run from the repo root to check it:
    python src/posizioni.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "elaborati" / "bes_2023_normalizzato.csv"


def calcola_posizioni(df_indice: pd.DataFrame) -> pd.DataFrame:
    """
    Add the column 'posizione' (1 = best) to the output of calcola_indice().

    Ties at full precision share the lowest position (1, 1, 3).
    Rows with a missing index are dropped. Sorted by posizione, then provincia.
    """
    richieste = {"provincia_id", "provincia", "indice"}
    mancanti = richieste - set(df_indice.columns)
    if mancanti:
        raise ValueError(f"Colonne mancanti in df_indice: {mancanti}")
    if df_indice["provincia_id"].duplicated().any():
        raise ValueError("Ogni provincia deve comparire una sola volta.")

    dati = df_indice.loc[df_indice["indice"].notna()].copy()
    dati["posizione"] = (
        dati["indice"].rank(method="min", ascending=False).astype(int)
    )
    return dati.sort_values(["posizione", "provincia"]).reset_index(drop=True)


if __name__ == "__main__":
    # 1) Ties: two provinces first ex aequo, the next one is third
    prova = pd.DataFrame({
        "provincia_id": ["A", "B", "C", "D"],
        "provincia": ["Provincia A", "Provincia B", "Provincia C", "Provincia D"],
        "indice": [70.0, 80.0, 80.0, 60.0],
    })
    pos = calcola_posizioni(prova)
    print(pos.to_string(index=False))
    assert pos["posizione"].tolist() == [1, 1, 3, 4]
    assert pos["provincia"].tolist()[2] == "Provincia A"

    # 2) Full precision: a tiny difference is NOT a tie
    vicine = pd.DataFrame({
        "provincia_id": ["X", "Y"],
        "provincia": ["Provincia X", "Provincia Y"],
        "indice": [55.000000001, 55.0],
    })
    pos_vicine = calcola_posizioni(vicine)
    assert pos_vicine["provincia_id"].tolist() == ["X", "Y"]
    assert pos_vicine["posizione"].tolist() == [1, 2]

    # 3) Missing index -> no position
    con_nan = pd.concat([prova, pd.DataFrame({
        "provincia_id": ["E"], "provincia": ["Provincia E"], "indice": [float("nan")],
    })])
    assert "E" not in set(calcola_posizioni(con_nan)["provincia_id"])

    print("\nTest sintetici OK")

    # 4) Real data, end to end: normalized CSV -> indice.py -> positions
    if not INPUT_FILE.exists():
        print("Verifica sui dati reali saltata: CSV assente.")
    else:
        from indice import AREE_ATTESE, calcola_indice, calcola_punteggi_aree

        df_norm = pd.read_csv(INPUT_FILE, dtype={"provincia_id": str})
        col = "valore_norm" if "valore_norm" in df_norm.columns else "punteggio"
        aree = calcola_punteggi_aree(df_norm, colonna_punteggio=col)

        pesi_uguali = {a: 1.0 for a in AREE_ATTESE}
        classifica = calcola_posizioni(calcola_indice(aree, pesi_uguali))
        print("\nPesi uguali, prime 5 province:")
        print(classifica.head(5).to_string(index=False))
        print("Province in classifica:", len(classifica),
              "| posizioni da", classifica["posizione"].min(),
              "a", classifica["posizione"].max(),
              "| ex aequo:", classifica["posizione"].duplicated().sum())
        assert len(classifica) == 105
        assert classifica["posizione"].min() == 1
        assert classifica["indice"].is_monotonic_decreasing
        print("Verifica sui dati reali OK")
