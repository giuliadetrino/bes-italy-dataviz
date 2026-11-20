from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "elaborati" / "bes_2023_normalizzato.csv"

AREE_ATTESE = [
    "Salute",
    "Istruzione e formazione",
    "Lavoro",
    "Economia",
    "Ambiente",
    "Servizi",
    "Sicurezza",
]


def calcola_punteggi_aree(
    df_norm: pd.DataFrame,
    colonna_punteggio: str = "punteggio",
) -> pd.DataFrame:
    """
    Calcola la media semplice degli indicatori normalizzati (0-100) per ogni
    provincia e per ciascuna delle sette aree di benessere.

    Restituisce un DataFrame con: provincia_id, provincia, area, punteggio_area.
    """
    colonne_richieste = {"provincia_id", "provincia", "area", colonna_punteggio}
    mancanti = colonne_richieste - set(df_norm.columns)
    if mancanti:
        raise ValueError(f"Colonne mancanti in df_norm: {mancanti}")

    aree = (
        df_norm.groupby(["provincia_id", "provincia", "area"], as_index=False)[colonna_punteggio]
        .mean()
        .rename(columns={colonna_punteggio: "punteggio_area"})
    )
    return aree


def calcola_indice(
    df_aree: pd.DataFrame,
    pesi: dict[str, float],
    solo_complete: bool = True,
) -> pd.DataFrame:
    """
    Calcola l'indice sintetico per ogni provincia come media delle sette aree
    ponderata dai pesi scelti negli slider.

    Se solo_complete=True (accordo tecnico di pag. 1: classifica sulle province
    con tutti i 14 indicatori / 7 aree valide), esclude le province con punteggi
    di area mancanti.

    Restituisce un DataFrame con: provincia_id, provincia, indice.
    """
    colonne_richieste = {"provincia_id", "provincia", "area", "punteggio_area"}
    mancanti = colonne_richieste - set(df_aree.columns)
    if mancanti:
        raise ValueError(f"Colonne mancanti in df_aree: {mancanti}")

    if any(p < 0 for p in pesi.values()):
        raise ValueError("I pesi non possono essere negativi.")

    somma_pesi = sum(pesi.values())
    if somma_pesi <= 0:
        raise ValueError("Almeno un'area deve avere peso maggiore di zero.")

    dati = df_aree.copy()

    if solo_complete:
        province_incomplete = dati.loc[dati["punteggio_area"].isna(), "provincia_id"].unique()
        dati = dati[~dati["provincia_id"].isin(province_incomplete)].copy()

    pesi_norm = {area: peso / somma_pesi for area, peso in pesi.items()}
    dati["peso_norm"] = dati["area"].map(pesi_norm).fillna(0.0)
    dati["contributo"] = dati["punteggio_area"] * dati["peso_norm"]

    risultato = (
        dati.groupby(["provincia_id", "provincia"], as_index=False)["contributo"]
        .sum(min_count=1)
        .rename(columns={"contributo": "indice"})
    )
    return risultato


if __name__ == "__main__":
    # 1. Test sintetico in memoria
    righe = []
    punteggi_prova = {
        "Salute": [80.0, 90.0],
        "Istruzione e formazione": [70.0, 80.0],
        "Lavoro": [60.0, 80.0],
        "Economia": [75.0, 85.0],
        "Ambiente": [50.0, 60.0],
        "Servizi": [65.0, 75.0],
        "Sicurezza": [40.0, 50.0],
    }
    for area, valori in punteggi_prova.items():
        for i, val in enumerate(valori):
            righe.append({
                "provincia_id": "001",
                "provincia": "Provincia A",
                "area": area,
                "indicatore_id": f"{area[:3].upper()}_{i+1}",
                "punteggio": val,
            })

    df_prova = pd.DataFrame(righe)
    df_aree_prova = calcola_punteggi_aree(df_prova)

    # Verifica requisito: con una sola area attiva, indice e punteggio di area coincidono
    pesi_solo_lavoro = {a: (100.0 if a == "Lavoro" else 0.0) for a in AREE_ATTESE}
    df_ind_prova = calcola_indice(df_aree_prova, pesi_solo_lavoro)
    lavoro_a = df_aree_prova.loc[df_aree_prova["area"] == "Lavoro", "punteggio_area"].item()
    assert abs(df_ind_prova["indice"].item() - lavoro_a) < 1e-9

    # 2. Verifica sul dataset reale normalizzato
    if INPUT_FILE.exists():
        df_reale = pd.read_csv(INPUT_FILE, dtype={"provincia_id": str})
        df_aree_reale = calcola_punteggi_aree(df_reale)

        pesi_uguali = {a: 1.0 for a in AREE_ATTESE}
        df_ind_reale = calcola_indice(df_aree_reale, pesi_uguali, solo_complete=True)

        pesi_solo_salute = {a: (1.0 if a == "Salute" else 0.0) for a in AREE_ATTESE}
        df_solo_salute = calcola_indice(df_aree_reale, pesi_solo_salute, solo_complete=True)

        confronto = df_aree_reale[df_aree_reale["area"] == "Salute"].merge(
            df_solo_salute, on=["provincia_id", "provincia"]
        )
        assert (confronto["punteggio_area"] - confronto["indice"]).abs().max() < 1e-9

        print("Province ammesse (complete):", len(df_ind_reale))
        print("Top 5 con pesi uguali:")
        print(df_ind_reale.sort_values("indice", ascending=False).head(5).to_string(index=False))

    print("Verifica OK")
