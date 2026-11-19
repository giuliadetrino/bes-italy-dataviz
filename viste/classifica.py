
import pandas as pd
import plotly.graph_objects as go

# https://www.youtube.com/watch?v=3TNpOD6bov8


def crea_classifica(df: pd.DataFrame, provincia_selezionata: str | None = None) -> go.Figure:
    """
    Crea una classifica orizzontale delle province.

    Il DataFrame deve contenere:
    provincia, indice, posizione.

    Restituisce una figura Plotly.
    """

    colonne = {"provincia", "indice", "posizione"}

    if not colonne.issubset(df.columns):
        raise ValueError(
            f"Colonne mancanti: {colonne - set(df.columns)}"
        )

    dati = df.copy()
    dati = dati.sort_values(
        ["posizione", "provincia"],
        ascending=[True, True]
    )

    colori = [
        "#F59E0B" if provincia == provincia_selezionata else "#138A8A"
        for provincia in dati["provincia"]
    ]

    etichette = [
        f"{int(posizione)}° {provincia}"
        for provincia, posizione in zip(
            dati["provincia"], dati["posizione"]
        )
    ]

    figura = go.Figure()

    figura.add_trace(
        go.Bar(
            x=dati["indice"],
            y=etichette,
            orientation="h",
            marker_color=colori,
            customdata=dati["provincia"],
            hovertemplate=(
                "<b>%{customdata}</b>"
                "<br>Indice: %{x:.2f}"
                "<extra></extra>"
            ),
        )
    )

    figura.update_layout(
        title="Classifica delle province italiane",
        xaxis_title="Indice di benessere (0–100)",
        yaxis_title="",
        yaxis=dict(autorange="reversed"),
        xaxis=dict(range=[0, 100]),
        template="plotly_white",
        height=max(450, len(dati) * 24),
        showlegend=False,
        margin=dict(l=150, r=30, t=70, b=50),
    )

    return figura
