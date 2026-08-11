# Project notes: UK DB Pension Funding and Longevity Model

Running log of decisions, assumptions and gotchas.
Started 29 July 2026. Target completion 22 August 2026.

Conventions used in this file:

- Decisions are numbered D1 upward and are never edited in place. Where a
  decision changes or turns out wrong, a dated note is appended below the
  original and the original wording stands.
- Flags are numbered F1 upward and carry a status line: OPEN, RESOLVED,
  DEFERRED or DUPLICATE, with the day and the reason. Flags are never deleted.
- Day numbers refer to the project plan. Where a day reference in an older
  entry no longer matches the revised plan, the reference has been updated and
  the change is recorded in the Day 12 log entry.

---

## Status index

### Decisions

| Ref | Subject | Settled |
| --- | --- | --- |
| D1 | Population, United Kingdom | Day 1 |
| D2 | Base mortality period, 2022-2024 | Day 1, confirmed Day 12 |
| D3 | Valuation date, 28 July 2026 | Day 1, confirmed Day 12 |
| D4 | Raw data gitignored | Day 1 |
| D5 | Discounting convention, continuous | Day 1 |
| D6 | Gompertz-Makeham fitting range, ages 50 to 100 | Day 4 |
| D7 | Scheme design | Day 3 |
| D8 | CPI assumption, 3.0 per cent | Day 3 |
| D9 | Reproducibility and committing generated data | Day 3 |
| D10 | Upper limiting age of 120 | Day 4 |
| D11 | Fit to ln(mu) rather than mu | Day 4 |
| D12 | Separate fits by sex | Day 4, values Day 5 |
| D13 | Scope reduction | Day 4 |
| D14 | Mortality improvement basis and base year | Day 6 |
| D15 | Life expectancy calculation method | Day 6 |
| D16 | Gilt curve interpolation basis | Day 8, quantified Day 9 |
| D17 | Short end below one year | Day 9 |
| D18 | Persist the curves to a committed CSV | Day 8 |
| D19 | Extrapolation above 40 years | Day 9 |
| D20 | Extrapolation reach | Day 9 |
| D21 | Valuation module structure | Day 10 |
| D22 | Payment timing | Day 10, superseded by D24 |
| D23 | Mortality basis in the annuity factor | Day 10 |
| D24 | Pension payment frequency, monthly in advance | Day 12 |
| D25 | Pension increases at flat CPI 3.0 per cent | Day 12 |
| D26 | Per-member loop rather than a masked matrix | Day 13 |
| D27 | Shared constants imported rather than duplicated | Day 13 |

### Flags

| Ref | Subject | Status |
| --- | --- | --- |
| F1 | BoE rates are continuously compounded | RESOLVED Day 9 |
| F2 | Convention trap in the reconciliation | RESOLVED Day 10 |
| F3 | HMD file parsing | DEFERRED Day 4 |
| F4 | Restrict Lee-Carter fitting window | DEFERRED Day 4 |
| F5 | Gilt curve parsing and shape | RESOLVED Day 8 |
| F6 | Projection base year mismatch | RESOLVED Day 6 |
| F7 | ONS sheet duplicate column names | RESOLVED Day 4 |
| F8 | README with data retrieval steps | OPEN, Day 24 |
| F9 | HMD outputs in committed notebooks | DEFERRED Day 4 |
| F10 | Use the implied inflation term structure | RESOLVED Day 12 |
| F11 | Deployed dashboard cannot read gitignored raw data | OPEN, Days 19 to 20 |
| F12 | Reading members.csv back | OPEN, Day 13 |
| F13 | Independent random streams | OPEN, stretch, no fixed day |
| F14 | Spyder kernel will not start | OPEN, workaround in place |
| F15 | Log-scale objective undefined for negative mu | OPEN, no action |
| F16 | Gilt source file is a rolling download | RESOLVED Day 8 |
| F17 | Fitted GM parameters not committed | OPEN, Day 15 |
| F18 | 40-year forward sits well below the 40-year spot | OPEN, Day 15 |
| F19 | pandas.read_csv float precision | RESOLVED Day 8 |
| F20 | Extrapolation dominates the long horizon | OPEN, Day 15 |
| F21 | Monthly payment frequency not implemented | RESOLVED Day 12 |
| F22 | No cohort survival function exists | RESOLVED Day 12 |
| F23 | Payment grid assumes an integer age | RESOLVED Day 13 for pensioners |
| F24 | RuntimeWarning during curve_fit | DUPLICATE of F15, Day 12 |
| F25 | Implied inflation term structure as a sensitivity | OPEN, Day 15 |
| F26 | LPI cap applied to a central estimate | OPEN, limitations only |
| F27 | Inflation raw file is the only copy | OPEN, Day 15 |
| F28 | membership.py run section was unguarded | RESOLVED Day 13 |
| F29 | annuity_factor defaults to the period basis | OPEN, Day 15 |
| F30 | valuation.py imports membership.py | OPEN, Day 15 |

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
  entry-point error line. This is cosmetic noise, not a failure.
  Solving is slower as a result. Not worth repairing before deadline.
- `requirements.txt` deliberately left empty until Day 24, when it will
  be generated from the packages actually used.

---

## Repository

- GitHub: `jeevanbajra/db-pensions-model` (public)
- `data/raw/` is gitignored in full. `data/processed/` is gitignored
  except for `members.csv` and `gilt_curve.csv`, which are committed
  (see D9 and D18)
- Structure: `src/` (modules), `notebooks/` (exploration),
  `dashboard/` (Streamlit app), `tests/`, `data/`, `report/`
- `.gitkeep` files exist in the empty directories because git tracks
  files, not folders
- `notebooks/scratch.ipynb` is gitignored. It is a workbench, not a
  deliverable (F14)

---

## Data sources

### 1. HMD age-specific death rates

- **File:** `data/raw/Mx_1x1.txt`
- **Source:** mortality.org (Human Mortality Database), account required
- **Downloaded:** 30 July 2026
- **Path on site:** Period data, then Age-Specific Death Rates, then 1x1
- **Population:** United Kingdom
- **Coverage:** 1922 to 2022, single year of age 0 to 110+, by sex
- **Quantity:** central death rates (mx), not probabilities (qx)
- **Version:** last modified 03 Feb 2025, Methods Protocol v6 (2017)
- **Used for:** originally the Lee-Carter improvement projection. Lee-Carter
  was cut under D13, so nothing in the model currently reads this file. It is
  retained in `data/raw` and documented in the README because the further-work
  section of the report scopes a Lee-Carter or CMI implementation
- **Licence:** not redistributable, gitignored, retrieval steps in README

### 2. ONS National Life Tables

- **File:** `data/raw/nltuk198020223.xlsx`
- **Source:** ons.gov.uk, "National life tables: UK"
- **Downloaded:** 30 July 2026
- **Population:** United Kingdom
- **Coverage:** 43 three-year period sheets, 1980-1982 to 2022-2024
- **Layout:** males cols A to F, blank col G, females cols H to M;
  headers on row 6, data from row 7
- **Columns:** age, mx, qx, lx, dx, ex
- **Used for:** Gompertz-Makeham base table (Days 4 to 5) and the
  published e(65) validation check (Day 6)

### 3. Bank of England nominal gilt curve

- **File:** `data/raw/GLC_nominal_daily_current_month.xlsx`
- **Source:** bankofengland.co.uk/statistics/yield-curves
- **Downloaded:** 30 July 2026
- **Curve:** Government Liability Curve, nominal
- **Sheets used:** `4. spot curve` and `2. fwd curve`, the latter for the
  beyond-40-year extrapolation
- **Grid:** 0.5 to 40 years in 0.5-year steps; rows are dates
- **Coverage in file:** 20 business days, 1 to 28 July 2026
- **Units:** percent, continuously compounded, annual basis
- **Used for:** discounting (Days 8 to 9). Note that the model reads the
  committed extract at `data/processed/gilt_curve.csv`, not this file (D18)

### 4. Bank of England implied inflation curve

- **File:** `data/raw/GLC_inflation_daily_current_month.xlsx`
- **Source:** same ZIP download as source 3
- **Downloaded:** 31 July 2026
- **Curve:** implied inflation, derived by the Bank from the nominal
  and real gilt curves
- **Sheet layout:** identical five-sheet structure to the nominal file,
  but `4. spot curve` starts at 2.5 years, not 0.5. 76 maturities to 40
  years. The short end sits in the separate short-end sheets
- **Values at 28 July 2026:** 5y 3.38%, 10y 3.17%, 20y 3.24%,
  30y 3.30%, 40y 3.24%. Essentially flat across the relevant range
- **Used for:** deriving the CPI assumption (D8). Not used as a term
  structure, per D25. Retained for the F25 sensitivity
- **Warning:** this file has not been extracted to a committed CSV and is the
  only copy of 28 July 2026 implied inflation data. See F27

**Naming convention:** BoE files are renamed on the way in to
`GLC_<curve>_daily_current_month.xlsx`, lowercase curve name, no spaces.
Spaces in filenames require escaping or quoting in every terminal
command. The README must state the original download names alongside the
renamed ones.

The ZIP also contains a real (index-linked) curve and an OIS curve.
Neither is currently used. The real curve is a plausible sensitivity if
there is time at the end.

---

## Decisions

### D1: Population, United Kingdom (Day 1, 29 July)

Both mortality sources are UK-wide. HMD also publishes England and Wales
separately, but mixing an E&W improvement trend with a UK base table
would be inconsistent. UK chosen for consistency across both sources.

### D2: Base mortality period, 2022-2024 (Day 1, 29 July)

Most recent available. Excludes 2020 and 2021, which carry severe
pandemic excess mortality and would build a one-off shock into a
long-run assumption.

Rejected: `2019-2021` and `2020-2022`, worst pandemic contamination.
Rejected: `2017-2019`, pre-pandemic so no issue, but a base table centred
on 2018 is eight years prior to the valuation date.

Caveat: 2022 mortality was still somewhat elevated. Accepted, flagged
in Limitations.

Planned sensitivity: re-run the engine with `2017-2019` once the engine works
and report the difference in funding ratio (Days 16 to 17, stress testing).

CONFIRMED (Day 12 review). The 2022-2024 sheet is what the fitted parameters
in D12 were produced from, so this has been in force since Day 5.

### D3: Valuation date, 28 July 2026 (Day 1, 29 July)

Latest gilt curve available in the downloaded file. All discounting
uses the spot curve as at this date.

CONFIRMED (Day 12 review). The committed `gilt_curve.csv` under D18 is the
28 July 2026 row, and every figure recorded in this file is at that date.

### D4: Raw data gitignored (Day 1, 29 July)

HMD terms of use do not permit redistribution, so their data cannot be
committed to a public repo. Also avoids permanent repo bloat. README must
therefore give full retrieval instructions for all four files.

