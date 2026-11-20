import pandas as pd
import plotly.graph_objects as go

COLORE_INIZIALE = "#9CA3AF"   # grigio: pesi uguali
COLORE_GUADAGNO = "#138A8A"   # stesso verde acqua di classifica.py
COLORE_PERDITA = "#F59E0B"    # stesso arancio di classifica.py
COLORE_STABILE = "#6B7280"


def calcola_spostamenti(iniziale: pd.DataFrame, aggiornata: pd.DataFrame) -> pd.DataFrame:
    """
    Unisce le due classifiche e calcola lo spostamento di ogni provincia.

    Entrambi i DataFrame devono contenere: provincia, posizione.
    - iniziale: classifica con i sette pesi uguali
    - aggiornata: classifica con i pesi scelti negli slider

    guadagno = posizione iniziale - posizione aggiornata
    (dal posto 8 al 5 -> +3; positivo = sale in classifica).
    """
    for nome, df in {"iniziale": iniziale, "aggiornata": aggiornata}.items():
        mancanti = {"provincia", "posizione"} - set(df.columns)
        if mancanti:
            raise ValueError(f"Colonne mancanti in {nome}: {mancanti}")

    dati = iniziale[["provincia", "posizione"]].merge(
        aggiornata[["provincia", "posizione"]],
        on="provincia",
        how="inner",
        suffixes=("_iniziale", "_aggiornata"),
        validate="one_to_one",
    )
    if len(dati) != len(iniziale) or len(dati) != len(aggiornata):
        raise ValueError("Le due classifiche non contengono le stesse province.")

    dati["guadagno"] = dati["posizione_iniziale"] - dati["posizione_aggiornata"]
    return dati.sort_values(["posizione_aggiornata", "provincia"]).reset_index(drop=True)


def crea_spostamenti(
    iniziale: pd.DataFrame,
    aggiornata: pd.DataFrame,
    provincia_selezionata: str | None = None,
) -> go.Figure:
    """
    Per ogni provincia disegna due punti collegati da una linea:
    grigio = posizione a pesi uguali, colorato = posizione con i pesi scelti.
    Il colore indica se la provincia sale (verde acqua) o scende (arancio).

    Restituisce una figura Plotly, ordinata per posizione aggiornata.
    """
    dati = calcola_spostamenti(iniziale, aggiornata)

    etichette = [
        f"<b>{p}</b>" if p == provincia_selezionata else p
        for p in dati["provincia"]
    ]
    colori = [
        COLORE_GUADAGNO if g > 0 else COLORE_PERDITA if g < 0 else COLORE_STABILE
        for g in dati["guadagno"]
    ]
    testo_guadagno = [f"{g:+d}" if g != 0 else "0" for g in dati["guadagno"]]

    figura = go.Figure()

    # linee che collegano i due punti di ogni provincia
    for y, x0, x1, colore in zip(
        etichette, dati["posizione_iniziale"], dati["posizione_aggiornata"], colori
    ):
        figura.add_trace(
            go.Scatter(
                x=[x0, x1], y=[y, y], mode="lines",
                line=dict(color=colore, width=2),
                hoverinfo="skip", showlegend=False,
            )
        )

    dettagli = dati[["provincia", "posizione_iniziale", "posizione_aggiornata"]].assign(
        guadagno=testo_guadagno
    )

    figura.add_trace(
        go.Scatter(
            x=dati["posizione_iniziale"], y=etichette, mode="markers",
            name="Pesi uguali",
            marker=dict(color=COLORE_INIZIALE, size=9),
            customdata=dettagli,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Pesi uguali: %{customdata[1]}°"
                "<br>Pesi scelti: %{customdata[2]}°<br>Spostamento: %{customdata[3]}"
                "<extra></extra>"
            ),
        )
    )
    figura.add_trace(
        go.Scatter(
            x=dati["posizione_aggiornata"], y=etichette, mode="markers+text",
            name="Pesi scelti",
            marker=dict(color=colori, size=11, line=dict(color="white", width=1)),
            text=testo_guadagno,
            # l'asse va da destra (1°) a sinistra: chi scende ha l'etichetta a sinistra
            textposition=["middle left" if g < 0 else "middle right" for g in dati["guadagno"]],
            textfont=dict(color=colori, size=11),
            customdata=dettagli,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>Pesi uguali: %{customdata[1]}°"
                "<br>Pesi scelti: %{customdata[2]}°<br>Spostamento: %{customdata[3]}"
                "<extra></extra>"
            ),
        )
    )

    n = int(max(dati["posizione_iniziale"].max(), dati["posizione_aggiornata"].max()))
    figura.update_layout(
        title="Spostamenti in classifica: pesi uguali → pesi scelti",
        xaxis=dict(title="Posizione (1 = migliore)", range=[n + 1.5, 0], dtick=max(1, n // 20)),
        yaxis=dict(title="", autorange="reversed"),
        template="plotly_white",
        height=max(450, len(dati) * 24),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(l=150, r=30, t=90, b=50),
    )
    return figura


if __name__ == "__main__":
    # Piccoli dati di prova in memoria (dal 21 arrivano le classifiche reali da app.py)
    province = [f"Provincia {c}" for c in "ABCDEFGHIJ"]
    iniziale = pd.DataFrame({"provincia": province, "posizione": range(1, 11)})

    # Pesi scelti: H passa dall'8° al 5° posto, le altre scalano
    nuova = ["A", "B", "C", "D", "H", "E", "F", "G", "I", "J"]
    aggiornata = pd.DataFrame({
        "provincia": [f"Provincia {c}" for c in nuova],
        "posizione": range(1, 11),
    })

    sp = calcola_spostamenti(iniziale, aggiornata)
    h = sp.loc[sp["provincia"] == "Provincia H", "guadagno"].item()
    print("Provincia H: dal posto 8 al 5, guadagno =", h)
    assert h == 3

    uguali = calcola_spostamenti(iniziale, iniziale)
    print("A pesi uguali, spostamenti diversi da zero:", (uguali["guadagno"] != 0).sum())
    assert (uguali["guadagno"] == 0).all()

    # Ex aequo (1, 1, 3) accettati senza errori
    pari = pd.DataFrame({"provincia": province[:3], "posizione": [1, 1, 3]})
    print(calcola_spostamenti(pari, pari)[["provincia", "guadagno"]].to_string(index=False))

    figura = crea_spostamenti(iniziale, aggiornata, provincia_selezionata="Provincia H")
    print("Figura creata:", type(figura).__name__, "con", len(figura.data), "tracce")
    print("Verifica OK")
