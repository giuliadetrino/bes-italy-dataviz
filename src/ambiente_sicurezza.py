import pandas as pd
from lettura_istat import leggi_istat
from pathlib import Path

dati, metadati = leggi_istat()

codici_scelti = [
    "10AMB017",   # Raccolta differenziata dei rifiuti urbani
    "10AMB008",   # Disponibilità di verde urbano
    "07SIC004P",  # Denunce di furto in abitazione
    "07SIC005P",  # Denunce di borseggio
    "07SIC006P",  # Denunce di rapina
]

estratto = dati.loc[dati["CODICE"].isin(codici_scelti)].copy()

valori = estratto["V2023"].replace("....", pd.NA)
valori = valori.str.replace(",", ".", regex=False)
estratto["valore"] = pd.to_numeric(valori, errors="raise")

area_per_codice = {
    "10AMB017": "Ambiente",
    "10AMB008": "Ambiente",
    "07SIC004P": "Sicurezza",
    "07SIC005P": "Sicurezza",
    "07SIC006P": "Sicurezza",
}

estratto["area"] = estratto["CODICE"].map(area_per_codice)
estratto["verso"] = estratto["area"].map({"Ambiente": "+", "Sicurezza": "-"})

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
print("Valori mancanti:", estratto["valore"].isna().sum())

print(estratto.head(3).to_string(index=False))
print("Dimensioni:", estratto.shape)
print("Duplicati provincia-indicatore:",
      estratto.duplicated(["provincia_id", "indicatore_id"]).sum())


cartella = Path("data/estratti")
cartella.mkdir(parents=True, exist_ok=True)

percorso_csv = cartella / "ambiente_sicurezza.csv"
estratto.to_csv(percorso_csv, index=False)

print("CSV salvato in:", percorso_csv)