### D5: Discounting convention, continuous (Day 1, 29 July)

BoE rates are continuously compounded, so v(t) = exp(-y(t) * t) with
y in decimal. Discounting directly in the source convention rather
than converting to annual effective, to minimise conversion steps.
See F1.

### D6: Gompertz-Makeham fitting range, ages 50 to 100 (Day 4)

Log-mortality plot (2022-2024, ONS) is near-linear from roughly age 35
onwards, confirming exponential growth in the senescent range.
Below about 35 the curve is dominated by infant mortality and the
accident hump (ages 18 to 25, pronounced in males), which GM cannot
represent.

Chose 50 rather than 35 as the lower bound because scheme liability is
concentrated at ages 55+; fitting over the wider range trades accuracy
where it matters for accuracy where it is not so necessary.

Upper bound 100 is the limit of ONS data.

### D7: Scheme design (Day 3, 31 July)

The synthetic scheme, and every distributional choice behind it.

**Status.** Closed to new entrants in 2005 and closed to future accrual
in 2015. This matches the majority of UK private-sector DB schemes in
2026, and it removes future service cost, salary progression and
withdrawal rates from scope entirely. Existing actives keep what they
have already earned but build up nothing further.

**Salary link broken at closure to accrual.** Accrued pension is fixed
at the closure date and revalues with statutory increases from then on,
rather than remaining tied to the member's actual final salary.
Retaining the link is more generous and does happen in practice, but it
would require salary data and a salary growth assumption, which is
precisely the machinery that closing to accrual was chosen to avoid.

Consequence: actives and deferreds are financially identical. The
`status` field does no calculation work and exists for reporting only.
This must be stated explicitly in the report.

**Death in service excluded.** It is active-only, frequently insured
separately rather than paid from scheme assets, usually expressed as a
multiple of salary (which is not modelled), and it is the opposite tail
to the longevity risk this project is about.

**Size and split.** 1,000 members: 500 pensioners, 350 deferreds, 150
actives. A scheme closed for two decades is pensioner-heavy, because
members retire over time and the active group shrinks and never refills.
1,000 is large enough for the age and pension distributions to look like
a real population, small enough for the dashboard to recalculate
instantly.

**Fields.** Six, each with a named downstream consumer:
`member_id` (tracing one member through the calculation), `status`
(reporting), `sex` (mortality basis), `date_of_birth` (age now and in
every future year), `annual_pension` (amount as at the valuation date),
`normal_retirement_age` (when payment starts).

Not stored: date joined, date left, service, salary. Those are the
inputs used to calculate a pension, and the pension is being generated
directly. Not stored: spouse records, because the standard actuarial
approach uses population-level marriage assumptions instead.

**Date of birth stored, not age.** Age is a fact about a particular
date. If the valuation date moves (D3), stored ages become silently
wrong while dates of birth stay correct. Conversion uses 365.25 days per
year to account for leap years; the exact Gregorian year is 365.2425
days, so the residual error is under a day across the whole population.

**Age distributions.** Normal, truncated, drawn by rejection rather than
clipping. Clipping would set every out-of-range draw to exactly the
bound, producing an artificial spike of members at one age, and for
pensioners that spike would sit at 65, which is the longest-duration and
most expensive point in the population.

| Category | Mean | SD | Range |
| --- | --- | --- | --- |
| Pensioners | 72 | 8 | 65 to 100 |
| Deferreds | 54 | 7 | 43 to 64 |
| Actives | 56 | 6 | 43 to 64 |

Pensioner lower bound is the NRA, since early retirement is not
modelled. Upper bound 100 is the limit of the ONS life table.
Deferred and active lower bound of 43 follows from the scheme having
closed to new entrants in 2005: someone joining at 22 in that year is 43
at the valuation date. Upper bound 64 because at 65 they would reach NRA
and become pensioners.

Note that truncation compresses the spread. Realised standard deviations
are materially below the parameters: about 6.0 for pensioners (one tail
cut) and about 5.2 and 4.8 for deferreds and actives (both tails cut
close to the mean). Anyone reading the constants and then the data will
notice this, so it is worth stating.

**Sex.** Coded `"M"` and `"F"` to match the ONS table as loaded on Day 2,
so the mortality lookup joins directly without recoding. Proportion male
by category: pensioners 0.65, deferreds 0.55, actives 0.50. Pensioners
retired from a workforce formed decades ago when full-career scheme
membership was heavily male; actives are the most recent cohort and are
close to even. Worth distinguishing because sex drives the mortality
basis and pensioners carry the largest share of the liability.

**Pension amounts.** Lognormal. It cannot produce negative amounts, it is
right-skewed in the way real scheme membership is, and it follows from
the calculation itself: service times accrual rate times final salary is
a product of positive quantities, and such products tend to lognormal in
the same way sums tend to normal.

Medians: pensioners 6,000, deferreds 3,500, actives 8,000 pounds a year.
Sigma 0.9 for all three. Deferreds left after shorter service and hold
the smallest pensions; actives were the long stayers at closure and hold
the largest; pensioners sit between, with full careers but earned on
older salary levels.

Note the parameterisation: numpy's first two arguments describe the
underlying normal, so the first is the log of the median, not the mean
pension. No truncation, because very small pensions from short service
and very large ones from long senior careers are both real.

The 6,000 figure is a plausible round number rather than one taken from a
published source. The PPF Purple Book would be the place to anchor it if
needed, but the median scales total liability almost linearly and the
asset value is equally synthetic, so the funding ratio is barely
affected. What the project measures is longevity and rate sensitivity,
which depend on the shape and the demographics rather than the absolute
pound level.

Realised total: 8.13m pounds a year across the scheme (pensioners 4.57m,
deferreds 1.91m, actives 1.65m).

**Benefit increases.** A single tranche, one rule for everybody: CPI
capped at 5% a year, both in payment and in deferment.

Real UK DB benefits are sliced by when the pension was earned, with no
statutory increase requirement pre-1997, CPI capped 5% for 1997-2005,
and CPI capped 2.5% post-2005, plus GMP with its own rules and its own
equalisation litigation. A real valuation tracks every tranche
separately for every member. Modelling that would require a service
history to allocate the tranches and would tell us nothing about
longevity.

Capped at 5% was chosen over 2.5% because it is a real statutory rule,
so the simplification is toward something that exists.

Note that at the assumed CPI of 3.0% (D8) the cap never binds. It is
inert under the central assumption and only earns its place in the
Days 16 to 17 stress test, where a higher inflation scenario shows how
much the cap protects the scheme. See also F26 on what applying a cap to
a central estimate costs.

**Normal retirement age.** 65 for all members. The most common scheme
NRA, and it keeps deferreds uniform. Not to be confused with State
Pension Age, which is moving to 67 and 68; a scheme's NRA is set by its
own rules. Kept as a column despite every value being identical, because
Days 16 to 17 will want to stress it and a column is trivial to vary
where a hardcoded constant is not.

**Spouse's pension.** 50% of the member's pension, payable on the
member's death for the remainder of the spouse's life. 75% of members
assumed married at death. Spouse assumed three years younger than a male
member and three years older than a female member, following the average
age gap. Spouse mortality assumed independent of member mortality.

No spouse records are stored: `sex` already tells the calculation which
direction the age gap runs, so the six-field structure stands.

Commonly worth 10 to 15% of pensioner liability, so it cannot be
ignored, but the reversionary annuity (paying only while the spouse is
alive and the member is dead) is the largest remaining piece of
complexity in the cashflow engine.

SUPERSEDED IN PART (Day 4): D13 cut the explicit reversionary annuity and
replaced it with a loading of roughly 12 per cent applied to pensioner
liability, scheduled Day 15. The assumptions above are what that loading is
derived from and they stand.

### D8: CPI assumption, 3.0% a year (Day 3, 31 July)

Derived rather than assumed. The BoE implied inflation curve at 28 July
2026 sits at roughly 3.2 to 3.3% across the maturities where scheme
liability actually falls. Two deductions from that:

1. **Index basis.** Index-linked gilts are benchmarked to RPI, so the
   implied inflation curve is RPI-based. The historic RPI/CPI wedge is
   roughly 0.5 to 1.0 percentage points. However, RPI is being aligned to
   CPIH from 2030 and nearly all of this scheme's cashflows fall after
   that date, so the market is already effectively pricing CPIH beyond
   2030 and the residual wedge is much smaller than the historic figure,
   arguably close to zero for the bulk of the term.
2. **Inflation risk premium.** Breakeven inflation is not expected
   inflation. Investors pay for protection, which pushes the implied rate
   above genuine expectations. Conventionally worth a couple of tenths.

3.0% is market implied less a small residual wedge and a modest risk
premium. Both deductions are judgement rather than calculation, and
different consultancies would land anywhere between roughly 2.8% and
3.2%. What matters for the report is stating the derivation, not hitting
a correct number, because there is not one.

Note the consistency requirement this addresses: the discount rate comes
from nominal gilt yields of around 5.5%, which already contain the
market's own view of inflation. Assuming CPI at the Bank's 2% target
would implicitly claim a real return far above what the market is
pricing and would understate the liability.

### D9: Reproducibility and committing the generated data (Day 3, 31 July)

**Seed.** `SEED = 42`, used via `numpy.random.default_rng(SEED)`. Every
draw comes from that generator, passed explicitly into each function
rather than reached for as a global. The legacy `np.random.seed` style
sets one hidden global seed for the whole process, so anything else in
the program that uses numpy randomness shares and disturbs it.

Without a fixed seed every run produces a different scheme and therefore
a different liability, so a number moving could not be attributed to a
code change rather than to the dice, and no figure quoted in the report
could be reproduced by anyone.

Note that the seed fixes a single sequence, not individual values.
Each draw consumes the next chunk of that sequence, so inserting or
reordering a draw shifts everything downstream to a different part of the
stream. This stopped mattering once the call order in
`src/membership.py` was finalised.

**Committing `members.csv`.** D4's reasoning is licensing and repo
bloat. Neither applies to self-generated data: there is no licence, and
1,000 rows of six columns is about 60KB. Committed so that anyone
cloning the repo can run the dashboard without regenerating anything.
CSV rather than a binary format because GitHub renders it as a browsable
table in the web interface.

Mechanics: excluding a directory stops git looking inside it at all, so
a negation pattern under `data/processed/` would never be reached. The
contents must be excluded instead:

```
data/processed/*
# members.csv is synthetic and self-generated
!data/processed/members.csv
```

`.gitignore` has no inline comments. A `#` only starts a comment when it
is the first character of the line; anywhere else it becomes part of the
pattern, and the rule silently matches nothing.

### D10: Upper limiting age of 120 (Day 4)

ONS data stops at age 100. Options were to let the fitted GM curve extrapolate
beyond 100, or impose an upper limiting age forcing survival to zero. Chose
both: extrapolate GM from 100 to 120, terminal age 120.

