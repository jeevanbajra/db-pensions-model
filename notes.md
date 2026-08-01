√# Project notes: UK DB Pension Funding and Longevity Model

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
  entry-point error line. This is cosmetic noise, not a failure.
  Solving is slower as a result. Not worth repairing before deadline.
- `requirements.txt` deliberately left empty until Day 24, when it will
  be generated from the packages actually used.

## Repository

- GitHub: `jeevanbajra/db-pensions-model` (public)
- `data/raw/` is gitignored in full. `data/processed/` is gitignored
  except for `members.csv`, which is committed (see D9)
- Structure: `src/` (modules), `notebooks/` (exploration),
  `dashboard/` (Streamlit app), `tests/`, `data/`
- `.gitkeep` files exist in the empty directories because git tracks
  files, not folders

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
- **Used for:** Lee-Carter improvement projection (Days 7 to 9)
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
  published ex(65) validation check (Day 6)

### 3. Bank of England nominal gilt curve
- **File:** `data/raw/GLC_nominal_daily_current_month.xlsx`
- **Source:** bankofengland.co.uk/statistics/yield-curves
- **Downloaded:** 30 July 2026
- **Curve:** Government Liability Curve, nominal
- **Sheet used:** `4. spot curve` (also keeping `2. fwd curve` for
  the beyond-40-year extrapolation)
- **Grid:** 0.5 to 40 years in 0.5-year steps; rows are dates
- **Coverage in file:** 20 business days, 1 to 28 July 2026
- **Units:** percent, continuously compounded, annual basis
- **Used for:** discounting (Days 10 to 11)

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
- **Used for:** deriving the CPI assumption (D8), and potentially a full
  inflation term structure (F10)

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

### D1: Population, United Kingdom (29 July)
Both mortality sources are UK-wide. HMD also publishes England and Wales
separately, but mixing an E&W improvement trend with a UK base table
would be inconsistent. UK chosen for consistency across both sources.

### D2: Base mortality period, 2022-2024  [CONFIRM]
Most recent available. Excludes 2020 and 2021, which carry severe
pandemic excess mortality and would build a one-off shock into a
long-run assumption.
Rejected: `2019-2021` and `2020-2022`, worst pandemic contamination.
Rejected: `2017-2019`, clean pre-pandemic, but a base table centred
on 2018 is eight years stale by the valuation date.
Caveat: 2022 mortality was still somewhat elevated. Accepted, flagged
in Limitations.
Planned sensitivity: re-run with `2017-2019` once the engine works and
report the difference in funding ratio (Day 22 stress testing).

### D3: Valuation date, 28 July 2026  [CONFIRM]
Latest gilt curve available in the downloaded file. All discounting
uses the spot curve as at this date.

### D4: Raw data gitignored (29 July)
HMD terms of use do not permit redistribution, and committing their
data to a public repo would constitute exactly that. Also avoids
permanent repo bloat. README must therefore give full retrieval
instructions for all four files.

### D5: Discounting convention, continuous  [see F1]
BoE rates are continuously compounded, so v(t) = exp(-y(t) * t) with
y in decimal. Discounting directly in the source convention rather
than converting to annual effective, to minimise conversion steps.

### D6: Gompertz-Makeham fitting range, ages 50 to 100  (Day 4)
Log-mortality plot (2022-2024, ONS) is near-linear from roughly age 35
onwards, confirming exponential growth in the senescent range.
Below about 35 the curve is dominated by infant mortality and the
accident hump (ages 18 to 25, pronounced in males), which GM cannot
represent.
Chose 50 rather than 35 as the lower bound because scheme liability is
concentrated at ages 55+; fitting over the wider range trades accuracy
where it matters for accuracy where it does not.
Upper bound 100 is the limit of ONS data.

### D7: Scheme design (31 July)
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
inert under the central assumption and only earns its place in the Day
22 stress test, where a 6% inflation scenario shows how much the cap
protects the scheme.

**Normal retirement age.** 65 for all members. The most common scheme
NRA, and it keeps deferreds uniform. Not to be confused with State
Pension Age, which is moving to 67 and 68; a scheme's NRA is set by its
own rules. Kept as a column despite every value being identical, because
Day 22 will want to stress it and a column is trivial to vary where a
hardcoded constant is not.

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
complexity in the cashflow engine, due Days 12 to 13.

