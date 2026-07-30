# Project notes — UK DB Pension Funding & Longevity Model

Running log of decisions, assumptions and gotchas.
Started 29 July 2026. Target completion 24 August 2026.

---

## Environment

- Python 3.11, conda environment named `pensions`
- Recreate with: `conda create -n pensions python=3.11`
  then `conda install -c conda-forge numpy pandas scipy matplotlib
  statsmodels jupyter openpyxl spyder streamlit`
- Activate with `conda activate pensions` at the start of every session
- **Quirk:** `conda-libmamba-solver` is broken in this machine's `base`
  environment (version mismatch with `libmambapy`). Fixed by setting
  `solver: classic` in `~/.condarc`. Every conda command prints an
  entry-point error line — this is cosmetic noise, not a failure.
  Solving is slower as a result. Not worth repairing before deadline.
- `requirements.txt` deliberately left empty until Day 24, when it will
  be generated from the packages actually used.

## Repository

- GitHub: `jeevanbajra/db-pensions-model` (public)
- `data/raw/` and `data/processed/` are gitignored — see Decisions below
- Structure: `src/` (modules), `notebooks/` (exploration),
  `dashboard/` (Streamlit app), `tests/`, `data/`

---

## Data sources

### 1. HMD age-specific death rates
- **File:** `data/raw/Mx_1x1.txt`
- **Source:** mortality.org (Human Mortality Database), account required
- **Downloaded:** 30 July 2026
- **Path on site:** Period data → Age-Specific Death Rates → 1x1
- **Population:** United Kingdom
- **Coverage:** 1922–2022, single year of age 0–110+, by sex
- **Quantity:** central death rates (mx), not probabilities (qx)
- **Version:** last modified 03 Feb 2025, Methods Protocol v6 (2017)
- **Used for:** Lee-Carter improvement projection (Days 7–9)
- **Licence:** not redistributable — gitignored, retrieval steps in README

### 2. ONS National Life Tables
- **File:** `data/raw/nltuk198020223.xlsx`
- **Source:** ons.gov.uk, "National life tables: UK"
- **Downloaded:** 30 July 2026
- **Population:** United Kingdom
- **Coverage:** 43 three-year period sheets, 1980-1982 to 2022-2024
- **Layout:** males cols A–F, blank col G, females cols H–M;
  headers on row 6, data from row 7
- **Columns:** age, mx, qx, lx, dx, ex
- **Used for:** Gompertz-Makeham base table (Days 4–5) and the
  published ex(65) validation check (Day 6)

### 3. Bank of England nominal gilt curve
- **File:** `data/raw/GLC_Nominal_daily_data_current_month.xlsx`
- **Source:** bankofengland.co.uk/statistics/yield-curves
- **Downloaded:** 30 July 2026
- **Curve:** Government Liability Curve, nominal
- **Sheet used:** `4. spot curve` (also keeping `2. fwd curve` for
  the beyond-40-year extrapolation)
- **Grid:** 0.5 to 40 years in 0.5-year steps; rows are dates
- **Coverage in file:** 20 business days, 1–28 July 2026
- **Units:** percent, continuously compounded, annual basis
- **Used for:** discounting (Days 10–11)
- **Renaming of origiinal file: Previously GLC Nominal daily data current month.xlsx
 now GLC_nominal_daily_current_month.xlsx

---

## Decisions

### D1 — Population: United Kingdom (29 July)
Both mortality sources are UK-wide. HMD also publishes England & Wales
separately, but mixing an E&W improvement trend with a UK base table
would be inconsistent. UK chosen for consistency across both sources.

### D2 — Base mortality period: 2022-2024  [CONFIRM]
Most recent available. Excludes 2020 and 2021, which carry severe
pandemic excess mortality and would build a one-off shock into a
long-run assumption.
Rejected: `2019-2021` and `2020-2022` — worst pandemic contamination.
Rejected: `2017-2019` — clean pre-pandemic, but a base table centred
on 2018 is eight years stale by the valuation date.
Caveat: 2022 mortality was still somewhat elevated. Accepted, flagged
in Limitations.
Planned sensitivity: re-run with `2017-2019` once the engine works and
report the difference in funding ratio (Day 22 stress testing).

