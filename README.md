# bes-italy-dataviz

An interactive Streamlit dashboard for comparing well-being across Italian provinces. It uses 14 indicators from the 2025 edition of **ISTAT BES dei Territori**, with 2023 as the reference year.

Users can assign weights to seven dimensions of well-being: **Health, Education, Employment, Economy, Environment, Services, and Safety**.

## Dashboard views

| View | What you can explore |
|---|---|
| **Province ranking** | See how provinces rank under the selected weights and highlight a province of interest. |
| **Province profiles** | Compare two provinces across the seven dimensions and inspect the original indicator values. |
| **Ranking changes** | See how many positions each province gains or loses relative to the equal-weight ranking. |

## Run the dashboard locally# bes-italy-dataviz

An interactive Streamlit dashboard for comparing well-being across Italian provinces. It uses 14 indicators from the 2025 edition of **ISTAT BES dei Territori**, with 2023 as the reference year.

Users can assign weights to seven dimensions of well-being: **Health, Education, Employment, Economy, Environment, Services, and Safety**.

## Dashboard views

| View | What you can explore |
|---|---|
| **Province ranking** | See how provinces rank under the selected weights and highlight a province of interest. |
| **Province profiles** | Compare two provinces across the seven dimensions and inspect the original indicator values. |
| **Ranking changes** | See how many positions each province gains or loses relative to the equal-weight ranking. |

## Run the dashboard locally

The following commands are for **Windows PowerShell**. After cloning the repository, open PowerShell in the `bes-italy-dataviz` folder containing `app.py` and `requirements.txt`. Run all commands from that folder.

### 1. Install the dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Check the source files

The project uses the following two Excel workbooks. Before running the extraction scripts, check that both files are present at these paths:

```text
data/raw/Indicatori_per_provincia_sesso_ed.2025.xlsx
data/raw/Metadati_IT_ed.2025.xlsx
```

The first workbook contains the indicator values. The second contains the indicator metadata.

### 3. Rebuild the 2023 dataset

Run the four extraction scripts, then combine their outputs:

```powershell
python src/salute_istruzione.py
python src/lavoro.py
python src/economia_servizi.py
python src/ambiente_sicurezza.py
python src/prepara_dataset.py
```

The combined dataset used by the dashboard is `data/elaborati/bes_2023.csv`.

### 4. Launch the dashboard

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal. Adjust the seven weights to explore different scenarios. At least one weight must be positive for the dashboard to calculate the index.

## Manual validation — Turin (2023)

| Setting | Value |
|---|---|
| Province | Torino (Turin) |
| ISTAT code | `01-01-001` |
| Reference year | 2023 |
| Data source | ISTAT BES dei Territori, 2025 edition |
| Weighting scenario | Equal weights across all seven dimensions |

### 1. NEET indicator normalization

The NEET indicator (`02IST006-N22`) measures the percentage of young people who are not in employment, education, or training. A lower percentage represents a better outcome, so the normalization assigns a higher score to a lower rate.

| Value used in the calculation | NEET rate |
|---|---:|
| Turin | 12.0% |
| Minimum in the dataset | 5.2% |
| Maximum in the dataset | 33.8% |

```text
NEET score = 100 × (maximum − Turin rate) / (maximum − minimum)
           = 100 × (33.8 − 12.0) / (33.8 − 5.2)
           = 76.223776
```

The manual result matches the normalized score produced by Python to six decimal places.

### 2. Education area score

The Education score is the arithmetic mean of two normalized indicator scores.

| Education indicator | Normalized score for Turin |
|---|---:|
| Tertiary education (ages 25–39) | 58.974359 |
| Young people not in employment, education, or training | 76.223776 |

```text
Education score = (58.974359 + 76.223776) / 2
                ≈ 67.599068
```

### 3. Composite well-being index

With equal weights, each of the seven area scores contributes one seventh of the composite index.

| Area | Normalized score for Turin |
|---|---:|
| Health | 65.789474 |
| Education | 67.599068 |
| Employment | 66.176994 |
| Economy | 58.897396 |
| Environment | 27.342761 |
| Services | 55.820228 |
| Safety | 45.557236 |

