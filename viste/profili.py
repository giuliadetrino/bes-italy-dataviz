import pandas as pd
import plotly.graph_objects as go

COLORE_PROVINCIA_A = "#138A8A"   # stesso verde acqua di classifica.py e spostamenti.py
COLORE_PROVINCIA_B = "#F59E0B"   # stesso arancio di classifica.py e spostamenti.py
COLORE_LINEA = "#9CA3AF"         # stesso grigio di spostamenti.py

AREE_ORDINATE = [
    "Salute",
    "Istruzione e formazione",
    "Lavoro",
    "Economia",
    "Ambiente",
    "Servizi",
    "Sicurezza",
]


def _formatta_valori_originali(
    df_indicatori: pd.DataFrame | None,
    provincia: str,
    area: str,
) -> str:
    """
    Costruisce il testo HTML per il tooltip con i valori originali ISTAT e le unità.
    Se df_indicatori non è fornito o non contiene dati per l'area, restituisce un avviso.
    """
    if df_indicatori is None or df_indicatori.empty:
        return "Valori originali non disponibili"

    colonne_richieste = {"provincia", "area", "valore", "unita"}
    mancanti = colonne_richieste - set(df_indicatori.columns)
    if mancanti:
        raise ValueError(f"Colonne mancanti in df_indicatori: {mancanti}")

    sottoinsieme = df_indicatori[
        (df_indicatori["provincia"] == provincia) & (df_indicatori["area"] == area)
    ]
    if sottoinsieme.empty:
        return "Nessun indicatore originale disponibile"

    righe = []
    for _, riga in sottoinsieme.iterrows():
        nome = riga.get("indicatore", riga.get("indicatore_id", "Indicatore"))
        valore = riga["valore"]
        unita = riga["unita"]
        if pd.isna(valore):
            righe.append(f"• {nome}: dato mancante ({unita})")
        else:
            righe.append(f"• {nome}: {float(valore):.2f} ({unita})")

    return "<br>".join(righe)


def _valida_profilo_provincia(df_prov: pd.DataFrame, provincia: str) -> pd.Series:
    """
    Verifica che la provincia sia presente, abbia tutte e sette le macroaree
    senza duplicati e che tutti i punteggi siano compresi tra 0 e 100.
    Restituisce una Series indicizzata per area.
    """
    if df_prov.empty:
        raise ValueError(f"Provincia non trovata in df_aree: {provincia}")

    if df_prov["area"].duplicated().any():
        raise ValueError(f"Aree duplicate trovate per la provincia: {provincia}")

    aree_mancanti = set(AREE_ORDINATE) - set(df_prov["area"])
    if aree_mancanti:
        raise ValueError(
            f"Macroaree mancanti per {provincia}: {sorted(aree_mancanti)}"
        )

    serie = df_prov.set_index("area").loc[AREE_ORDINATE, "punteggio_area"]

    if serie.isna().any() or (serie < 0).any() or (serie > 100).any():
        raise ValueError(
            f"I punteggi di {provincia} devono essere compresi tra 0 e 100."
        )

    return serie