### D8: CPI assumption, 3.0% a year (31 July)
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

### D9: Reproducibility and committing the generated data (31 July)
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

### D10 (1 Aug 2026): Upper limiting age of 120

ONS data stops at age 100. Options were to let the fitted GM curve extrapolate
beyond 100, or impose an upper limiting age forcing survival to zero. Chose
both: extrapolate GM from 100 to 120, terminal age 120.

Justification:
- Immateriality. Survival from 65 to 100 is roughly 4 per cent male and 9 per
  cent female. Discounting 35 years at 5.5 per cent continuously compounded
  gives exp(-0.055*35) = 0.146. A pound payable at 100 is worth under a penny
  today. Ages 100 and above contribute a few tenths of one per cent of total
  liability.
- The Day 12 cashflow projection needs a finite terminal age to terminate at
  all. This is the binding reason, not the modelling one.
- Terminal age 100 rejected because the oldest members are aged 100 at the
  valuation date and would be assigned zero liability.
- 120 is the conventional choice and leaves headroom for every member.

### D11 (1 Aug 2026): Fit to ln(mu) rather than mu

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

### D12 (1 Aug 2026): Separate fits by sex

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

### D13 (1 Aug 2026): Scope reduction

The original plan contained no buffer days and assumed full days of work.
This was not sustainable alongside graduate applications opening late August.
Revised plan (Project_Plan_Revised.md) cuts three items and adds four buffer
days. Driver was time pressure, not technical difficulty.

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

---

## Flags: issues to handle on a specific day

### F1: BoE rates are continuously compounded  (Days 10 to 11)
The original plan specified v(t) = 1/(1+y(t))^t, which is the annual
effective form and is WRONG for this data.
Correct: v(t) = exp(-y_c(t) * t), or convert first via
y_a = exp(y_c) - 1 and then use the plan's formula.
Both give identical discount factors; the conversion is per maturity.
Size of error if unfixed: discount factors overstated about 1.6% at 20
years, about 3.2% at 40 years. Liabilities overstated about 1.5%
overall.
Rates in the spreadsheet are percentages, so divide by 100 first.

### F2: Convention trap in the reconciliation  (Days 12 to 13)
The hand-calculated annuity check must state its own compounding
convention explicitly. If the two sides disagree on convention they
will not reconcile, and the discrepancy will look like a mortality bug.

### F3: HMD file parsing  (Day 7)
- Whitespace-delimited text, two lines of preamble before the headers
- Final age is the string `110+`, so Age will not parse as numeric
- Missing values are `.` not blank (one at male 110+, 2022)
All three fail silently. Pandas will load text where numbers are
expected and the error will surface somewhere unrelated.

DEFERRED (Day 4): Lee-Carter cut from scope, see D13.

### F4: Restrict Lee-Carter fitting window  (Day 7)
File starts 1922. Wars and the 1920s contain violent mortality spikes
unrelated to the long-run improvement trend. Fit from roughly 1970
onwards. State the chosen window in the report.

DEFERRED (Day 4): Lee-Carter cut from scope, see D13.

### F5: Gilt curve parsing and shape  (Day 10)
- Maturities sit on row 4; a junk `#VALUE!` row follows
- One maturity missing on 28 July, confirmed as the 0.5-year point
  (BoE: available range depends on which instruments had reliable
  prices). Handle gaps, do not assume a complete row
- Long end slopes DOWNWARD: curve peaks around 5.77% in the mid-20s,
  20y spot about 5.70%, 40y about 5.49%. This is real market structure,
  not a data error
- CONFIRMED 30 July. Consequence for extrapolation: on a
  downward-sloping segment the instantaneous forward rate sits BELOW the
  spot rate, so holding the forward flat beyond 40 years makes the
  extrapolated spot curve continue to fall. It does not level off at
  5.49%. Expected behaviour, not a bug. Read the 40-year forward from
  sheet `2. fwd curve` rather than assuming it resembles the 40-year spot

### F6: Projection base year mismatch  (Day 9)
HMD data ends 2022; the 2022-2024 base table is centred on 2023.
State explicitly which year improvements are projected from.

STILL LIVE, reworded (Day 4). Originally flagged the gap between HMD
ending 2022 and the 2022-2024 base table centred on 2023. With Lee-Carter
cut, this now applies to the constant improvement factor: the report must
state explicitly that improvements are projected from the 2023 base year.


