# bes-italy-dataviz
An interactive dashboard for comparing quality of life across Italian provinces using 14 ISTAT BES indicators and user-defined weights for seven dimensions of well-being.


## Manual Validation – Turin (2023)

This section documents a manual validation of the ISTAT BES
normalization and composite index calculations.

**Province:** Torino (ISTAT code: 01-01-001)

**Reference year:** 2023

**Dataset:** ISTAT BES dei Territori, 2025 edition

### 1. NEET indicator normalization

Indicator: Young people not in employment, education or
training (02IST006-N22).

Since lower NEET rates are preferable, the indicator
has a negative direction.

Values from the dataset:

- Turin NEET rate: 12.0%
- Minimum: 5.2%
- Maximum: 33.8%

Manual calculation:

NEET score = 100 × (33.8 - 12.0) / (33.8 - 5.2)

**Manual result: 76.223776**

This matches the normalized score produced by Python,
within rounding precision.

### 2. Education area score

The Education area contains two indicators:

- Tertiary education (25–39 years): 58.974359
- NEET: 76.223776

The area score is the arithmetic mean:

Education = (58.974359 + 76.223776) / 2

**Education score: 67.599068**

### 3. Composite well-being index

The seven area scores for Turin are:

| Area | Normalized score |
|---|---:|
| Health | 65.789474 |
| Education | 67.599068 |
| Employment | 66.176994 |
| Economy | 58.897396 |
| Environment | 27.342761 |
| Services | 55.820228 |
| Safety | 45.557236 |

With equal weights, each area contributes 1/7
to the composite index.

Index = Sum of the seven area scores / 7

**Manual index: 55.311879**

### 4. Python verification

The manual result was compared with the output of
`calcola_punteggi_aree()` and `calcola_indice()`
from `src/indice.py`.

The calculation used:

- `data/elaborati/bes_2023_normalizzato.csv`
- The `punteggio` column
- Seven equal weights
- `solo_complete=True`

Results:

- Manual index: 55.311879
- Python index: 55.311879
- Absolute difference: below 0.00001

**Validation result: PASSED**

The manual calculation and Python implementation agree
within the specified numerical tolerance.

This confirms the calculations for the selected province
and equal-weight scenario, not the correctness of every
province or weighting configuration.

Validation performed by Anna Luna Orso.