The manual calculation gave a composite index of **55.311879**. The area scores in the table are displayed to six decimal places.

### 4. Comparison with Python

The manual result was compared with the output of `calcola_punteggi_aree()` and `calcola_indice()` from `src/indice.py`. The calculation used the `punteggio` column from `data/elaborati/bes_2023_normalizzato.csv`, seven equal weights, and `solo_complete=True`.

| Measure | Result |
|---|---:|
| Manual index | 55.311879 |
| Python index | 55.311879 |
| Absolute difference | < 0.00001 |

**Result: passed.** The manual calculation and the Python implementation agree within the specified tolerance for Turin under equal weights.

Validation performed by Anna Luna Orso.

## Final verification

### Education-only scenario

Set **Education to 100** and the other six weights to **0**. In this scenario, each province’s composite index should equal its Education score, and the ranking should follow Education scores in descending order.

For Turin, the expected index is **67.599068**, or **67.60** when displayed to two decimal places.

| Check | Result |
|---|---|
| Turin index observed in the dashboard | 67.60 — matches the expected Education score rounded to two decimal places. |
| Ranking checked against Education scores | Passed — the dashboard ranking matched the descending order of the mean Education scores for all 105 eligible provinces. |

Restore equal weights after the check.

### Profile values and ranking changes

| Check | Result |
|---|---|
| Province profiles | Passed — the displayed values for the two selected provinces matched the 2023 source data. |
| Ranking changes | Passed — the displayed changes matched the differences between the initial and updated positions. |
| Equal-weight reset | Passed — all provinces showed a change of 0 after equal weights were restored. |

### Reproduce the project on a second computer

Passed — dataset regenerated and all three dashboard views opened successfully.# bes-italy-dataviz

An interactive Streamlit dashboard for comparing well-being across Italian provinces. It uses 14 indicators from the 2025 edition of **ISTAT BES dei Territori**, with 2023 as the reference year.

Users can assign weights to seven dimensions of well-being: **Health, Education, Employment, Economy, Environment, Services, and Safety**.

## Dashboard views

| View | What you can explore |
|---|---|
| **Province ranking** | See how provinces rank under the selected weights and highlight a province of interest. |
| **Province profiles** | Compare two provinces across the seven dimensions and inspect the original indicator values. |
| **Ranking changes** | See how many positions each province gains or loses relative to the equal-weight ranking. |

## Run the dashboard locally

The following commands are for **Windows PowerShell**. After cloning the repository, open PowerShell in the `bes-italy-dataviz` folder containing `app.py` and `requirements.txt`. Run all commands from that folder.

### 1. Install the dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Check the source files

The project uses the following two Excel workbooks. Before running the extraction scripts, check that both files are present at these paths:

```text
data/raw/Indicatori_per_provincia_sesso_ed.2025.xlsx
data/raw/Metadati_IT_ed.2025.xlsx
```

The first workbook contains the indicator values. The second contains the indicator metadata.

### 3. Rebuild the 2023 dataset

Run the four extraction scripts, then combine their outputs:

```powershell
python src/salute_istruzione.py
python src/lavoro.py
python src/economia_servizi.py
python src/ambiente_sicurezza.py
python src/prepara_dataset.py
```

The combined dataset used by the dashboard is `data/elaborati/bes_2023.csv`.

### 4. Launch the dashboard

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal. Adjust the seven weights to explore different scenarios. At least one weight must be positive for the dashboard to calculate the index.

## Manual validation — Turin (2023)

| Setting | Value |
|---|---|
| Province | Torino (Turin) |
| ISTAT code | `01-01-001` |
| Reference year | 2023 |
| Data source | ISTAT BES dei Territori, 2025 edition |
| Weighting scenario | Equal weights across all seven dimensions |

### 1. NEET indicator normalization

The NEET indicator (`02IST006-N22`) measures the percentage of young people who are not in employment, education, or training. A lower percentage represents a better outcome, so the normalization assigns a higher score to a lower rate.

| Value used in the calculation | NEET rate |
|---|---:|
| Turin | 12.0% |
| Minimum in the dataset | 5.2% |
| Maximum in the dataset | 33.8% |