Justification:

- Immateriality. Survival from 65 to 100 is roughly 4 per cent male and 9 per
  cent female. Discounting 35 years at 5.5 per cent continuously compounded
  gives exp(-0.055*35) = 0.146. A pound payable at 100 is worth under a penny
  today. Ages 100 and above contribute a few tenths of one per cent of total
  liability.
- The cashflow projection needs a finite terminal age to terminate at all.
  This is the binding reason, not the modelling one.
- Terminal age 100 rejected because the oldest members are aged 100 at the
  valuation date and would be assigned zero liability.
- 120 is the conventional choice and leaves headroom for every member.

CORRECTED (Day 5): the immateriality arithmetic above used a survival
estimate of roughly 4 per cent from age 65 to 100, taken from memory rather
than from the model. The fitted model gives 35_p_65 = 0.0091 for males.

A pound payable at age 100 is therefore worth about 0.0091 * 0.146 = 0.0013,
so roughly a tenth of a penny today rather than under one penny. The
conclusion is unchanged and the case for immateriality is stronger than
originally stated.

### D11: Fit to ln(mu) rather than mu (Day 4)

curve_fit minimises the sum of squared absolute errors by default. Between
ages 50 and 100 mu spans roughly two orders of magnitude (0.003 to 0.45), so
a 10 per cent error at age 100 contributes around 1800 times more to the
objective than a 10 per cent error at age 65. An unweighted fit on mu is
effectively fitting ages 95 to 100 only.

Chose to fit the log of the GM law against observed ln(mu). The residual then
becomes ln(observed/fitted), a ratio, so every age carries equal weight in
proportional terms.

Justification:

- Scheme liability is concentrated at ages 65 to 90, where an unweighted fit
  puts almost no effort.
- Mortality rates are deaths over exposure. There are far fewer centenarians
  than 65 year olds, so the oldest rates are the least reliably estimated and
  an unweighted fit is most influenced by them.
- The error that matters is proportional, since survival probabilities and
  annuity factors scale with proportional error in mu.

Alternative considered: supplying sigma weights to curve_fit proportional to
mu, which achieves nearly the same reweighting. Rejected as harder to state
for equivalent benefit. The log scale is also the natural scale for a law
that is exponential in age.

Note: this means fitting the log of A + B*C^x, not a log-linear function.
ln(A + B*C^x) does not simplify. Only pure Gompertz gives a straight line.

### D12: Separate fits by sex (Day 4)

Two independent GM fits, male and female, three parameters each.

The Day 2 and Day 4 log-mortality plots show male and female lines running
close to parallel across 50 to 100. Parallel on a log scale means the same
slope and a different intercept, so the same C and a different B. Male
mortality is a roughly constant multiple of female mortality throughout.

A single fit with a sex adjustment would be defensible but would impose the
parallelism as an assumption. Two independent fits let the data demonstrate
it: the fitted C values can be compared afterwards as a check.

A is expected to be poorly determined. Over 50 to 100 the senescent term
B*C^x runs from about 3e-3 to 4e-1 while A is of order 1e-4, so A is
swamped by a factor of thirty at the bottom of the range and by thousands at
the top. A dominates only below about age 30, which is excluded. If A comes
out negative, that is the data failing to identify it rather than a coding
error; options then are bounds on curve_fit or falling back to pure Gompertz.

Fitted parameter values to be recorded on Day 5.

UPDATED (Day 5): the prediction above was wrong. Fitted A is 2.18e-3 male
and 1.54e-3 female, both positive, with standard errors of 9.7e-5 and 7.5e-5
respectively, under 5 per cent of the estimate and roughly 21 to 22 standard
errors from zero. A is therefore well determined over ages 50 to 100, not
weakly identified.

The error in the original reasoning: B*C^x dominates A at the top of the
range, but at age 50 B*C^x is about 1.4e-3 against A of 2.2e-3, so A is the
larger term at the bottom of the fitting range. The crossover sits around
age 55. The claim that A is swamped throughout the range was not checked
against the actual crossover point.

All three parameters are tightly estimated: se(B) about 6 per cent of B,
se(C) about 0.07 per cent of C.

Fitted values (Day 5), full precision for the male parameters because they
are the reference values used in every checkpoint since:

```
Male:   A = 0.002180882981459045
        B = 5.643224210947216e-06
        C = 1.1215211478841929

Female: A = 1.540e-03, B = 2.074e-06, C = 1.13096
```

Standard errors, order A, B, C:

```
Male:   [9.73e-05, 3.51e-07, 8.08e-04]
Female: [7.47e-05, 1.62e-07, 1.03e-03]
```

Mortality doubling time, ln(2)/ln(C): 6.04 years male, 5.63 years female.
Shorter than the classic figure of around 8 years because the fit starts at
age 50, where the curve is steepest, rather than spanning the full adult
range.

The two fitted C values agree to one decimal place, 1.12 against 1.13,
supporting the same-C-different-B reading of the parallel log-mortality
lines. The pure Gompertz baseline agreed more closely still, at 1.1071 and
1.1142.

Starting values came from the log-linear Gompertz baseline (B and C) with A
guessed at 1e-4. The fitted A is roughly twenty times that guess, which did
not prevent convergence.

### D13: Scope reduction (Day 4)

The original plan contained no buffer days and assumed full days of work.
This was not sustainable alongside graduate applications opening late August.
Revised plan cuts three items and adds four buffer days. Driver was time
pressure, not technical difficulty.

Cut 1: Lee-Carter, replaced by a constant mortality improvement factor of
1.25 per cent a year, with 0.75 and 1.75 per cent as the sensitivity range.
Improvement remains in the model and remains a stress test lever. The report
states that the CMI model is the UK industry standard and that a Lee-Carter
or CMI implementation is scoped as further work. Deferred, not abandoned.
HMD data stays in data/raw and in the README retrieval instructions.

Cut 2: spouse's pension applied as a loading of roughly 12 per cent to
pensioner liability, derived from the 75 per cent married proportion and the
50 per cent spouse fraction in D7, rather than an explicit reversionary
annuity calculation.

Cut 3: dashboard reduced to three sliders, four headline metrics, one runoff
chart and one stress table. Tornado chart and mortality curve plot dropped.

Not cut: deferred members, stress testing, liability duration, unit tests,
the trustee report, the deployed dashboard.

Model now completes 15 August, everything completes 22 August.

### D14: Mortality improvement basis and base year (Day 6)

Constant annual mortality improvement of 1.25 per cent, compounding,
applied to the force of mortality. Sensitivity range 0.75 and 1.75 per cent
(D13). Replaces the Lee-Carter projection cut from scope.

Applied to mu rather than to q, because Gompertz-Makeham is a law about the
force of mortality. Conversion to q, where needed, follows afterwards via
q_x = 1 - exp(-mu_x).

Base year is 2023, the midpoint of the 2022-2024 period table (D2).
Improvement compounds from 2023, not from the valuation date. The valuation
date is 28 July 2026 (D3), so three years of improvement have already
elapsed at the point of valuation, and a payment made at the valuation date
carries a factor of (1 - 0.0125)^3, about 0.963.

The three-year offset is applied inside `improved_force_of_mortality` rather
than left to the caller. BASE_YEAR and VALUATION_YEAR are module constants
and the gap is derived from them. This was a deliberate design choice: if
the offset were the caller's responsibility, forgetting it when the cohort
survival function was written would have overstated every mortality rate by
about 3.7 per cent, understating liability, with no error raised. Closes F6.

### D15: Life expectancy calculation method (Day 6)

Complete period life expectancy computed as the integral of t_p_x from
t = 0, evaluated by the trapezoidal rule (np.trapezoid) over integer steps
of t.

Period rather than cohort: current mortality held fixed with no improvement
allowance. This is deliberate, because the published ONS e(65) used for
validation is a period figure and the comparison must be like for like.
The improvement factor is applied separately in the projection, not here.

Trapezoidal integration over integer steps returns the complete expectation
rather than the curtate one, because it effectively averages consecutive
survival probabilities. No half-year adjustment is added. Adding one would
overstate the result by half a year.

Integral truncated at the upper limiting age of 120 (D10) rather than run
to infinity, so t runs from 0 to 55 at age 65. This understates the result
very slightly.

NOTED (Day 12): the function currently hardcodes the period basis. For the
report it should take `survival_fn` the way `annuity_factor` does under D23,
so both period and cohort life expectancy can be quoted. The gap between them
is longevity improvement expressed in years rather than percentage points.
Scheduled Day 15. The Checkpoint 1 validation stays on the period basis and
remains correct as written.

### D16: Gilt curve interpolation basis (Day 8)

Interpolation of the gilt spot curve between published half-year points is
linear on spot rates. Flat-forward interpolation (linear on log discount
factors) was the alternative considered, and is arguably more consistent
with the D19 extrapolation, which holds the forward flat. Rejected
because the difference over a half-year gap on a curve this smooth is
negligible, and one simple stated method is easier to defend than two.
Difference to be quantified on Day 9.

Note that every integer maturity from 1 to 40 is already published, so
interpolation does nothing in the pensioner-only run. It becomes load
bearing on Day 14, when deferred members retire at non-integer horizons.

RESOLVED (Day 9): linear on spot rates and flat forward interpolation were
compared across 781 maturities from 1 to 40 years. The maximum difference
is 0.674 basis points, at 1.2 years, worth 0.0084 per cent on the discount
factor at that point. The largest errors occur at the short end where the
curve has most curvature relative to the half year spacing, and where
scheme cashflows are lightest. Flat forward sits above linear on spot
because accumulated interest y(t)*t is convex here and a chord across a
convex curve lies above it. For scale, the D19 extrapolation choice moves a
discount factor at 76.78 years by roughly a factor of two, four orders of
magnitude larger.

### D17: Short end below one year (Day 9)

Below one year the one-year spot rate is held flat. The BoE publishes a
monthly short-end curve on sheet 3 of the same file, verified to be the
same curve at finer granularity (values match exactly at 1, 2, 3, 4 and
5 years), running down to 0.583 years at the valuation date. Using it was
checked and rejected: at t = 0.75 the true rate is 4.0756 per cent against
4.1225 per cent held flat, giving discount factors of 0.96990 and 0.96956,
a difference of 0.035 per cent on cashflows that are a negligible share of
a pensioner scheme's liability.

Implemented by numpy.interp's default endpoint behaviour rather than by an
explicit branch, which keeps the function vectorised.

### D18: Persist the curves to a committed CSV (Day 8)

The valuation date spot and forward curves are extracted from data/raw and
written to data/processed/gilt_curve.csv, which is committed. The model
reads only the committed CSV; nothing downstream touches data/raw.

