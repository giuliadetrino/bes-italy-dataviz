
import pandas as pd
from pathlib import Path
from lettura_istat import leggi_istat

# https://www.youtube.com/watch?v=3TNpOD6bov8

# Codici ufficiali ISTAT degli indicatori assegnati
indicatori_scelti = {
    "01SAL001": ("Salute", "+"),
    "02IST003P-N22": ("Istruzione e formazione", "+"),
    "02IST006-N22": ("Istruzione e formazione", "-"),
}

dati, metadati = leggi_istat()

# Seleziona i tre indicatori
estratto = dati.loc[
    dati["CODICE"].isin(indicatori_scelti)
].copy()

# Converte i valori ISTAT in numeri
valori = estratto["V2023"].replace("....", pd.NA)
valori = valori.str.replace(",", ".", regex=False)
estratto["valore"] = pd.to_numeric(valori, errors="coerce")

# Assegna macroarea e direzione
estratto["area"] = estratto["CODICE"].map({
    codice: area
    for codice, (area, verso) in indicatori_scelti.items()
})

estratto["verso"] = estratto["CODICE"].map({
    codice: verso
    for codice, (area, verso) in indicatori_scelti.items()
})

# Rinomina le colonne secondo lo schema comune
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

# Controlli di qualità
numero_indicatori = estratto["indicatore_id"].nunique()
numero_province = estratto["provincia_id"].nunique()
duplicati = estratto.duplicated(
    ["provincia_id", "indicatore_id"]
).sum()
mancanti = estratto["valore"].isna().sum()

print("Indicatori distinti:", numero_indicatori)
print("Province:", numero_province)
print("Anni presenti:", estratto["anno"].unique().tolist())
print("Valori mancanti:", mancanti)
print("Duplicati provincia-indicatore:", duplicati)
print("Dimensioni:", estratto.shape)
print(estratto.head(4).to_string(index=False))

assert numero_indicatori == 3
assert numero_province == 107
assert duplicati == 0
assert set(estratto["anno"]) == {2023}
assert len(estratto) == 321

# Salva il CSV
cartella = Path("data/estratti")
cartella.mkdir(parents=True, exist_ok=True)

percorso_csv = cartella / "salute_istruzione.csv"
estratto.to_csv(percorso_csv, index=False)

print("CSV salvato in:", percorso_csv)