### F7: ONS sheet duplicate column names  (Day 4)
Males and females share a single header row, so pandas appends `.1`
to the female columns (`age.1`, `mx.1`, and so on) when reading H:M.
Columns must be renamed after loading. Will recur when
`src/mortality.py` re-reads this sheet.

RESOLVED (Day 4). Handled by reading the male and female blocks
separately with usecols="A:F" and "H:M", then assigning .columns directly,
so the duplicate .1 names never appeared. Note this method is positional and
silent: it relies on both blocks sharing the same column ordering, which was
verified rather than assumed.

### F8: README with data retrieval steps  (Day 24)
No README in the repo yet, and D4 commits to one giving full retrieval
instructions for all four data files, including the BoE renaming
convention.

### F9: HMD outputs in committed notebooks  (Day 7)
Keep displayed HMD extracts small: heads, shapes, plots. Do not commit
outputs containing large blocks of the raw matrix. D4's
non-redistribution reasoning applies to notebook outputs, not just to
`data/raw/`.

F9: DEFERRED (Day 4): Lee-Carter cut from scope, see D13.

### F10: Use the implied inflation term structure  (Days 10 to 11)
Stretch goal. The inflation file (data source 4) has the same five-sheet
layout as the nominal file, so the discounting parser can be pointed at
it with little extra work. Inflating each year's cashflow at that year's
implied rate, rather than at a flat 3.0%, moves the report from
"inflation was assumed" to "inflation was derived from market data at the
valuation date". Watch that `4. spot curve` starts at 2.5 years, not 0.5.

### F11: Deployed dashboard cannot read gitignored raw data  (Day 20)
Streamlit Cloud builds from the GitHub repo, so at runtime it can only
see committed files. The ONS, HMD and BoE files are gitignored and
always will be. The dashboard must therefore read small committed
derived artefacts from `data/processed/` (fitted GM parameters, the
projected mortality table, the discount curve) rather than reprocessing
raw data on every page load. Faster as well.
Fitted parameters are derived work and committing them should be fine. A
full projected mortality table sits closer to the line: re-read the HMD
terms before committing anything mortality-derived.

### F12: Reading `members.csv` back  (Day 12)
CSV stores no type information. `date_of_birth` will arrive as text
unless the file is read with `parse_dates=["date_of_birth"]`. Silent
until date arithmetic fails somewhere unrelated.

### F13: Independent random streams  (stretch, no fixed day)
`rng.spawn()` gives each component of the generator its own independent
stream, so adding or reordering a draw in one place does not disturb the
numbers everywhere else. A genuine improvement over the single shared
sequence currently used, and a good thing to be able to point at. Not
worth the refactor unless there is spare time near the end.

### F14 (1 Aug 2026): Spyder kernel will not start

Spyder launches but the IPython console fails with "An error occurred while
starting the kernel", showing the conda-libmamba-solver entry point error
(module libmambapy has no attribute QueryFormat). Spyder appears to treat
unexpected output on the kernel startup stream as a failure. The same message
is harmless on the command line.

Checked and ruled out: which spyder gives the environment's own binary, and
spyder-kernels 3.1.5 is installed in the environment.

Root cause is the conda-libmamba-solver breakage deferred in Environment
notes. Not repaired: it is a conda dependency untangle with no bearing on
the model.

Workaround: editing src modules in the JupyterLab text editor and testing
in notebooks/scratch.ipynb with %autoreload 2. scratch.ipynb is gitignored
as a workbench rather than a deliverable.


---

## Limitations
_Accumulating for the report's limitations section (Day 25)._

**Data and mortality basis**
- HMD data ends 2022; valuation date is July 2026. Four-year gap
  between the latest observed mortality and the valuation.
- Base table period includes 2022, which had somewhat elevated
  mortality. Not fully clean of pandemic effects.
- National population mortality used throughout. Real DB schemes use
  scheme-specific or SAPS tables; pension scheme members are typically
  lighter-mortality than the general population.
- ONS life table ends at age 100. Fitted GM curve must be extrapolated
  beyond, or an upper limiting age imposed. Decision required Days 4 to 5.

