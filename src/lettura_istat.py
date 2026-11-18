import pandas as pd


def leggi_istat():
    dati = pd.read_excel("data/raw/Indicatori_per_provincia_sesso_ed.2025.xlsx", dtype=str)
    metadati = pd.read_excel("data/raw/Metadati_IT_ed.2025.xlsx", dtype=str)
    dati = dati.loc[dati["SESSO"] == "Totale"].copy()
    province = dati["W_GEO"].str.fullmatch(r"\d{2}-\d{2}-\d{3}", na=False)
    dati = dati.loc[province & ~dati["W_GEO"].str.endswith("000", na=False)].copy()
    province_storiche_sardegna = ["05-21-107", "05-21-108", "05-21-109", "05-21-110"]
    dati = dati.loc[~dati["W_GEO"].isin(province_storiche_sardegna)].copy()
    colonne = ["W_GEO", "TERRITORIO", "CODICE", "INDICATORE", "UNITA_MISURA", "V2023", "NOTA"]
    dati = dati[colonne]
    return dati, metadati


if __name__ == "__main__":
    dati, metadati = leggi_istat()
    print("Dimensioni dati:", dati.shape)
    print("Dimensioni metadati:", metadati.shape)