Reason: GLC_nominal_daily_current_month.xlsx is a rolling file. It contains
only 1 to 28 July 2026 and nothing else, so a reader following the retrieval
instructions in a later month cannot reproduce the valuation. It is also
gitignored, so the deployed Streamlit app cannot see it at all (F11).

Both the spot curve and the instantaneous forward curve are captured in the
same step, because the D19 extrapolation reads the forward from the same
rolling file and would otherwise be equally irreproducible.

No fallback to data/raw is implemented. A missing CSV should fail loudly
rather than silently switching data path.

### D19: Extrapolation above 40 years (Day 9)

Above the last published maturity of 40 years, the instantaneous forward
rate is held flat at its 40 year value of 3.6414 per cent, and the spot
rate follows as

```
y(t) = ( y(40)*40 + f(40)*(t - 40) ) / t
```

Two alternatives were considered. Holding the spot rate flat at y(40) was
rejected: it is a refusal to make an assumption rather than an assumption,
and it implies a forward curve that jumps discontinuously from 3.64 to 5.49
per cent at 40 years, which no market would price. Convergence to an
ultimate forward rate, as used under Solvency II, was rejected as not being
the approach taken in UK DB scheme funding valuations.

The single published f(40) is used rather than an average of the last five
years of forwards (4.1332 per cent). The averaged version is more stable,
since f(40) is the endpoint of a steep decline and the least well
determined point in the fitted curve, but the window length would be
discretionary and hard to justify. Holding the last published forward flat
is a rule with no discretion in it. The averaged version is quantified as a
sensitivity on Day 15.

### D20: Extrapolation reach (Day 9)

The youngest member is a deferred born 10 May 1983, aged 43.22 at the
valuation date. With a terminal age of 120 the longest discount horizon is
76.78 years, of which 47.9 per cent lies beyond the last published
maturity and is therefore extrapolated rather than observed. For
pensioners the figure is 27.2 per cent.

### D21: Valuation module structure (Day 10)

The annuity factor lives in src/valuation.py rather than in mortality.py or
discounting.py. It is the product of both, so placing it in either would make
one module import the other and destroy their independence. mortality.py can
currently be tested without a gilt curve and discounting.py without a mortality
table, and that is worth preserving. valuation.py is also where pensioner and
deferred liabilities will be built, both of which are constructed from this
function.

### D22: Payment timing (Day 10)

Annually in advance. The first payment falls at the valuation date, is certain
and is undiscounted, so the t = 0 term is exactly 1. Real UK schemes pay
monthly in advance and the standard approximation is a-due(12) = a-due - 11/24.
That adjustment is 0.4583 against an annuity factor of roughly 11.7, so about
3.9 per cent of liability. Not applied yet. See F21.

SUPERSEDED (Day 12): replaced by D24. Monthly in advance, modelled directly.

### D23: Mortality basis in the annuity factor (Day 10)

The annuity factor takes the survival function as an argument, survival_fn,
defaulting to survival_probability. Day 10 uses the period basis deliberately.
The period basis holds 2022-2024 mortality fixed forever, which is correct for
the Checkpoint 1 validation against published ONS period life expectancy, and
wrong for projecting a real member's cashflows, because a member reaching 85 in
2046 will face 2046 mortality rather than today's. The valuation requires a
cohort basis with the D14 improvement factor applied through calendar time.

Period was used on Day 10 because the Checkpoint 2 hand reconciliation needs a
formula that can be integrated on paper, and because introducing a third moving
part would have obscured which component was at fault had the reconciliation
failed. The cohort function is scheduled for Day 12. See F22.

IN FORCE (Day 12): the valuation basis is now cohort. `survival_probability`
remains the default argument and remains correct for validation work against
published period figures. Anything quoting a valuation result must pass
`survival_probability_cohort` explicitly.

### D24: Pension payment frequency, monthly in advance (Day 12, 8 August)

Monthly in advance, modelled directly on a monthly grid. Not annual in advance,
and not the (m-1)/(2m) approximation on its own. Supersedes D22 and resolves F21.

UK DB pensions are paid monthly. Annual in advance pays the whole year on day
one, so it overstates the liability. On the gilt-curve cohort annuity factor of
12.037432488233684, subtracting 11/24 gives 11.579099154900351, a reduction of
3.807877233549612 per cent. Not negligible.

Three options were considered. Annual in advance was rejected as too crude at
3.8 per cent. The approximation alone was rejected because the only thing it
saves is implementation cost, and on this architecture there is none:
annuity_factor already builds a time grid and calls survival and discount
functions that are vectorised and accept any real t, so monthly is a different
step size and a payment of 1/12 rather than 1. The grid goes from 56 elements
to 661.

Derivation of the approximation, which is retained as a validation check.
Monthly in advance pays 1/12 at times 0, 1/12, 2/12 up to 11/12, so the mean
delay against annual in advance is (1/12) * (0 + 1/12 + ... + 11/12) = 11/24,
and generally (m-1)/(2m). It assumes a delay of 11/24 years costs exactly 11/24
of a unit of annuity, which ignores that discounting is exponential rather than
linear and that survival falls across the delay. Both are second order and both
are worst at old ages, where much of a pensioner liability sits.

Monthly is modelled directly and the approximation is used as an independent
check, with the difference reported. Implementation Day 13.

### D25: Pension increases at flat CPI 3.0 per cent (Day 12, 8 August)

Flat 3.0 per cent per D8, not the implied inflation term structure. Resolves F10.

The shape effect was measured. Taking the raw implied rates and deducting a
uniform 0.24 percentage points, which calibrates the curve to 3.00 per cent at
the 20 year point, and comparing cumulative increase factors against flat 3.0
per cent:

```
  term   raw    adjusted   curve factor    flat 3.0 factor   difference
     5   3.38     3.14     1.1671740826    1.1592740743      +0.6815%
    10   3.17     2.93     1.3348108488    1.3439163793      -0.6775%
    20   3.24     3.00     1.8061112347    1.8061112347       0.0000%
    30   3.30     3.06     2.4700408954    2.4272624712      +1.7624%
    40   3.24     3.00     3.2620377920    3.2620377920       0.0000%
```

The zeros at 20 and 40 are an artefact of where the deduction was calibrated,
not a finding. The honest read is that shape moves a cumulative factor by under
2 per cent, in both directions, so it partly cancels across a scheme.

For contrast, the level question already settled by D8 is worth 9.7567 per cent
at 40 years, comparing 3.24 flat against 3.00 flat. Roughly five times larger
and one-directional.

F10 as drafted would have inflated cashflows at raw implied rates. Those are
breakeven rates, not expected rates, so it would have silently dropped both of
D8's deductions and been less accurate on level while more precise on shape.
Applying those deductions properly would mean applying a judgemental adjustment
at all 76 maturities, which does not make it less judgemental. D8 states the
defensible range as 2.8 to 3.2 per cent, so the shape refinement sits inside the
stated uncertainty of the level it is refining.

Note also that spot rates are the correct input here if the curve were used: the
cumulative increase factor to time t is (1 + i(t))^t directly, with no
bootstrapping to forward rates required. The objection to F10 is not that it is
technically awkward.

### D26: per-member loop rather than a masked matrix (Day 13, 10 August)

Total pensioner liability is computed by looping over members in Python and
calling pensioner_epv once each, with each call vectorised across that member's
own payment dates.

The alternative was a single rectangular grid sized for the youngest pensioner,
661 monthly payments to age 120, with a boolean mask zeroing payments beyond each
member's terminal age. That avoids the Python loop entirely at the cost of
computing several hundred columns of discarded values for the average member, and
at the cost of a mask that silently overstates liability if it is wrong.

Chosen on measurement rather than instinct. 500 members take 0.0415 seconds,
0.083 milliseconds each, so a full 1,000 member valuation after Day 14 is around
0.083 seconds. The matrix version would be a rewrite of validated code to save
eighty milliseconds. F11 means the dashboard re-runs the valuation on every slider
move, but Streamlit caching handles repeat calls and this is already well inside
interactive speed.

Revisit only if a measured bottleneck appears, not on suspicion.

### D27: shared constants imported rather than duplicated (Day 13, 10 August)

VALUATION_DATE is defined once in src/membership.py and imported by
src/valuation.py rather than declared twice. Two module level constants holding
the same date stay in step until they do not, and a valuation date differing
between modules would produce ages inconsistent with the dates of birth they came
from.

This required guarding the membership run section, see F28.

It also creates a dependency running from the valuation engine to the synthetic
data generator, which is backwards: a valuation should work on any membership
frame. Recorded as F30 with a proposed fix scheduled for Day 15. Accepted today
because the alternative was refactoring three working modules on a full day for no
change in output.

---

## Flags

### F1: BoE rates are continuously compounded

Raised Day 1. Status: RESOLVED (Day 9).

The original plan specified v(t) = 1/(1+y(t))^t, which is the annual
effective form and is wrong for this data.

Correct: v(t) = exp(-y_c(t) * t), or convert first via y_a = exp(y_c) - 1
and then use the plan's formula. Both give identical discount factors; the
conversion is per maturity.

Size of error if unfixed: discount factors overstated about 1.6% at 20
years, about 3.2% at 40 years. Liabilities overstated about 1.5% overall.

Rates in the spreadsheet are percentages, so divide by 100 first.

Supporting evidence (Day 9): the identity f(t) = y(t) + t*y'(t), which
holds under continuous compounding, was checked at 40 years using a one
year finite difference. It gives 3.698 per cent against a published
forward of 3.641 per cent. The convention is therefore visible in the data
and not only in the documentation.

Implemented in `discount_factor` on Day 9.

### F2: Convention trap in the reconciliation

Raised Day 1. Status: RESOLVED (Day 10).

The hand-calculated annuity check must state its own compounding
convention explicitly. If the two sides disagree on convention they
will not reconcile, and the discrepancy will look like a mortality bug.

Handled at Checkpoint 2, where both conventions were computed and compared.
See the Checkpoints section.

### F3: HMD file parsing

Raised Day 1. Status: DEFERRED (Day 4), Lee-Carter cut from scope under D13.

- Whitespace-delimited text, two lines of preamble before the headers
- Final age is the string `110+`, so Age will not parse as numeric
- Missing values are `.` not blank (one at male 110+, 2022)

All three fail silently. Pandas will load text where numbers are
expected and the error will surface somewhere unrelated.

### F4: Restrict Lee-Carter fitting window

Raised Day 1. Status: DEFERRED (Day 4), Lee-Carter cut from scope under D13.

File starts 1922. Wars and the 1920s contain violent mortality spikes
unrelated to the long-run improvement trend. Fit from roughly 1970
onwards. State the chosen window in the report.

### F5: Gilt curve parsing and shape

Raised Day 1. Status: RESOLVED (Day 8).

- Maturities sit on row 4; a junk `#VALUE!` row follows
- One maturity missing on 28 July, confirmed as the 0.5-year point
  (BoE: available range depends on which instruments had reliable
  prices). Handle gaps, do not assume a complete row
