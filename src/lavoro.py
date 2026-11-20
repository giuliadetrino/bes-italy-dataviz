import pandas as pd
from lettura_istat import leggi_istat
from pathlib import Path

dati, metadati = leggi_istat()

codici_scelti = [
    "03LAV001-N22",   # Tasso di occupazione (20-64 anni)
    "03LAV003P-N22",  # Tasso di occupazione giovanile (15-29 anni)
]

estratto = dati.loc[dati["CODICE"].isin(codici_scelti)].copy()

valori = estratto["V2023"].replace("....", pd.NA)
valori = valori.str.replace(",", ".", regex=False)
estratto["valore"] = pd.to_numeric(valori, errors="raise")

estratto["area"] = "Lavoro"
estratto["verso"] = "+"

estratto = estratto.rename(columns={
    "W_GEO": "provincia_id",
    "TERRITORIO": "provincia",
    "CODICE": "indicatore_id",
    "UNITA_MISURA": "unita",
})

estratto["anno"] = 2023

colonne = [
    "provincia_id", "provincia", "area", "indicatore_id",
    "valore", "unita", "verso", "anno",
]
estratto = estratto[colonne]

province = estratto[["provincia_id", "provincia"]].drop_duplicates()
indicatori = estratto[["area", "indicatore_id", "unita", "verso", "anno"]].drop_duplicates()

combinazioni = province.merge(indicatori, how="cross")

estratto = combinazioni.merge(
    estratto[["provincia_id", "indicatore_id", "valore"]],
    on=["provincia_id", "indicatore_id"],
    how="left",
    validate="one_to_one",
)

estratto = estratto[colonne]

print("Indicatori distinti:", estratto["indicatore_id"].nunique(), estratto["indicatore_id"].unique().tolist())
print("Anni presenti:", estratto["anno"].unique().tolist())
print("Valori mancanti:", estratto["valore"].isna().sum())
print("Duplicati provincia-indicatore:", estratto.duplicated(["provincia_id", "indicatore_id"]).sum())
print("Dimensioni:", estratto.shape)
print(estratto.head(4).to_string(index=False))

cartella = Path("data/estratti")
cartella.mkdir(parents=True, exist_ok=True)

percorso_csv = cartella / "lavoro.csv"
estratto.to_csv(percorso_csv, index=False)

print("CSV salvato in:", percorso_csv)