def crea_profili(
    df_aree: pd.DataFrame,
    provincia_a: str,
    provincia_b: str,
    df_indicatori: pd.DataFrame | None = None,
) -> go.Figure:
    """
    Disegna il profilo di due province sulle sette aree di benessere in scala 0-100
    tramite un grafico a punti collegati (dumbbell plot).
    Al passaggio del mouse rende consultabili i valori originali ISTAT e le unità.

    df_aree deve contenere: provincia, area, punteggio_area.
    df_indicatori (opzionale) deve contenere: provincia, area, valore, unita
    (e opzionalmente indicatore o indicatore_id).
    """
    mancanti = {"provincia", "area", "punteggio_area"} - set(df_aree.columns)
    if mancanti:
        raise ValueError(f"Colonne mancanti in df_aree: {mancanti}")

    serie_a = _valida_profilo_provincia(
        df_aree[df_aree["provincia"] == provincia_a], provincia_a
    )
    serie_b = _valida_profilo_provincia(
        df_aree[df_aree["provincia"] == provincia_b], provincia_b
    )

    punteggi_a = [float(serie_a[a]) for a in AREE_ORDINATE]
    punteggi_b = [float(serie_b[a]) for a in AREE_ORDINATE]

    dettagli_a = [_formatta_valori_originali(df_indicatori, provincia_a, a) for a in AREE_ORDINATE]
    dettagli_b = [_formatta_valori_originali(df_indicatori, provincia_b, a) for a in AREE_ORDINATE]

    figura = go.Figure()

    # Linee grigie che collegano i due punti su ciascuna area
    for area, x0, x1 in zip(AREE_ORDINATE, punteggi_a, punteggi_b):
        figura.add_trace(
            go.Scatter(
                x=[x0, x1],
                y=[area, area],
                mode="lines",
                line=dict(color=COLORE_LINEA, width=2.5),
                hoverinfo="skip",
                showlegend=False,
            )
        )

    # Serie Provincia A (verde acqua)
    figura.add_trace(
        go.Scatter(
            x=punteggi_a,
            y=AREE_ORDINATE,
            mode="markers",
            name=provincia_a,
            marker=dict(color=COLORE_PROVINCIA_A, size=12, line=dict(color="white", width=1.5)),
            customdata=dettagli_a,
            hovertemplate=(
                f"<b>{provincia_a}</b> — %{{y}}<br>"
                "Punteggio area: <b>%{x:.1f} / 100</b><br>"
                "%{customdata}<extra></extra>"
            ),
        )
    )

    # Serie Provincia B (arancio)
    figura.add_trace(
        go.Scatter(
            x=punteggi_b,
            y=AREE_ORDINATE,
            mode="markers",
            name=provincia_b,
            marker=dict(color=COLORE_PROVINCIA_B, size=12, line=dict(color="white", width=1.5)),
            customdata=dettagli_b,
            hovertemplate=(
                f"<b>{provincia_b}</b> — %{{y}}<br>"
                "Punteggio area: <b>%{x:.1f} / 100</b><br>"
                "%{customdata}<extra></extra>"
            ),
        )
    )

    figura.update_layout(
        title=f"Confronto profili per area: {provincia_a} vs {provincia_b}",
        xaxis=dict(title="Punteggio normalizzato (scala 0–100)", range=[-3, 103], dtick=10),
        yaxis=dict(title="", autorange="reversed"),
        template="plotly_white",
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=170, r=30, t=90, b=50),
    )
    return figura


if __name__ == "__main__":
    # Piccoli dati di prova in memoria (dal 21 arrivano i dati reali da app.py)
    aree = AREE_ORDINATE
    dati_aree = pd.DataFrame([
        *[{"provincia": "Provincia A", "area": a, "punteggio_area": v}
          for a, v in zip(aree, [82.0, 88.5, 79.0, 84.0, 68.0, 76.5, 34.0])],
        *[{"provincia": "Provincia B", "area": a, "punteggio_area": v}
          for a, v in zip(aree, [91.0, 77.0, 83.5, 75.0, 89.0, 72.0, 81.5])],
    ])

    dati_indicatori = pd.DataFrame([
        {"provincia": "Provincia A", "area": "Salute", "indicatore": "Speranza di vita", "valore": 83.8, "unita": "anni"},
        {"provincia": "Provincia B", "area": "Salute", "indicatore": "Speranza di vita", "valore": 84.4, "unita": "anni"},
        {"provincia": "Provincia A", "area": "Lavoro", "indicatore": "Occupazione 20–64 anni", "valore": 74.2, "unita": "Valori percentuali"},
        {"provincia": "Provincia B", "area": "Lavoro", "indicatore": "Occupazione 20–64 anni", "valore": 75.6, "unita": "Valori percentuali"},
    ])

    figura = crea_profili(dati_aree, "Provincia A", "Provincia B", df_indicatori=dati_indicatori)

    # Verifica requisiti: 7 linee + 2 serie = 9 tracce, stessa scala 0-100
    assert len(figura.data) == 9
    assert figura.layout.xaxis.range == (-3, 103)
    print("Figura creata:", type(figura).__name__, "con", len(figura.data), "tracce")
    print("Scala asse X:", figura.layout.xaxis.range)
    print("Verifica OK")
