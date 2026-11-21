from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from src.indice import AREE_ATTESE, calcola_indice, calcola_punteggi_aree
from src.normalizzazione import normalizza_indicatori
from src.posizioni import calcola_posizioni
from viste.classifica import crea_classifica
from viste.profili import crea_profili
from viste.spostamenti import crea_spostamenti


CSV_PATH = Path(__file__).resolve().parent / "data" / "elaborati" / "bes_2023.csv"

AREA_LABELS = {
    "Salute": "Health",
    "Istruzione e formazione": "Education and training",
    "Lavoro": "Employment",
    "Economia": "Economic well-being",
    "Ambiente": "Environment",
    "Servizi": "Services",
    "Sicurezza": "Safety",
}

UNIT_LABELS = {
    "Numero medio di anni": "years, on average",
    "Valori percentuali": "%",
    "Euro": "EUR",
    "Per 100.000 abitanti": "per 100,000 residents",
    "M2 per abitante": "m² per resident",
    "Per 10.000 abitanti": "per 10,000 residents",
}


@st.cache_data
def prepare_baseline(csv_contents: bytes):
    indicators = pd.read_csv(
        BytesIO(csv_contents),
        dtype={"provincia_id": str},
    )

    normalized = normalizza_indicatori(indicators)
    area_scores = calcola_punteggi_aree(
        normalized,
        colonna_punteggio="punteggio",
    )

    equal_weights = dict.fromkeys(AREE_ATTESE, 1)
    baseline = calcola_posizioni(calcola_indice(area_scores, equal_weights))

    # Units are translated only for display in the profile tooltips.
    display_indicators = indicators.copy()
    display_indicators["unita"] = display_indicators["unita"].replace(UNIT_LABELS)

    return display_indicators, area_scores, baseline


def ranking_chart(ranking, selected_province):
    figure = crea_classifica(ranking, selected_province)
    bars = figure.data[0]

    # Keep the ranking order and ties supplied by the project module.
    bars.y = [label.replace("° ", ". ", 1) for label in bars.y]
    bars.hovertemplate = (
        "<b>%{customdata}</b><br>"
        "Well-being index: %{x:.2f}<extra></extra>"
    )

    figure.update_layout(
        title="Provincial well-being ranking",
        xaxis_title="Well-being index (0–100)",
    )
    return figure


def profile_chart(area_scores, first_province, second_province, indicators):
    figure = crea_profili(
        area_scores,
        first_province,
        second_province,
        df_indicatori=indicators,
    )

    for trace in figure.data:
        # Translate both the connecting lines and the markers so they align.
        trace.y = [AREA_LABELS[area] for area in trace.y]

        if trace.mode == "markers":
            trace.hovertemplate = (
                "<b>%{fullData.name}</b> — %{y}<br>"
                "Area score: <b>%{x:.1f} / 100</b><br>"
                "%{customdata}<extra></extra>"
            )
            trace.customdata = [
                detail.replace("dato mancante", "missing value")
                .replace("Valori originali non disponibili", "Original values unavailable")
                .replace("Nessun indicatore originale disponibile", "No original indicator available")
                for detail in trace.customdata
            ]

    figure.update_layout(
        title=f"Well-being profiles: {first_province} and {second_province}",
        xaxis_title="Area score (0–100)",
    )
    return figure


def rank_change_chart(baseline, current, selected_province):
    figure = crea_spostamenti(baseline, current, selected_province)

    legend_labels = {
        "Pesi uguali": "Equal weights",
        "Pesi scelti": "Selected weights",
    }

    for trace in figure.data:
        if trace.name in legend_labels:
            trace.name = legend_labels[trace.name]
            trace.hovertemplate = (
                "<b>%{customdata[0]}</b><br>"
                "Rank with equal weights: %{customdata[1]}<br>"
                "Rank with selected weights: %{customdata[2]}<br>"
                "Positions gained or lost: %{customdata[3]}<extra></extra>"
            )

    figure.update_layout(
        title="Rank changes from equal to selected weights",
        xaxis_title="Rank (1 = highest)",
    )
    return figure


def main():
    st.set_page_config(
        page_title="Well-being across Italian provinces",
        layout="wide",
    )
    st.title("Well-being across Italian provinces")

    st.sidebar.header("Weights by area")
    st.sidebar.caption(
        "With equal weights, each area contributes one seventh of the index. "
        "Increase a weight to give that area more influence."
    )

    weights = {}
    for area in AREE_ATTESE:
        weights[area] = st.sidebar.slider(
            AREA_LABELS[area],
            min_value=0,
            max_value=100,
            value=10,
            key=f"weight_{area}",
        )

    if sum(weights.values()) == 0:
        st.warning("Set at least one weight above zero to calculate the ranking.")
        st.stop()

    indicators, area_scores, baseline = prepare_baseline(CSV_PATH.read_bytes())
    current = calcola_posizioni(calcola_indice(area_scores, weights))
    provinces = sorted(current["provincia"])

    st.caption(
        f"ISTAT BES 2023 · {len(provinces)} of "
        f"{indicators['provincia_id'].nunique()} provinces have complete data "
        "across all seven areas."
    )

    ranking_tab, profiles_tab, changes_tab = st.tabs(
        ["Ranking", "Province profiles", "Rank changes"]
    )

    with ranking_tab:
        selected = st.selectbox("Province to highlight", provinces)
        st.plotly_chart(ranking_chart(current, selected))

    with profiles_tab:
        left, right = st.columns(2)
        first = left.selectbox("First province", provinces)
        second = right.selectbox("Second province", provinces, index=1)
        st.plotly_chart(profile_chart(area_scores, first, second, indicators))

    with changes_tab:
        st.caption(
            "A positive value means the province moved up the ranking. "
            "For example, moving from 8th to 5th is a gain of 3 places."
        )
        st.plotly_chart(rank_change_chart(baseline, current, selected))


if __name__ == "__main__":
    main()