- Long end slopes downward: the curve peaks at 5.8092 per cent at 27 years,
  20y spot about 5.70 per cent, 40y about 5.49 per cent. This is real market
  structure, not a data error
- Confirmed 30 July. Consequence for extrapolation: on a downward-sloping
  segment the instantaneous forward rate sits below the spot rate, so holding
  the forward flat beyond 40 years makes the extrapolated spot curve continue
  to fall. It does not level off at 5.49 per cent. Expected behaviour, not a
  bug. Read the 40-year forward from sheet `2. fwd curve` rather than assuming
  it resembles the 40-year spot

CORRECTED (Day 8): an earlier record placed the peak at about 5.77 per cent in
the mid-20s. The peak is 5.8092 per cent at 27 years. Also, the published grid
runs 0.5 to 40.0 with 0.5 empty at the valuation date, so the 79 usable points
come from a dropna rather than from where the grid starts.

### F6: Projection base year mismatch

Raised Day 1. Status: RESOLVED (Day 6).

HMD data ends 2022; the 2022-2024 base table is centred on 2023.
State explicitly which year improvements are projected from.

REWORDED (Day 4): originally flagged the gap between HMD ending 2022 and the
2022-2024 base table centred on 2023. With Lee-Carter cut, this applies to the
constant improvement factor instead: the report must state explicitly that
improvements are projected from the 2023 base year.

RESOLVED (Day 6): handled in D14. Improvement compounds from the 2023 base
year, with the three-year gap to the 2026 valuation date applied inside
improved_force_of_mortality via the module constants BASE_YEAR and
VALUATION_YEAR. Documented in the function docstring and stated in D14 for
the report.

### F7: ONS sheet duplicate column names

Raised Day 1. Status: RESOLVED (Day 4).

Males and females share a single header row, so pandas appends `.1`
to the female columns (`age.1`, `mx.1`, and so on) when reading H:M.
Columns must be renamed after loading. Will recur when
`src/mortality.py` re-reads this sheet.

RESOLVED (Day 4). Handled by reading the male and female blocks
separately with usecols="A:F" and "H:M", then assigning .columns directly,
so the duplicate .1 names never appeared. Note this method is positional and
silent: it relies on both blocks sharing the same column ordering, which was
verified rather than assumed.

### F8: README with data retrieval steps

Raised Day 1. Status: OPEN, scheduled Day 24.

No README in the repo yet, and D4 commits to one giving full retrieval
instructions for all four data files, including the BoE renaming
convention.

### F9: HMD outputs in committed notebooks

Raised Day 1. Status: DEFERRED (Day 4), Lee-Carter cut from scope under D13.

Keep displayed HMD extracts small: heads, shapes, plots. Do not commit
outputs containing large blocks of the raw matrix. D4's
non-redistribution reasoning applies to notebook outputs, not just to
`data/raw/`.

Confirmed dead (Day 9): nothing HMD-derived exists anywhere in the project.

### F10: Use the implied inflation term structure

Raised Day 3. Status: RESOLVED (Day 12).

Stretch goal. The inflation file (data source 4) has the same five-sheet
layout as the nominal file, so the discounting parser can be pointed at
it with little extra work. Inflating each year's cashflow at that year's
implied rate, rather than at a flat 3.0%, moves the report from
"inflation was assumed" to "inflation was derived from market data at the
valuation date". Watch that `4. spot curve` starts at 2.5 years, not 0.5.

RESOLVED (Day 12): rejected as the primary basis under D25, with the shape
effect quantified against the level effect and against D8's own stated
judgement range. Reopened in reduced form as F25, a sensitivity rather than a
basis.

### F11: Deployed dashboard cannot read gitignored raw data

Raised Day 3. Status: OPEN, bites Days 19 to 20. Driver for F17 on Day 15.

Streamlit Cloud builds from the GitHub repo, so at runtime it can only
see committed files. The ONS, HMD and BoE files are gitignored and
always will be. The dashboard must therefore read small committed
derived artefacts from `data/processed/` (fitted GM parameters, the
discount curve) rather than reprocessing raw data on every page load.
Faster as well.

Fitted parameters are derived work and committing them should be fine. A
full projected mortality table sits closer to the line: re-read the HMD
terms before committing anything mortality-derived.

### F12: Reading members.csv back

Raised Day 3. Status: OPEN, bites Day 13.

CSV stores no type information. `date_of_birth` will arrive as text
unless the file is read with `parse_dates=["date_of_birth"]`. Silent
until date arithmetic fails somewhere unrelated.

PARTIALLY RESOLVED (Day 13). Exercised for the first time. Reading members.csv
without parse_dates raises TypeError inside exact_ages when the Timestamp
subtraction meets a column of strings, so the failure is loud rather than silent
as originally feared. It remains the caller's responsibility, since
pensioner_liability takes an already loaded frame. Left open until the dashboard
and the tests both load the file in one agreed place.

### F13: Independent random streams

Raised Day 3. Status: OPEN, stretch, no fixed day.

`rng.spawn()` gives each component of the generator its own independent
stream, so adding or reordering a draw in one place does not disturb the
numbers everywhere else. A genuine improvement over the single shared
sequence currently used, and a good thing to be able to point at. Not
worth the refactor unless there is spare time near the end.

### F14: Spyder kernel will not start

Raised Day 4, 1 August. Status: OPEN, workaround in place, no action planned.

Spyder launches but the IPython console fails with "An error occurred while
starting the kernel", showing the conda-libmamba-solver entry point error
(module libmambapy has no attribute QueryFormat). Spyder appears to treat
unexpected output on the kernel startup stream as a failure. The same message
is harmless on the command line.

Checked and ruled out: `which spyder` gives the environment's own binary, and
spyder-kernels 3.1.5 is installed in the environment.

Root cause is the conda-libmamba-solver breakage deferred in the Environment
notes. Not repaired: it is a conda dependency untangle with no bearing on
the model.

Workaround: editing src modules in the JupyterLab text editor and testing
in notebooks/scratch.ipynb with %autoreload 2. scratch.ipynb is gitignored
as a workbench rather than a deliverable.

### F15: Log-scale objective is undefined for negative mu

Raised Day 5, 2 August. Status: OPEN, no action taken.

curve_fit emits "RuntimeWarning: invalid value encountered in log" during
optimisation of the Gompertz-Makeham fit, for both sexes, so two warnings
appear on every import. Cause: the model function returns np.log(A + B*C**x),
and while exploring the parameter space the optimiser tries combinations where
A + B*C^x is negative at the lower end of the age range. np.log of a negative
number is NaN, which numpy warns about rather than raising.

Both fits recovered and converged, with all three parameters estimated to
tight standard errors, so the final result is unaffected. The warning
describes the path, not the destination.

Input data confirmed clean (Day 10): no missing values in qx or mu_x, no qx
outside (0, 1), no non-positive mu_x.

Parameter stability confirmed (Day 12): the fitted male parameters reproduce
the Day 5 values to twelve significant figures on re-running.

No action taken. Two residual concerns. First, the Days 16 to 17 re-fit on a
stressed base table (q_x multiplied by 1.1) may wander further into the invalid
region and fail to recover. Second, a reader of the repo sees two warnings on
import and cannot tell they are benign.

The known fix is to constrain the optimiser:
`bounds=([0, 0, 1], [np.inf, np.inf, np.inf])`, forcing A and B non-negative and
C at least 1. Not applied because supplying bounds changes the algorithm
curve_fit uses internally, and the current fit is already validated against the
data. Alternative is a local suppression with an explanatory comment. Decide on
Day 15 alongside F17, or immediately if the Days 16 to 17 fit misbehaves.

### F16: Gilt source file is a rolling download

Raised Day 8. Status: RESOLVED (Day 8) by D18.

The gilt curve source file is a rolling monthly download and cannot be
re-retrieved for 28 July 2026. Closed by D18: the extract is committed.
The BoE publishes archive files by period which would be a fully
reproducible route; not investigated, README footnote only.

### F17: Fitted GM parameters not committed

Raised Day 9. Status: OPEN, scheduled Day 15. Blocking for deployment.

src/mortality.py has the same problem D18 fixes for the gilt curve.
fit_gompertz_makeham reads nltuk198020223.xlsx from data/raw, which is
gitignored under D4 and is 594 KB, so the fit cannot run on Streamlit Cloud.

Fix is the same shape: a run-once extract writing the six fitted parameters
and their standard errors to data/processed/gm_parameters.csv, committed,
with the valuation reading that rather than re-fitting.

This is not housekeeping. Without it the dashboard cannot deploy at all (F11),
so it is a hard gate on Day 15 rather than a tidy-up.

### F18: 40-year forward sits well below the 40-year spot

Raised Day 9. Status: OPEN, quantified further on Day 15 with F20.

The 40-year instantaneous forward at the valuation date is 3.6414 per cent
against a 40-year spot of 5.4880 per cent, a gap of 1.85 percentage points.
Holding the forward flat beyond 40 years therefore continues the downward
slope steeply: extrapolated spot rates are 5.2828 per cent at 45 years,
5.1187 at 50 and 4.9844 at 55. At t = 55 this gives a discount factor 32
per cent higher than holding the 40-year spot flat. This extends F5 with
figures.

### F19: pandas.read_csv float precision

Raised Day 8. Status: RESOLVED (Day 8).

pandas.read_csv loses the final bit of a float64 with its default parser.
load_curve uses float_precision="round_trip" so that the committed CSV
reloads bit-for-bit identically to the frame that was written. Immaterial
to the valuation (differences of order 1e-16) but it would break exact
equality in the unit tests.

### F20: Extrapolation dominates the long horizon

Raised Day 9. Status: OPEN, scheduled Day 15. Largest open judgement in the
model.

Nearly half the discount horizon for the youngest members rests on the D19
extrapolation rather than on observed market data. At t = 76.78 the
extrapolated spot is 4.6034 per cent, giving a discount factor of 0.029174
against 0.014790 if the spot were held flat instead, a factor of roughly
two on the same cashflow.

The mitigation is that survival to age 120 is vanishingly unlikely so the
cashflows out there are minute, but that has not yet been quantified. Total
liability under flat-forward, flat-spot and averaged-forward extrapolations to
be compared on Day 15. This belongs in the report in plain words, and it gets a
section rather than a sentence.

### F21: Monthly payment frequency not implemented

Raised Day 10. Status: RESOLVED (Day 12).

Benefits are valued as annual payments in advance. UK schemes pay monthly. The
11/24 adjustment under D22 is worth about 3.9 per cent of liability, which is
material and cannot be left silent in the report. To be settled on Day 12,
either by applying the adjustment or by stating the annual basis as a
simplification with its size quantified.