```text
NEET score = 100 × (maximum − Turin rate) / (maximum − minimum)
           = 100 × (33.8 − 12.0) / (33.8 − 5.2)
           = 76.223776
```

The manual result matches the normalized score produced by Python to six decimal places.

### 2. Education area score

The Education score is the arithmetic mean of two normalized indicator scores.

| Education indicator | Normalized score for Turin |
|---|---:|
| Tertiary education (ages 25–39) | 58.974359 |
| Young people not in employment, education, or training | 76.223776 |

```text
Education score = (58.974359 + 76.223776) / 2
                ≈ 67.599068
```

### 3. Composite well-being index

With equal weights, each of the seven area scores contributes one seventh of the composite index.

| Area | Normalized score for Turin |
|---|---:|
| Health | 65.789474 |
| Education | 67.599068 |
| Employment | 66.176994 |
| Economy | 58.897396 |
| Environment | 27.342761 |
| Services | 55.820228 |
| Safety | 45.557236 |

The manual calculation gave a composite index of **55.311879**. The area scores in the table are displayed to six decimal places.

### 4. Comparison with Python

The manual result was compared with the output of `calcola_punteggi_aree()` and `calcola_indice()` from `src/indice.py`. The calculation used the `punteggio` column from `data/elaborati/bes_2023_normalizzato.csv`, seven equal weights, and `solo_complete=True`.

| Measure | Result |
|---|---:|
| Manual index | 55.311879 |
| Python index | 55.311879 |
| Absolute difference | < 0.00001 |

**Result: passed.** The manual calculation and the Python implementation agree within the specified tolerance for Turin under equal weights.

Validation performed by Anna Luna Orso.

## Final verification

### Education-only scenario

Set **Education to 100** and the other six weights to **0**. In this scenario, each province’s composite index should equal its Education score, and the ranking should follow Education scores in descending order.

For Turin, the expected index is **67.599068**, or **67.60** when displayed to two decimal places.

| Check | Result |
|---|---|
| Turin index observed in the dashboard | 67.60 — matches the expected Education score rounded to two decimal places. |
| Ranking checked against Education scores | Passed — the dashboard ranking matched the descending order of the mean Education scores for all 105 eligible provinces. |

Restore equal weights after the check.

### Profile values and ranking changes

| Check | Result |
|---|---|
| Province profiles | Passed — the displayed values for the two selected provinces matched the 2023 source data. |
| Ranking changes | Passed — the displayed changes matched the differences between the initial and updated positions. |
| Equal-weight reset | Passed — all provinces showed a change of 0 after equal weights were restored. |

### Reproduce the project on a second computer

Passed — dataset regenerated and all three dashboard views opened successfully.# bes-italy-dataviz

An interactive Streamlit dashboard for comparing well-being across Italian provinces. It uses 14 indicators from the 2025 edition of **ISTAT BES dei Territori**, with 2023 as the reference year.

Users can assign weights to seven dimensions of well-being: **Health, Education, Employment, Economy, Environment, Services, and Safety**.

## Dashboard views

| View | What you can explore |
|---|---|
| **Province ranking** | See how provinces rank under the selected weights and highlight a province of interest. |
| **Province profiles** | Compare two provinces across the seven dimensions and inspect the original indicator values. |
| **Ranking changes** | See how many positions each province gains or loses relative to the equal-weight ranking. |

## Run the dashboard locally

The following commands are for **Windows PowerShell**. After cloning the repository, open PowerShell in the `bes-italy-dataviz` folder containing `app.py` and `requirements.txt`. Run all commands from that folder.

### 1. Install the dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Check the source files

The project uses the following two Excel workbooks. Before running the extraction scripts, check that both files are present at these paths:

```text
data/raw/Indicatori_per_provincia_sesso_ed.2025.xlsx
data/raw/Metadati_IT_ed.2025.xlsx
```

The first workbook contains the indicator values. The second contains the indicator metadata.

### 3. Rebuild the 2023 dataset

Run the four extraction scripts, then combine their outputs:

```powershell
python src/salute_istruzione.py
python src/lavoro.py
python src/economia_servizi.py
python src/ambiente_sicurezza.py
python src/prepara_dataset.py
```

The combined dataset used by the dashboard is `data/elaborati/bes_2023.csv`.

### 4. Launch the dashboard

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal. Adjust the seven weights to explore different scenarios. At least one weight must be positive for the dashboard to calculate the index.

## Manual validation — Turin (2023)

| Setting | Value |
|---|---|
| Province | Torino (Turin) |
| ISTAT code | `01-01-001` |
| Reference year | 2023 |
| Data source | ISTAT BES dei Territori, 2025 edition |
| Weighting scenario | Equal weights across all seven dimensions |

### 1. NEET indicator normalization

The NEET indicator (`02IST006-N22`) measures the percentage of young people who are not in employment, education, or training. A lower percentage represents a better outcome, so the normalization assigns a higher score to a lower rate.

| Value used in the calculation | NEET rate |
|---|---:|
| Turin | 12.0% |
| Minimum in the dataset | 5.2% |
| Maximum in the dataset | 33.8% |

```text
NEET score = 100 × (maximum − Turin rate) / (maximum − minimum)
           = 100 × (33.8 − 12.0) / (33.8 − 5.2)
           = 76.223776
```

The manual result matches the normalized score produced by Python to six decimal places.

### 2. Education area score

The Education score is the arithmetic mean of two normalized indicator scores.

| Education indicator | Normalized score for Turin |
|---|---:|
| Tertiary education (ages 25–39) | 58.974359 |
| Young people not in employment, education, or training | 76.223776 |

```text
Education score = (58.974359 + 76.223776) / 2
                ≈ 67.599068
```

### 3. Composite well-being index

With equal weights, each of the seven area scores contributes one seventh of the composite index.

| Area | Normalized score for Turin |
|---|---:|
| Health | 65.789474 |
| Education | 67.599068 |
| Employment | 66.176994 |
| Economy | 58.897396 |
| Environment | 27.342761 |
| Services | 55.820228 |
| Safety | 45.557236 |

The manual calculation gave a composite index of **55.311879**. The area scores in the table are displayed to six decimal places.

### 4. Comparison with Python

The manual result was compared with the output of `calcola_punteggi_aree()` and `calcola_indice()` from `src/indice.py`. The calculation used the `punteggio` column from `data/elaborati/bes_2023_normalizzato.csv`, seven equal weights, and `solo_complete=True`.

| Measure | Result |
|---|---:|
| Manual index | 55.311879 |
| Python index | 55.311879 |
| Absolute difference | < 0.00001 |

**Result: passed.** The manual calculation and the Python implementation agree within the specified tolerance for Turin under equal weights.

Validation performed by Anna Luna Orso.

## Final verification

### Education-only scenario

Set **Education to 100** and the other six weights to **0**. In this scenario, each province’s composite index should equal its Education score, and the ranking should follow Education scores in descending order.

For Turin, the expected index is **67.599068**, or **67.60** when displayed to two decimal places.

| Check | Result |
|---|---|
| Turin index observed in the dashboard | 67.60 — matches the expected Education score rounded to two decimal places. |
| Ranking checked against Education scores | Passed — the dashboard ranking matched the descending order of the mean Education scores for all 105 eligible provinces. |

Restore equal weights after the check.

### Profile values and ranking changes

| Check | Result |
|---|---|
| Province profiles | Passed — the displayed values for the two selected provinces matched the 2023 source data. |
| Ranking changes | Passed — the displayed changes matched the differences between the initial and updated positions. |
| Equal-weight reset | Passed — all provinces showed a change of 0 after equal weights were restored. |

### Reproduce the project on a second computer

Passed — dataset regenerated and all three dashboard views opened successfully.

The following commands are for **Windows PowerShell**. After cloning the repository, open PowerShell in the `bes-italy-dataviz` folder containing `app.py` and `requirements.txt`. Run all commands from that folder.

### 1. Install the dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Check the source files

The project uses the following two Excel workbooks. Before running the extraction scripts, check that both files are present at these paths:

```text
data/raw/Indicatori_per_provincia_sesso_ed.2025.xlsx
data/raw/Metadati_IT_ed.2025.xlsx
```

The first workbook contains the indicator values. The second contains the indicator metadata.

### 3. Rebuild the 2023 dataset

Run the four extraction scripts, then combine their outputs:

```powershell
python src/salute_istruzione.py
python src/lavoro.py
python src/economia_servizi.py
python src/ambiente_sicurezza.py
python src/prepara_dataset.py
```

The combined dataset used by the dashboard is `data/elaborati/bes_2023.csv`.

### 4. Launch the dashboard

```powershell
python -m streamlit run app.py
```

Open the local URL printed in the terminal. Adjust the seven weights to explore different scenarios. At least one weight must be positive for the dashboard to calculate the index.

## Manual validation — Turin (2023)

| Setting | Value |
|---|---|
| Province | Torino (Turin) |
| ISTAT code | `01-01-001` |
| Reference year | 2023 |
| Data source | ISTAT BES dei Territori, 2025 edition |
| Weighting scenario | Equal weights across all seven dimensions |

### 1. NEET indicator normalization

The NEET indicator (`02IST006-N22`) measures the percentage of young people who are not in employment, education, or training. A lower percentage represents a better outcome, so the normalization assigns a higher score to a lower rate.

| Value used in the calculation | NEET rate |
|---|---:|
| Turin | 12.0% |
| Minimum in the dataset | 5.2% |
| Maximum in the dataset | 33.8% |

```text
NEET score = 100 × (maximum − Turin rate) / (maximum − minimum)
           = 100 × (33.8 − 12.0) / (33.8 − 5.2)
           = 76.223776
```

The manual result matches the normalized score produced by Python to six decimal places.

### 2. Education area score

The Education score is the arithmetic mean of two normalized indicator scores.

| Education indicator | Normalized score for Turin |
|---|---:|
| Tertiary education (ages 25–39) | 58.974359 |
| Young people not in employment, education, or training | 76.223776 |

```text
Education score = (58.974359 + 76.223776) / 2
                ≈ 67.599068
```

### 3. Composite well-being index

With equal weights, each of the seven area scores contributes one seventh of the composite index.

| Area | Normalized score for Turin |
|---|---:|
| Health | 65.789474 |
| Education | 67.599068 |
| Employment | 66.176994 |
| Economy | 58.897396 |
| Environment | 27.342761 |
| Services | 55.820228 |
| Safety | 45.557236 |

The manual calculation gave a composite index of **55.311879**. The area scores in the table are displayed to six decimal places.

### 4. Comparison with Python

The manual result was compared with the output of `calcola_punteggi_aree()` and `calcola_indice()` from `src/indice.py`. The calculation used the `punteggio` column from `data/elaborati/bes_2023_normalizzato.csv`, seven equal weights, and `solo_complete=True`.

| Measure | Result |
|---|---:|
| Manual index | 55.311879 |
| Python index | 55.311879 |
| Absolute difference | < 0.00001 |

**Result: passed.** The manual calculation and the Python implementation agree within the specified tolerance for Turin under equal weights.

Validation performed by Anna Luna Orso.

## Final verification

### Education-only scenario

Set **Education to 100** and the other six weights to **0**. In this scenario, each province’s composite index should equal its Education score, and the ranking should follow Education scores in descending order.

For Turin, the expected index is **67.599068**, or **67.60** when displayed to two decimal places.

| Check | Result |
|---|---|
| Turin index observed in the dashboard | 67.60 — matches the expected Education score rounded to two decimal places. |
| Ranking checked against Education scores | Passed — the dashboard ranking matched the descending order of the mean Education scores for all 105 eligible provinces. |

Restore equal weights after the check.

### Profile values and ranking changes

| Check | Result |
|---|---|
| Province profiles | Passed — the displayed values for the two selected provinces matched the 2023 source data. |
| Ranking changes | Passed — the displayed changes matched the differences between the initial and updated positions. |
| Equal-weight reset | Passed — all provinces showed a change of 0 after equal weights were restored. |

### Reproduce the project on a second computer

Passed — dataset regenerated and all three dashboard views opened successfully.