**Financial assumptions**
- Gilt curve published only to 40 years. Cashflows run well beyond
  that for deferred members, so the tail rests on an extrapolation
  assumption rather than market data.
- The BoE implied inflation curve is RPI-based. The CPI assumption is
  derived from it by deduction rather than observed directly.
- Inflation is applied as a single flat rate rather than as the term
  structure the market actually prices (F10).

**Membership**
- Membership data is synthetic, not a real scheme.
- Pensioner ages are drawn from a symmetric normal. A real closed
  scheme's pensioners are a cohort that entered at NRA and has been
  thinned by mortality ever since, so the true right tail is lighter
  than a normal implies.
- Pension amounts are drawn independently of age and of sex. In
  practice longer service correlates with both, and historic earnings
  patterns mean male members tend to hold larger pensions.

**Benefit structure**
- A single benefit tranche is modelled. Pre-1997, 1997-2005 and
  post-2005 accrual and GMP are not distinguished. This overstates
  increases on older pension and understates the bite of the cap on
  newer pension.
- Death in service is not modelled.
- Early retirement with an actuarial reduction, and late retirement,
  are not modelled.
- The salary link is assumed broken, so actives and deferreds are
  modelled identically. The status split is presented for reporting
  only.
- Spouse mortality is assumed independent of member mortality.
  Couples' mortality is correlated in practice (the widowhood effect is
  well documented), so this slightly understates the joint liability.
- Gompertz-Makeham overstates mortality above roughly age 95, where observed
  mortality decelerates and flattens. Visible in the Day 4 log-mortality plot.
  Overstating mortality understates survival, which understates liability and
  the deficit, so the bias runs the imprudent way. Quantifiable on Day 15 by
  comparing total liability at terminal ages 110 and 120. The standard fix is
  a logistic blend such as Kannisto above the oldest ages; noted as further
  work rather than implemented.

- The Makeham constant A is weakly identified over the fitted range 50 to 100,
  since the senescent term dominates it throughout. See D12.

- Force of mortality assumed constant within each year of age, giving
  mu_x = -ln(1 - q_x). This is an approximation and is stated in the report.
  It also means the fitted mu is closest in interpretation to mu at age x+0.5
  rather than exactly x.

---

## Log

**29 July.** Registered with HMD (instant, no approval delay).
Created `pensions` conda environment; hit the libmamba solver bug,
resolved with classic solver. Built folder skeleton, wrote `.gitignore`,
first commit, pushed to GitHub successfully.

**30 July.** Downloaded all three datasets into `data/raw/`.
Confirmed `.gitignore` works: repo shows four folders, no data. Spotted
the continuous compounding error in the original plan (F1).
Pushed the notes after renaming the BoE file to remove spaces.

**30 to 31 July.** Day 2. Both datasets loaded into clean DataFrames.
ONS validated against published e0 (79.12 M, 83.02 F). Log-mortality
plot near-linear from about age 35; accident hump visible at 18 to 25,
larger for males; M/F lines parallel above 35 (constant ratio). Gilt
curve reshaped to 79 maturities, humped with inverted long end. F5 and
F7 both confirmed as predicted.

**31 July.** Day 3. Settled the full scheme design (D7), the CPI
assumption (D8) and the reproducibility approach (D9). Added the BoE
implied inflation file as data source 4 after checking what else was in
the downloaded ZIP; it showed the working assumption of 2.5% CPI to be
roughly 0.75 percentage points below market, which would have understated
the liability materially. Wrote `src/membership.py`, the first module in
`src/`: four functions plus a run section, generating 1,000 members with
a total of 8.13m pounds of annual pension. Committed the generated
`members.csv` alongside it. Also fixed a `.gitignore` negation pattern
that was silently doing nothing because of an inline comment.

**1 August.** Day 4: Settled D10, D11, D12 before coding. Revised project plan
to a sustainable scope (D13). Wrote src/mortality.py with load_ons_table,
add_force_of_mortality, restrict_to_fit_range and plot_log_mortality.
Validated against Day 2: e(0) of 79.12 male and 83.02 female reproduced
through a different code path.
**1 August.** Day 4: Spyder kernel failed (F14), switched to JupyterLab text
editor plus scratch notebook. Log-mortality plot over 50 to 100 confirms
near-linear and near-parallel lines, supporting both the GM law and separate
fits by sex, with visible flattening above 95.