RESOLVED (Day 12): settled by D24. Monthly in advance, modelled directly, with
the approximation retained as a validation check.

### F22: No cohort survival function exists

Raised Day 10. Status: RESOLVED (Day 12).

survival_probability integrates the unimproved Gompertz-Makeham force.
improved_force_of_mortality exists but nothing integrates it, so there is
currently no way to compute survival on the D14 improvement basis. The integral
remains closed form: the improvement factor is exponential in time and
Gompertz-Makeham is exponential in age, so C is replaced by C*(1-r) in the
senescence term and the Makeham constant acquires its own exponential decay.
Scheduled Day 12, before pensioner liabilities. Estimated to raise the annuity
factor by roughly 4 to 4.5 per cent at realistic discount rates.

RESOLVED (Day 12). survival_probability_cohort implemented in src/mortality.py.
Closed form derived from first principles rather than quoted.

**Derivation.** The force for a life aged x at the valuation date, at duration
s, is (A + B*C^(x+s)) * d^(k+s) where d = 1 - r and k = BASE_TO_VALUATION = 3.
Splitting d^(k+s) and C^(x+s), and folding C^s * d^s into (C*d)^s, gives an
integrand of d^k * [A*d^s + B*C^x*(Cd)^s]. Each term is a constant times a
single base to the power s, so both integrate as a^s / ln(a). Hence

```
t_p_x = exp( -d^k [ (A/ln(d))*(d^t - 1) + (B*C^x/ln(Cd))*((Cd)^t - 1) ] )
```

Senescent base Cd = 1.1075021335356405 for the fitted male C.

**Validation.** Verified against seven independently computed targets at x = 65,
agreeing to sixteen significant figures. Structural checks pass: exactly 1.0 at
t = 0, monotonically decreasing over t = 0 to 55 at quarter-year steps, strictly
above the period curve for all t > 0, all values in (0, 1].

**Reduction to the period case.** At r = 0 the senescent term collapses to the
period form directly. The Makeham term becomes A*(1-1)/ln(1), which requires the
limit of (d^t - 1)/ln(d) as d tends to 1, equal to t, recovering A*t. So the
cohort model contains the period model as a special case. Note that
improvement = 0 cannot be passed literally, since ln(1) = 0 gives nan. Tested at
improvement = 1e-13, which reproduces the period 20_p_65 of 0.44876302444756944
to twelve significant figures.

**Correction to the estimate made when this flag was raised.** The 4 to 4.5 per
cent figure above was produced from four significant figure parameters. Computed
from the exact fitted parameters the uplift is 4.612467896856232 per cent at
flat 5 per cent, above that range, and 4.079496382960346 per cent on the gilt
curve, inside it. The original estimate stands unedited.

**Consequence.** `improved_force_of_mortality` is no longer reached by any
execution path, because the cohort survival function computes from the closed
form. It is retained as a test fixture: a finite difference on
survival_probability_cohort must reproduce it. At x = 65, t = 20 both routes
give 0.07399580786141326. Test to be written Day 15.

### F23: Payment grid assumes an integer age

Raised Day 10. Status: RESOLVED (Day 13) for pensioners. Deferreds to be checked
on Day 14.

annuity_factor builds its payment times with
np.arange(0, UPPER_LIMITING_AGE - x + 1), which assumes x is a whole number.
True for the age 65 test case, not true for real members, whose ages derive
from dates of birth.

RESCHEDULED (Day 12): originally Day 14, for deferred members retiring at
non-integer horizons. It bites a day earlier than that, because the Day 13
monthly grid under D24 has to run from a pensioner's actual non-integer age.
Two sub-questions to settle when it is fixed: whether the grid still terminates
at age 120 exactly, and whether the final payment lands on or before the
terminal age.

RESOLVED (Day 13). payment_times(x, frequency, upper_age) built in
src/valuation.py. The payment count is floor((upper_age - x) * frequency) + 1,
which handles any real age, and the times are integer month indices divided once
by frequency.

Verified at five ages: 65.0 gives 661 payments ending at t = 55.0, 72.34 gives
572 ending at 47.583333333333336, 84.5 gives 427, 99.8 gives 243, 100.0 gives
241. In every case the first payment is exactly 0.0 and the age at the last
payment does not exceed 120. Whole number ages land exactly on the terminal age
because their runway is a whole number of months; fractional ages stop just short,
which is correct rather than a rounding artefact.

frequency = 1 reproduces the Day 10 annual grid of 56 elements ending at 55.0,
which is an independent cross-check against already validated work.


### F24: RuntimeWarning during curve_fit

Raised Day 10. Status: DUPLICATE of F15, identified Day 12.

Raised independently on Day 10 as a fresh observation, having already been
logged as F15 on Day 5. The number is retained rather than reused so that
references to F24 elsewhere still resolve. The substance, including the input
data cleanliness check performed on Day 10, has been merged into F15.

### F25: Implied inflation term structure as a sensitivity

Raised Day 12. Status: OPEN, scheduled Day 15. First item on the cut list.

The reduced-scope survivor of F10. Re-run total liability using the raw implied
inflation term structure and report the difference against flat 3.0 per cent, as
evidence that the flat assumption is not materially distorting the answer.

Requires extracting the inflation curve to a committed CSV first, per D18 and
F27. Sits alongside the F20 extrapolation comparison already scheduled for Day
15, which needs the same re-run harness.

Not a basis change. D25 stands regardless of what this produces, unless the
difference is far larger than the shape analysis in D25 predicts.

### F26: LPI cap applied to a central estimate

Raised Day 12. Status: OPEN, limitations section only. Not a build item.

LPI is min(max(CPI, 0), 5), a non-linear function, and it is being fed a single
expected rate rather than a distribution. The expectation of the function is not
the function of the expectation.

Modelling CPI as normal around 3.0 per cent and integrating:

```
  sd     E[LPI]     shortfall     P(>5%)    P(<0%)    effect on 20yr cumulative
  1.0   2.991891   -0.008109 pp   2.28%     0.13%     -0.1573%
  1.5   2.949143   -0.050857 pp   9.12%     2.28%     -0.9829%
  2.0   2.891983   -0.108017 pp  15.87%     6.68%     -2.0767%
  2.5   2.839738   -0.160262 pp  21.19%    11.51%     -3.0663%
```

The cap sits 2 percentage points above the central rate and the floor 3 below,
so the cap truncates more probability than the floor rescues and the net is
always negative. The deterministic treatment therefore overstates increases and
overstates the liability, which is the prudent direction.

At plausible volatility of 1.5 to 2.0 percentage points the error is 1 to 2 per
cent on a 20 year cumulative increase factor. Comparable to the inflation shape
effect rejected as immaterial under D25, so consistency requires the same
treatment: acknowledge, quantify, do not build for it.

The Days 16 to 17 inflation stress of plus or minus 0.5 percentage points moves
the central rate rather than introducing dispersion, so it is not a substitute.

### F27: Inflation raw file is the only copy

Raised Day 12. Status: OPEN, first step of F25 on Day 15.

D18 closed this for the nominal gilt curve by committing an extracted CSV. The
inflation file has the same problem and has not been extracted. The only copy of
28 July 2026 implied inflation data is the gitignored
GLC_inflation_daily_current_month.xlsx in data/raw.

If it is lost or re-downloaded, F25 becomes impossible and D8's derivation
becomes unverifiable by anyone including me. Do not delete data/raw.

File confirmed present 8 August, 349,408 bytes, dated 29 July.

### F28: membership.py run section was unguarded

Raised Day 13. Status: RESOLVED (Day 13).

The generation and write block at the foot of src/membership.py sat at module
level, so importing anything from that file regenerated 1,000 members, rewrote
data/processed/members.csv and printed seven diagnostic blocks.

Found while implementing D27, which imports VALUATION_DATE from that module.

Fixed by placing the build, assemble, save and check sections under
if __name__ == "__main__". Constants and the seeded generator stay at module
level, since creating a generator consumes nothing from the sequence and every
draw_ call sits inside the guard.

Verified two ways. Running the file directly still writes the file and prints as
before, and git status afterwards shows members.csv unmodified, so the D9 seeding
reproduces the scheme byte for byte. Importing the module now prints nothing.

Would have surfaced on Days 19 to 20 as a regeneration and disk write on every
Streamlit page load, on a platform where the filesystem is ephemeral.

### F29: annuity_factor defaults to the period basis

Raised Day 13. Status: OPEN, decision scheduled Day 15.

D23 gave annuity_factor a survival_fn parameter defaulting to
survival_probability, the period basis. Since Day 12 the valuation basis is
cohort, so the default is now the exception rather than the rule. Any call that
omits the argument silently returns a figure roughly 4 per cent too low, with no
error raised.

Same failure shape that D14 designed out by putting the base year offset inside
improved_force_of_mortality rather than trusting the caller.

Not changed on Day 13 because flipping the default breaks the Day 10 tests that
call annuity_factor without the argument, and rewriting those is mortality.py and
tests/ work rather than liability engine work. pensioner_epv was written with
survival_probability_cohort as its default from the outset, so nothing built today
carries the problem.

Proposed resolution: flip the default and make every validation call state
survival_probability explicitly. Breaking the tests is the point, since a test
asserting a period figure should say so in its own body rather than inherit it
from a default.

### F30: valuation.py imports membership.py

Raised Day 13. Status: OPEN, decision scheduled Day 15.

D27 makes the valuation engine depend on the synthetic data generator, which
inverts the intended direction. D21 explicitly valued keeping modules independent
so each can be tested without the others.

Proposed fix: a small src/config.py holding the constants that cross module
boundaries, VALUATION_DATE, UPPER_LIMITING_AGE, CPI, LPI_CAP, LPI_FLOOR and
IMPROVEMENT_RATE, with every module importing from it and none importing each
other.

Deferred because it touches three working modules for no change in output.

---

## Limitations

Accumulating for the report's limitations section, Days 22 to 23.

### Data

- HMD data ends 2022 and the valuation date is July 2026, a four-year gap
  between the latest observed mortality and the valuation. Moot in the current
  scope, since Lee-Carter was cut and nothing reads the HMD file.
- The base table period includes 2022, which had somewhat elevated mortality.
  Not fully clean of pandemic effects.
- National population mortality is used throughout. Real DB schemes use
  scheme-specific or SAPS tables, and pension scheme members are typically
  lighter-mortality than the general population.
- Membership data is synthetic, not a real scheme.

### Mortality model and fit

- Force of mortality is assumed constant within each year of age, giving
  mu_x = -ln(1 - q_x). This is an approximation and is stated in the report.
  It also means the fitted mu is closest in interpretation to mu at age x+0.5
  rather than exactly x.
