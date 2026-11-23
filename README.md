# bes-italy-dataviz

An interactive Streamlit dashboard for comparing well-being across Italian provinces using 14 indicators from ISTAT. Select a province, adjust the weights assigned to seven dimensions of well-being, and explore how its score and ranking change.

The seven dimensions are **Health, Education, Employment, Economy, Environment, Services, and Safety**.

## Dashboard views

| View | What you can explore |
|---|---|
| **Province ranking** | Highlight a province and see its score and position under the selected weights. |
| **Province profiles** | Compare two provinces across all seven dimensions and inspect the original indicator values. |
| **Ranking changes** | See how many positions each province gains or loses compared with the equal-weight ranking. |

## Team contributions

| Team member | Contribution |
|---|---|
| **Giulia De trino** | Extracted the environment and safety indicators. Integrated the calculation modules and the three views into the Streamlit dashboard, added the seven weight controls, and documented how to rebuild the dataset and run the app. |
| **Anna Luna Orso** | Extracted the health and education indicators. Manually checked the NEET normalization, Education score, and equal-weight composite index for Turin and documented the calculations. |
| **Federico** | Extracted the two employment indicators used in the dashboard, covering the employment rates for people aged 20–64 and 15–29. |
| **Giovanni** | Extracted the economy and services indicators. Checked that province identifiers in his extract matched those in the environment and safety extract so the datasets could be joined by province. |

## Data source

The project uses the **2025 edition of ISTAT BES dei Territori**, with **2023** as the reference year. The source data cover 107 provinces. The composite ranking includes the 105 provinces with complete scores across all seven dimensions.

| Source file | Contents |
|---|---|
| `data/raw/Indicatori_per_provincia_sesso_ed.2025.xlsx` | Provincial indicator values used to extract the 2023 observations. |
| `data/raw/Metadati_IT_ed.2025.xlsx` | Indicator descriptions and units of measurement. |

## Run the dashboard locally

The commands below are for **Windows PowerShell**. After cloning the repository, open PowerShell in the `bes-italy-dataviz` folder containing `app.py` and `requirements.txt`. Run all commands from that folder.

### 1. Set up the Python environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Rebuild the 2023 dataset

Check that both Excel workbooks listed under **Data source** are present in `data/raw/`. Run the four extraction scripts, then combine their outputs:

```powershell
python src/salute_istruzione.py
python src/lavoro.py
python src/economia_servizi.py
python src/ambiente_sicurezza.py
python src/prepara_dataset.py
```

The combined dataset is saved to `data/elaborati/bes_2023.csv`.

### 3. Launch the dashboard

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal. Select a province in the ranking and move a weight slider to see how its score and position change. At least one weight must be positive. Restoring equal weights returns the dashboard to the baseline ranking.

## Manual validation — Turin (2023)

Anna Luna Orso checked three stages of the calculation for **Torino (Turin)**, ISTAT code `01-01-001`.

### 1. NEET indicator normalization

The NEET indicator (`02IST006-N22`) measures the percentage of young people who are not in employment, education, or training. A lower rate corresponds to a higher normalized score.

| Value used in the calculation | NEET rate |
|---|---:|
| Turin | 12.0% |
| Minimum in the dataset | 5.2% |
| Maximum in the dataset | 33.8% |

```text
NEET score = 100 × (maximum − Turin rate) / (maximum − minimum)
           = 100 × (33.8 − 12.0) / (33.8 − 5.2)
           ≈ 76.223776
```

The manual result matched the normalized score produced by Python to six decimal places.

### 2. Education area score

The Education score is the arithmetic mean of two normalized indicator scores.

| Education indicator | Normalized score for Turin |
|---|---:|
| Tertiary education among people aged 25–39 | 58.974359 |
| Young people not in employment, education, or training | 76.223776 |

```text
Education score = (58.974359 + 76.223776) / 2
                ≈ 67.599068
```

### 3. Equal-weight composite index

With equal weights, each area contributes one seventh of the composite index. The area scores below are displayed to six decimal places.

| Area | Normalized score for Turin |
|---|---:|
| Health | 65.789474 |
| Education | 67.599068 |
| Employment | 66.176994 |
| Economy | 58.897396 |
| Environment | 27.342761 |
| Services | 55.820228 |
| Safety | 45.557236 |

The manual index was compared with the output of `calcola_punteggi_aree()` and `calcola_indice()` in `src/indice.py`. The Python calculation used the `punteggio` column from `data/elaborati/bes_2023_normalizzato.csv`, seven equal weights, and `solo_complete=True`.

| Measure | Result |
|---|---:|
| Manual composite index | 55.311879 |
| Python composite index | 55.311879 |
| Absolute difference | < 0.00001 |

**Result: passed.** The two calculations agreed within the specified tolerance.

## Final verification

### Education-only scenario

Education was set to **100** and all six other weights to **0**. With these settings, each province’s composite index equals its Education score.

| Check | Result |
|---|---|
| Turin’s displayed index | **Passed.** The dashboard displayed **67.60**, matching the manually calculated Education score of **67.599068** rounded to two decimal places. |
| Province ranking | **Passed.** The dashboard ranking matched the descending order of Education scores for all 105 eligible provinces. |

### Province profiles and ranking changes

| Check | Result |
|---|---|
| Province profiles | **Passed.** The indicator values displayed for the two selected provinces matched their 2023 source data. |
| Ranking changes | **Passed.** The displayed gain or loss matched `initial position − updated position`. A move from 10th to 7th corresponds to a gain of `+3`. |
| Equal-weight reset | **Passed.** After equal weights were restored, every province showed a change of `0` positions. |

### Reproducibility on a second computer

**Passed.** Starting from a fresh clone on a second computer, the team regenerated the dataset and successfully opened all three dashboard views.