### D3 — Valuation date: 28 July 2026  [CONFIRM]
Latest gilt curve available in the downloaded file. All discounting
uses the spot curve as at this date.

### D4 — Raw data gitignored (29 July)
HMD terms of use do not permit redistribution, and committing their
data to a public repo would constitute exactly that. Also avoids
permanent repo bloat. README must therefore give full retrieval
instructions for all three files.

### D5 — Discounting convention: continuous  [see F1]
BoE rates are continuously compounded, so v(t) = exp(-y(t) * t) with
y in decimal. Discounting directly in the source convention rather
than converting to annual effective, to minimise conversion steps.

---

## Flags — issues to handle on a specific day

### F1 — BoE rates are continuously compounded  → Day 10-11
The original plan specified v(t) = 1/(1+y(t))^t, which is the annual
effective form and is WRONG for this data.
Correct: v(t) = exp(-y_c(t) * t), or convert first via
y_a = exp(y_c) - 1 and then use the plan's formula.
Both give identical discount factors; the conversion is per maturity.
Size of error if unfixed: discount factors overstated ~1.6% at 20
years, ~3.2% at 40 years. Liabilities overstated ~1.5% overall.
Rates in the spreadsheet are percentages — divide by 100 first.

### F2 — Convention trap in the reconciliation  → Day 12-13
The hand-calculated annuity check must state its own compounding
convention explicitly. If the two sides disagree on convention they
will not reconcile, and the discrepancy will look like a mortality bug.

### F3 — HMD file parsing  → Day 7
- Whitespace-delimited text, two lines of preamble before the headers
- Final age is the string `110+`, so Age won't parse as numeric
- Missing values are `.` not blank (one at male 110+, 2022)
All three fail silently — pandas will load text where numbers are
expected and the error will surface somewhere unrelated.

### F4 — Restrict Lee-Carter fitting window  → Day 7
File starts 1922. Wars and the 1920s contain violent mortality spikes
unrelated to the long-run improvement trend. Fit from roughly 1970
onwards. State the chosen window in the report.

### F5 — Gilt curve parsing and shape  → Day 10
- Maturities sit on row 4; a junk `#VALUE!` row follows
- One maturity missing on 28 July (BoE: available range depends on
  which instruments had reliable prices) — handle gaps, don't assume
  a complete row
- Long end slopes DOWNWARD: 20y spot ~5.70%, 40y ~5.49%. This is real,
  not a data error. Extrapolation beyond 40y holds the FORWARD rate
  flat, not the spot rate — read the 40y forward from sheet 2.

### F6 — Projection base year mismatch  → Day 9
HMD data ends 2022; the 2022-2024 base table is centred on 2023.
State explicitly which year improvements are projected from.

---

## Limitations
_Accumulating for the report's limitations section (Day 25)._

- HMD data ends 2022; valuation date is July 2026. Four-year gap
  between the latest observed mortality and the valuation.
- Base table period includes 2022, which had somewhat elevated
  mortality. Not fully clean of pandemic effects.
- Gilt curve published only to 40 years. Cashflows run well beyond
  that for deferred members, so the tail rests on an extrapolation
  assumption rather than market data.
- National population mortality used throughout. Real DB schemes use
  scheme-specific or SAPS tables; pension scheme members are typically
  lighter-mortality than the general population.
- Membership data is synthetic, not a real scheme.

---

## Log

**29 July** — Registered with HMD (instant, no approval delay).
Created `pensions` conda environment; hit the libmamba solver bug,
resolved with classic solver. Built folder skeleton, wrote .gitignore,
first commit, pushed to GitHub successfully.

**30 July** — Downloaded all three datasets into `data/raw/`.
Confirmed .gitignore works: repo shows four folders, no data. Spotted
the continuous compounding error in the original plan (F1).
Pushed the notes after renaming the BoE file to remove spaces.