- Gompertz-Makeham overstates mortality above roughly age 95, where observed
  mortality decelerates and flattens. Visible in the Day 4 log-mortality plot.
  Quantified on Day 5: the fitted model gives 35_p_65 = 0.0091 for males, so
  roughly 1 per cent of 65 year old males are projected to reach 100, against a
  national life table figure nearer 3 to 4 per cent. Overstating mortality
  understates survival, which understates liability and the deficit, so the bias
  runs the imprudent way. Quantifiable on Day 15 by comparing total liability at
  terminal ages 110 and 120. The standard fix is a logistic blend such as
  Kannisto above the oldest ages; noted as further work rather than implemented.
- It has not been established whether the 3 to 4 per cent comparison figure
  above is a period or a cohort one. If cohort, part of what was attributed to
  Gompertz-Makeham functional form is actually the period basis. To be checked
  on Day 15 now that both bases are running.
- The Gompertz-Makeham residuals show a systematic wave rather than random
  scatter. Observed minus fitted ln(mu) is negative at ages 50 to 54, positive
  at 55 to 70, negative at 71 to 86, positive at 87 to 97, and negative at 98 to
  100. Both sexes trace the same shape almost exactly, so this is
  functional-form error rather than sampling noise: two independent fits to two
  independent datasets would not produce the same wave by chance.
- Maximum absolute deviation is about 0.08 in log units, so roughly 8 per cent
  in mu, occurring near ages 76 and 91. Over ages 50 to 100 the fitted curve is
  within 8 per cent of observed mortality everywhere, which is a reasonable
  result for a three-parameter model spanning two orders of magnitude.
- The negative lobe at 71 to 86 means the fit overstates mortality where
  pensioner liability is concentrated, which understates liability and the
  deficit. The positive lobe at 87 to 97 partly offsets this. Richer functional
  forms such as Perks, Beard, or a logistic model fit UK adult mortality better
  and are what the CMI and most UK insurers use. Noted as further work rather
  than implemented.
- Mortality improvement is a constant 1.25 per cent a year rather than the CMI
  model that is UK industry standard. Scoped as further work under D13.

### Financial assumptions

- The gilt curve is published only to 40 years. Cashflows run well beyond that
  for deferred members, so the tail rests on an extrapolation assumption rather
  than market data. 47.9 per cent of the longest horizon is extrapolated (D20,
  F20).
- The BoE implied inflation curve is RPI-based. The CPI assumption is derived
  from it by deduction rather than observed directly, and both deductions are
  judgement rather than calculation (D8).
- Inflation is applied as a single flat rate rather than as the term structure
  the market prices. Quantified and defended under D25; a sensitivity is
  scheduled under F25.
- The LPI cap and floor are applied to a central estimate rather than to a
  distribution, which overstates the liability by roughly 1 to 2 per cent on a
  20 year cumulative increase factor at plausible inflation volatility (F26).

### Membership

- Pensioner ages are drawn from a symmetric normal. A real closed scheme's
  pensioners are a cohort that entered at NRA and has been thinned by mortality
  ever since, so the true right tail is lighter than a normal implies.
- Pension amounts are drawn independently of age and of sex. In practice longer
  service correlates with both, and historic earnings patterns mean male members
  tend to hold larger pensions.
- Normal retirement age is 65 for every member, so the deferred population is
  uniform in a way a real scheme is not.
- Exact ages are computed from whole days, since Timedelta.dt.days discards any
  part day remainder. A member is therefore up to one day younger than their true
  age. Consistent with D7's use of 365.25 days per year in the other direction,
  and worth under three thousandths of a per cent of a single payment.

### Benefit structure

- A single benefit tranche is modelled. Pre-1997, 1997-2005 and post-2005
  accrual and GMP are not distinguished. This overstates increases on older
  pension and understates the bite of the cap on newer pension.
- Death in service is not modelled.
- Early retirement with an actuarial reduction, and late retirement, are not
  modelled.
- The salary link is assumed broken, so actives and deferreds are modelled
  identically. The status split is presented for reporting only.
- The spouse's pension is applied as a loading of roughly 12 per cent rather
  than as an explicit reversionary annuity (D13).
- Spouse mortality is assumed independent of member mortality. Couples'
  mortality is correlated in practice, the widowhood effect being well
  documented, so this slightly understates the joint liability.
- The pensioner liability recorded on Day 13 excludes the spouse's pension. The
  D13 loading of roughly 12 per cent is applied on Day 15, so the Day 13 figure is
  not the pensioner Technical Provisions.

### Basis and scope

- Figures recorded in this file before 8 August are on the period mortality
  basis. They remain valid as validation results, in particular the Checkpoint 1
  comparison against ONS published e(65), which correctly compares period
  against period. They are superseded for valuation purposes by the cohort basis
  under D23 and F22.

---

## Checkpoints

### Checkpoint 1 (Day 6, 3 August): graduated table validated against published e(65). PASSED.

Complete period life expectancy at age 65, computed from the fitted
Gompertz-Makeham parameters by analytic survival probabilities and
trapezoidal integration:

```
              Fitted    ONS published    Difference
Male          18.26         18.73          -0.47
Female        20.66         21.16          -0.50
```

Both within half a year, against a tolerance of roughly one year. The two
figures come from entirely independent routes: ONS build theirs from the
raw q_x by their own method, and the fitted figure comes from a
three-parameter curve integrated analytically.

Both differences are negative and almost identical in size, so the model
systematically understates life expectancy by about half a year. Two
contributions, both already documented before this result was seen:

1. Truncation at the upper limiting age of 120 (D10) removes the tail
   beyond that age. Small, and always in the same direction.
2. The old-age flattening limitation. GM overstates mortality above age 95,
   so survivors are removed too quickly in their late nineties. Already
   quantified on Day 5: the fitted model gives 35_p_65 = 0.0091 for males
   against a national life table figure nearer 3 to 4 per cent. This
   accounts for most of the half year.

Consequence for the valuation: understating survival understates liability.
The shortfall is concentrated at very old ages, which are heavily
discounted, so the effect on the funding ratio is considerably smaller than
0.47/18.73 would suggest. To be quantified on Day 15 alongside the
terminal-age comparison.

### Checkpoint 2 (Day 10, 7 August): annuity factor validation. PASSED.

Male aged 65, terminal age 120, annual payments in advance, period mortality
basis, flat 5 per cent continuously compounded curve.

Reconciled three ways.

**Individual terms**, hand calculation in Desmos against code output:

```
  t    t_p_65          v(t)            term
  0    1.0000000000    1.0000000000    1.0000000000
  1    0.9875657826    0.9512294245    0.9394016310
  2    0.9740625009    0.9048374180    0.8813681983
  3    0.9593920437    0.8607079764    0.8257563845
```

Agreement to every printed digit.

**Total**, annuity_factor against a hand-rolled sum written independently in the
notebook: both 11.747146253364836. Identical to all seventeen digits, so the
summation and the payment grid carry no error.

**Against Checkpoint 1.** The sum of survival probabilities over the payment
grid equals the Checkpoint 1 life expectancy plus exactly 0.5, for both sexes.
18.764535919118817 against e(65) of 18.264535919118817 for males, and
0.4999999999999964 for females, the latter differing from 0.5 by float noise of
order 1e-15. This falls out of the trapezoidal integration used in
life_expectancy and validates the payment grid against a figure already
validated against published ONS data.

On the real gilt curve at the valuation date the annuity factors are
11.565613695844538 for males and 12.429276334946415 for females.

**Compounding convention, F2.** The same annuity under effective annual
discounting at 5 per cent is 11.863569819905354, against 11.747146253364836
continuous. A difference of 0.11642356654051866, or 0.991 per cent. 5 per cent
continuous is 5.127109637602412 per cent effective annual, since exp(0.05) - 1
gives that figure, so continuous discounting at the same headline rate discounts
harder and produces the smaller annuity. Just under 1 per cent of liability
turns on how the discount factor is written, which is the same order of
magnitude as a plausible mortality error. This is why the convention is stated
explicitly in the report rather than assumed.

Note on the reconciliation itself: the first attempt disagreed because the hand
calculation used A^t in place of A*t. The code was correct and the hand
calculation was wrong. That is the more common outcome and it is still a pass.
The reconciliation establishes that two independent routes agree, not which one
is right when they do not.

**Superseded (Day 12).** These figures are on the period basis. The cohort
equivalents are recorded in the Day 12 log entry. The validation itself stands.

### Day 13 decision gate (10 August): pensioner liability. PASSED.

Total pensioner liability 51480005.7698302, against total pensioner pension in
payment of 4569142.85. Cohort mortality basis (D23), monthly in advance (D24),
LPI at flat CPI 3.0 per cent (D25), gilt curve at the valuation date, before the
spouse loading.

Ratio of liability to pension in payment is 11.266884722115922, a pension
weighted average annuity factor. This must sit below 15.069777434175714, the
monthly with increases EPV per pound for a male aged exactly 65, because every
pensioner is older than that. Mean pensioner age is 74.45756057494867.

Reconciliation against single member work. The youngest male is aged
65.07597535934292 and returns 15.032912 per pound, against 15.069777434175714
computed independently at exactly 65.0. The gap implies 0.4852288227992443 per
year of age, or 3.219875663905588 per cent, which is the right order for an
annuity at that age. The whole population path and the single member path agree
at the one point where they overlap.

EPV per pound by sex and age:

  M  324 members, youngest 65.0760 at 15.032912, oldest 95.2416 at 2.521870
  F  176 members, youngest 65.2813 at 16.391052, oldest 95.3128 at 2.880782

Monotonically decreasing with age within each sex, allowing ties. Six tied pairs
arise from members sharing a date of birth, five male and one female, with
differences of exactly zero or of order 1e-15. Ties are near certain rather than
surprising: across 11,044 possible dates of birth in the pensioner age range, the
probability of at least one shared date is 0.991243484804045 among 324 males and
0.7520237517916077 among 176 females.

Mean EPV per pound is 10.48669025897467 male and 11.78026746520839 female, a
ratio of 1.1233541922463721. Checkpoint 2's age 65 gilt curve factors imply about
1.075; the figure here is higher because the two sexes have different age
distributions, so they are not directly comparable.

Concentration. The largest single member EPV is 1080655.1352335217, being
2.0991744640923068 per cent of the total. The ten largest together are
14.657452877827176 per cent. Consistent with the lognormal pension draw in D7.

Runtime 0.0415 seconds for 500 members. See D26.

### D24 validation (Day 13): the 11/24 approximation

Male aged 65, gilt curve, cohort basis, no increases.

  annual in advance    12.037432488233684
  monthly in advance   11.574695632191498
  exact adjustment      0.46273685604218606
  11/24 approximation   0.4583333333333333
  residual             -0.004403522708852747

The approximation understates the true cost of paying monthly by
0.9607685910224176 per cent of the adjustment itself, or 0.03658190991440318 per
cent of the annuity. Direction as predicted in D24: the approximation assumes a
delay of 11/24 years costs exactly 11/24, ignoring that discounting is exponential
rather than linear and that survival falls across the delay. Both omissions make
the true cost slightly larger than the linear estimate.

