from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents
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


def _media_senza_missing(serie: pd.Series) -> float:
    """Restituisce la media semplice solo se nessun indicatore dell'area è NaN."""
    if serie.isna().any():
        return float("nan")
    return float(serie.mean())


def calcola_punteggi_aree(
    df_norm: pd.DataFrame,
    colonna_punteggio: str = "valore_norm",
) -> pd.DataFrame:
    """
    Calcola la media semplice degli indicatori normalizzati (0-100) per ogni
    provincia e per ciascuna delle sette aree di benessere.
    Se anche un solo indicatore dell'area è mancante (NaN), il punteggio dell'area è NaN.

    Restituisce un DataFrame con: provincia_id, provincia, area, punteggio_area.
    """
    colonne_richieste = {"provincia_id", "provincia", "area", colonna_punteggio}
    mancanti = colonne_richieste - set(df_norm.columns)
    if mancanti:
        raise ValueError(f"Colonne mancanti in df_norm: {mancanti}")

    aree = (
        df_norm.groupby(["provincia_id", "provincia", "area"], as_index=False)[colonna_punteggio]
        .agg(_media_senza_missing)
        .rename(columns={colonna_punteggio: "punteggio_area"})
    )
    return aree


def _valida_pesi(pesi: dict[str, float]) -> dict[str, float]:
    """Verifica che pesi contenga esattamente le 7 aree attese e valori non negativi."""
    chiavi = set(pesi.keys())
    attese = set(AREE_ATTESE)
    if chiavi != attese:
        mancanti = sorted(attese - chiavi)
        extra = sorted(chiavi - attese)
        raise ValueError(f"Chiavi pesi non valide. Mancanti: {mancanti}, extra: {extra}")

    if any(p < 0 for p in pesi.values()):
        raise ValueError("I pesi non possono essere negativi.")

    somma_pesi = sum(pesi.values())
    if somma_pesi <= 0:
        raise ValueError("Almeno un'area deve avere peso maggiore di zero.")

    return {area: peso / somma_pesi for area, peso in pesi.items()}


def _valida_copertura_aree(df_aree: pd.DataFrame) -> None:
    """Verifica che ogni provincia abbia esattamente tutte le 7 macroaree attese."""
    attese = set(AREE_ATTESE)
    for (prov_id, prov_nome), gruppo in df_aree.groupby(["provincia_id", "provincia"]):
        if gruppo["area"].duplicated().any():
            raise ValueError(f"Macroaree duplicate per {prov_nome} ({prov_id}).")
        presenti = set(gruppo["area"])
        if presenti != attese:
            mancanti = sorted(attese - presenti)
            raise ValueError(f"Macroaree mancanti per {prov_nome} ({prov_id}): {mancanti}")


def calcola_indice(
    df_aree: pd.DataFrame,
    pesi: dict[str, float],
    solo_complete: bool = True,
) -> pd.DataFrame:
    """
    Calcola l'indice sintetico per ogni provincia come media delle sette aree
    ponderata dai pesi scelti negli slider.

    Se solo_complete=True, vengono ammesse solo le province con punteggio valido
    su tutte e sette le macroaree (escludendo quelle con almeno un NaN).
    Restituisce un DataFrame con: provincia_id, provincia, indice.
    """
    colonne_richieste = {"provincia_id", "provincia", "area", "punteggio_area"}
    mancanti = colonne_richieste - set(df_aree.columns)
    if mancanti:
        raise ValueError(f"Colonne mancanti in df_aree: {mancanti}")

    pesi_norm = _valida_pesi(pesi)
    _valida_copertura_aree(df_aree)

    dati = df_aree.copy()
    if solo_complete:
        province_incomplete = dati.loc[dati["punteggio_area"].isna(), "provincia_id"].unique()
        dati = dati.loc[~dati["provincia_id"].isin(province_incomplete)].copy()

    dati["peso_norm"] = dati["area"].map(pesi_norm)
    dati["contributo"] = dati["punteggio_area"] * dati["peso_norm"]

    risultato = (
        dati.groupby(["provincia_id", "provincia"], as_index=False)["contributo"]
        .sum()
        .rename(columns={"contributo": "indice"})
    )
    return risultato


if __name__ == "__main__":
    # 1. Test in memoria sulle 7 aree
    punteggi_a = {
        "Salute": [80.0, 90.0],
        "Istruzione e formazione": [70.0],
        "Lavoro": [60.0, 80.0],
        "Economia": [75.0],
        "Ambiente": [50.0],
        "Servizi": [65.0],
        "Sicurezza": [40.0],
    }
    righe = [
        {
            "provincia_id": "001",
            "provincia": "Provincia A",
            "area": area,
            "indicatore_id": f"{area[:3].upper()}_{i+1}",
            "valore_norm": val,
        }
        for area, valori in punteggi_a.items()
        for i, val in enumerate(valori)
    ]

    df_prova = pd.DataFrame(righe)
    df_aree_prova = calcola_punteggi_aree(df_prova)

    salute_a = df_aree_prova.loc[df_aree_prova["area"] == "Salute", "punteggio_area"].item()
    assert abs(salute_a - 85.0) < 1e-9

    pesi_solo_lavoro = {a: (100.0 if a == "Lavoro" else 0.0) for a in AREE_ATTESE}
    df_indice_lavoro = calcola_indice(df_aree_prova, pesi_solo_lavoro)
    lavoro_a = df_aree_prova.loc[df_aree_prova["area"] == "Lavoro", "punteggio_area"].item()
    assert abs(df_indice_lavoro["indice"].item() - lavoro_a) < 1e-9

    # 2. Test sul dataset reale (se presente in data/elaborati)
    if INPUT_FILE.exists():
        df_reale = pd.read_csv(INPUT_FILE, dtype={"provincia_id": str})
        col_norm = "valore_norm" if "valore_norm" in df_reale.columns else "punteggio"
        df_aree_reale = calcola_punteggi_aree(df_reale, colonna_punteggio=col_norm)

        pesi_uguali = {a: 1.0 for a in AREE_ATTESE}
        df_indice_reale = calcola_indice(df_aree_reale, pesi_uguali, solo_complete=True)

        province_ammesse = set(df_indice_reale["provincia"])
        escluse = sorted(set(df_reale["provincia"]) - province_ammesse)
        print("Province ammesse (solo_complete=True):", len(df_indice_reale))
        print("Province escluse:", escluse)
        assert len(df_indice_reale) == 105
        assert not any("Bolzano" in p for p in province_ammesse)
        assert not any("Sud Sardegna" in p for p in province_ammesse)

    print("Verifica OK")