Two independent routes agreeing to within a thousandth of a per cent of the
liability, with the residual explained rather than absorbed.

With increases the frequency adjustment is larger, 4.212845828806289 per cent
against 3.8441491281010376 per cent without. Increases push value into later
payments and later payments are where the timing shift bites hardest, so the two
interact rather than adding independently. This is why D24 required modelling
monthly directly rather than subtracting 11/24 from a figure computed on a
different basis.

Increase uplift at age 65: 30.69702536791967 per cent annual,
30.195885170956103 per cent monthly. CPI at 3.0 per cent against a gilt curve
near 5.5 per cent leaves a real discount rate near 2.5 per cent, worth close to a
third of the liability over a 65 year old's horizon.

---

## Log

### Day 1, Wednesday 29 July

Registered with HMD (instant, no approval delay). Created the `pensions` conda
environment; hit the libmamba solver bug, resolved with the classic solver.
Built the folder skeleton, wrote `.gitignore`, first commit, pushed to GitHub
successfully. Settled D1 to D5 and raised F1 to F4.

### Day 2, Thursday 30 to Friday 31 July

Downloaded all three datasets into `data/raw/`. Confirmed `.gitignore` works:
the repo shows four folders and no data. Spotted the continuous compounding
error in the original plan (F1). Pushed the notes after renaming the BoE file to
remove spaces.

Both datasets loaded into clean DataFrames. ONS validated against published e(0)
of 79.12 male and 83.02 female. Log-mortality plot near-linear from about age
35; accident hump visible at 18 to 25, larger for males; male and female lines
parallel above 35, meaning a constant ratio. Gilt curve reshaped to 79
maturities, humped with an inverted long end. F5 and F7 both confirmed as
predicted.

### Day 3, Friday 31 July

Settled the full scheme design (D7), the CPI assumption (D8) and the
reproducibility approach (D9). Added the BoE implied inflation file as data
source 4 after checking what else was in the downloaded ZIP; it showed the
working assumption of 2.5 per cent CPI to be roughly 0.75 percentage points
below market, which would have understated the liability materially.

Wrote `src/membership.py`, the first module in `src/`: four functions plus a run
section, generating 1,000 members with a total of 8.13m pounds of annual
pension. Committed the generated `members.csv` alongside it. Also fixed a
`.gitignore` negation pattern that was silently doing nothing because of an
inline comment.

### Day 4, Saturday 1 August

Settled D10, D11 and D12 before coding. Revised the project plan to a
sustainable scope (D13). Wrote `src/mortality.py` with load_ons_table,
add_force_of_mortality, restrict_to_fit_range and plot_log_mortality. Validated
against Day 2: e(0) of 79.12 male and 83.02 female reproduced through a
different code path.

The Spyder kernel failed (F14), so work moved to the JupyterLab text editor plus
a scratch notebook. The log-mortality plot over 50 to 100 confirms near-linear
and near-parallel lines, supporting both the GM law and separate fits by sex,
with visible flattening above 95.

### Day 5, Sunday 2 August

Fitted a log-linear pure Gompertz baseline by np.polyfit on ln(mu) to obtain
starting values (C = 1.1071 male, 1.1142 female). Fitted the full
Gompertz-Makeham by curve_fit on ln(mu), separately by sex, with p0 from the
baseline plus A = 1e-4. Both converged. All three parameters tightly estimated;
the Makeham constant A proved well determined, contrary to the prediction in
D12, which has been corrected. Raised F15.

Built fitted-against-raw and residual diagnostic plots. Residuals show a
systematic wave within plus or minus 8 per cent in mu across 50 to 100, logged
as a limitation.

Derived and implemented the closed-form t-year survival probability by
integrating the GM force of mortality analytically. Validated: 0_p_65 = 1.0
exactly, 10_p_65 = 0.8151, 20_p_65 = 0.4488, 35_p_65 = 0.0091, monotonically
decreasing throughout.

### Day 6, Monday 3 August

Wrote life_expectancy, computing complete period life expectancy by trapezoidal
integration of the closed-form survival function to the upper limiting age.
Validated the graduated table against the published ONS e(65): 18.26 against
18.73 male, 20.66 against 21.16 female, both within half a year and both
understating, consistent with the old-age flattening limitation identified on
Day 5. Checkpoint 1 passed.

Wrote improved_force_of_mortality applying the constant 1.25 per cent annual
improvement to mu, compounding from the 2023 base year with the three-year gap
to the valuation date handled internally (D14, closes F6). Verified the
compounding at 0 and 20 years from valuation against ln(0.9875) multiples.
Mortality module complete.

### Day 7, Tuesday 4 August, BUFFER

Buffer day to catch up on any work not completed on time. Everything was up to
date, so the time went on rewording notes and on graduate role application
research.

### Day 8, Wednesday 5 August

src/discounting.py: constants, read_curve_sheet, extract_curves, load_curve,
spot_rate. Both curves extracted and committed. Interpolation verified against
published points and against the midpoint at 19.75 years. Decisions D16 and D18,
flags F16, F19 and the corrections recorded under F5.

### Day 9, Thursday 6 August

spot_rate extended above 40 years by flat forward extrapolation, kept vectorised
with numpy.where and numpy.maximum. discount_factor added as exp(-y(t)*t) per
F1. D16 quantified and closed. Decisions D17, D19 and D20, flags F17, F18 and
F20.

### Day 10, Friday 7 August

Built src/valuation.py with annuity_factor, the expected present value of one
pound a year payable annually in advance. Five lines, fully vectorised, no loop.
Takes the survival function as an argument so the mortality basis can be swapped
without editing the body (D23).

Cleared Checkpoint 2, the Day 10 decision gate. See the Checkpoints section.

Added a test suite: pytest 9.0.3, conftest.py at the repo root putting src on the
import path, seven tests across three files, all passing.

The payment grid test is the one worth explaining. An earlier draft built the
grid as np.arange(0, UPPER_LIMITING_AGE + 1) rather than
np.arange(0, UPPER_LIMITING_AGE - x + 1), running payments for a 65 year old to
age 185. Summing survival over 0 to 55 and over 0 to 120 gives the identical
float64 result, because terms beyond about t = 60 underflow to zero, so the bug
returned the correct number on every input and would have survived any value
based check. The test instead compares against a sum over an independently
constructed 56 element grid, at a zero discount rate so the annuity collapses to
that sum, and hard codes the 56 rather than deriving it from UPPER_LIMITING_AGE,
so changing the terminal age forces a deliberate change to the test.

Decisions D21 to D23 added, flags F21 to F24 added.

### Day 11, Friday 8 August, reallocated

Day 11 and Day 12 were swapped. Day 11 was scheduled as a buffer and Day 12 work
was brought forward into it, because Sunday 9 August is a wedding. Sunday
becomes the buffer instead. The two-day pensioner liability block stays intact,
running Saturday 8 and Monday 10 August. Day 14 onward is unaffected.

### Day 12, Saturday 8 August

Derived and implemented survival_probability_cohort from first principles,
closing F22. Derivation recorded under F22.

Revalidated the Day 10 annuity factor on both bases, male aged 65:

```
  basis                       period               cohort               uplift
  flat 5 per cent    11.747146253364836   12.288979603098038   4.612467896856232%
  gilt curve         11.565613695844538   12.037432488233684   4.079496382960346%
```

The flat 5 per cent period figure reproduces Day 10 to seventeen digits.

Three observations from those four numbers. The gilt curve discounts harder than
flat 5 per cent, with period falling 1.5453332546047083 per cent and cohort
2.0469324792510846 per cent on the curve change. The improvement uplift is
0.5329715138958857 percentage points smaller on the gilt curve, because
improvement adds survival mass at long durations and the gilt curve discounts
long durations more heavily. And the improvement effect is more rate-sensitive
than the base liability it sits on, since cohort falls further than period on the
same curve change. That last point predicts a longer liability duration on the
cohort basis than the period basis, to be tested on Days 16 to 17.

Cumulative hazard decomposition at x = 65, t = 20: Makeham term
0.038563644881799294, senescent term 0.6404597002645365. The senescent term is 98
per cent of the total, so over ages 65 to 85 ageing does essentially all the work
and background mortality is a rounding error.

Settled D24 and D25. Resolved F10, F21 and F22. Opened F25, F26 and F27.
Identified F24 as a duplicate of F15 and merged its substance into F15.

Reviewed the whole of this file for consistency. Day references in older entries
were updated to the revised plan, and the status index at the top was added so
that every decision and flag has one place to be looked up. Content was not
rewritten, only reorganised, except where a flag number collision or a
superseded scheduling reference made the original misleading.

Created report/notes_for_report.md and began collecting report material.

### Day 13, Monday 10 August

Built the pensioner liability engine in src/valuation.py: payment_times,
pension_amounts, pensioner_epv, exact_ages and pensioner_liability. Cleared the
Monday decision gate with a total pensioner liability of 51480005.7698302. See the
Checkpoints section.

Created report/notes_for_report.md and seeded it with material from Days 8 to 12,
organised by report section rather than by date.

Three gotchas worth recording.

np.arange with a fractional step accumulates error and its stopping rule becomes
unpredictable. np.arange(0, 55.0, 1/12) returns 660 elements ending at
54.916666666666664, where the correct grid has 661 ending at exactly 55.0. One
payment silently missing at the terminal age. Building integer month indices and
dividing once avoids it, because each value is a single division rather than an
accumulation. Across the range where both agree the largest discrepancy is
7.105427357601002e-15.

An exact whole number age is reachable and is not evidence of a data problem.
Ages are integer days divided by 365.25, and 365.25 * 4 = 1461 exactly, so ages
that are multiples of four years land on whole numbers. Across the pensioner range
the probability for a given member is 0.0007065265389031175, giving an expected
0.3532632694515588 across 500 members and a 0.2976954402207945 chance of at least
one. An assertion that no age is whole would fail on correct data roughly three
times in ten.

pandas 3.0.2 read_csv with parse_dates returns datetime64[us], not
datetime64[ns]. The column built in memory by membership.py is nanosecond, because
it comes from to_timedelta arithmetic. Both are genuine datetimes and nothing
downstream depends on the resolution, but a dtype check must use
pd.api.types.is_datetime64_any_dtype rather than comparing against a literal.

Membership figures for the report: 500 pensioners, mean age 74.45756057494867,
minimum 65.07597535934292, maximum 95.31279945242984, split 324 male and 176
female, a male proportion of 0.648 against the 0.65 parameter in D7. Total
pensioner pension in payment 4569142.85.

Settled D26 and D27. Resolved F23 for pensioners and F28. Partially resolved F12.
Opened F29 and F30.