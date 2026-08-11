# Material for the trustee valuation report

Collected as the work happens, not written up at the end. Each entry sits under
the report section it belongs to. Entries are raw material and are not yet in
final wording.

Report sections: Executive Summary, Membership Data, Assumptions, Methodology,
Results, Sensitivity Analysis, Limitations and Further Work.


---

## Executive Summary

Nothing yet. Written last.

---

## Membership Data

### Valuation date

All figures are at 28 July 2026. Market data is taken at that date and member
ages are calculated to it.

### The scheme

The model values a synthetic scheme of 1,000 members: 500 pensioners already
receiving a pension, 350 deferred members who have left the scheme but not yet
retired, and 150 active members still employed. Total pension roll is
8,130,201.07 a year.

The membership is generated rather than real, because no genuine scheme data is
publicly available at member level. Ages, pension amounts and sexes are drawn
from distributions chosen to resemble a mature private sector scheme closed to
new entrants: a pensioner population with a mean age in the mid seventies, a
deferred population in the mid fifties, and pension amounts skewed so that a
small number of members hold much larger pensions than the median.

The generator uses a fixed random seed, so the membership is identical every
time the model is run. This matters because a valuation that produced a
different answer on each run could not be checked by anyone else.

### Pensioner population

The scheme has 500 members in payment, with a mean age of 74.46 at the
valuation date, ranging from 65.08 to 95.31. The split is 324 male and 176
female. Total pension in payment is 4,569,142.85 a year.

### Concentration

The single largest pensioner liability is 1,080,655.14, which is 2.10 per cent
of the pensioner total. The ten largest together account for 14.66 per cent.
The scheme is therefore not heavily exposed to the longevity of any one
individual. This is worth stating because it is a natural question for a
scheme of this size, and here the answer is reassuring.


---

## Benefits

### Benefits valued

The scheme pays a pension for life from age 65, increasing each year in payment
in line with CPI capped at 5 per cent. Deferred pensions revalue at the same
rate between the valuation date and retirement.

Nothing else is valued. There is no benefit on death before retirement, no
option to take part of the pension as a cash lump sum, and no early or late
retirement. Every member has a normal retirement age of 65.

The spouse's pension is not modelled member by member. Instead an allowance is
made at scheme level, described under Assumptions.

---
## Assumptions

### Discount rate

The gilt spot curve peaks at 5.8092 per cent at 27 years, and 27 years is
exactly where the instantaneous forward curve crosses it: spot 5.8092, forward
5.8051. This is not a coincidence. A spot rate is an average of forward rates
out to that maturity, so the average stops rising precisely when the value being
averaged into it stops exceeding it. Worth stating because it demonstrates the
data is internally coherent rather than broken, and because the inverted long
end looks like an error to a reader who has not seen this.

### Proportion, and where the judgement actually sits

The interpolation choice (D16) moves a discount factor by 0.0084 per cent. The
extrapolation choice above 40 years (D19) moves one by roughly 100 per cent.
Four orders of magnitude apart. One deserves a sentence, the other a section.
This is the organising principle for the assumptions section: length should
track materiality, not the effort that went into the decision.

### Mortality

Over ages 65 to 85 the senescent Gompertz term accounts for 98 per cent of the
accumulated force of mortality: 0.6405 against 0.0386 for the Makeham constant.
Ageing does essentially all the work at pensioner ages and background mortality
is a rounding error. Useful for explaining in plain words what the three fitted
parameters are actually doing.

### Pension increases

CPI at 3.0 per cent was derived from market data, not assumed. The BoE implied
inflation curve sat at 3.2 to 3.3 per cent across the relevant maturities, less
a residual RPI to CPIH wedge and an inflation risk premium. Stating the
derivation matters more than the number, because different consultancies would
land anywhere between 2.8 and 3.2 per cent.

### Payment frequency

Pensions are modelled as payable monthly in advance, matching the way the
scheme actually pays them, rather than annually with a frequency adjustment
applied afterwards. The conventional adjustment of adding roughly 11/24 to an
annual-in-advance annuity was computed as a check on the direct calculation
rather than used in place of it. Modelling the payments directly costs nothing
in a vectorised implementation and removes an approximation that would
otherwise need defending.

### Discount rates beyond 40 years

The Bank of England publishes gilt yields out to 40 years. The youngest member
of this scheme is 43, and if she lives to 120 the scheme will still be paying
her in 77 years time. Nearly half of that discount period is beyond anything
the market tells us, and something has to be assumed.

The model holds the forward rate flat at its 40 year value of 3.64 per cent.
In plain terms: the market's view of the interest rate available in year 40 is
assumed to be the rate available in every year after that.

Two alternatives were considered. Holding the spot rate flat instead is
simpler, but it implies the one-year rate available in year 40 jumps from 3.64
per cent to 5.49 per cent for no reason, which is not a view anybody holds.
Converging to an ultimate forward rate, as insurers do under Solvency II, was
rejected because it is not how UK defined benefit funding valuations are done.

The choice matters more than any other assumption in the model. At the longest
horizon of 77 years, one pound is worth 2.92 pence under the chosen method and
1.48 pence under a flat spot rate, a factor of two on the same payment. The
offsetting point is that almost nobody survives to 120, so the payments being
discounted at those horizons are tiny. The effect on the total liability is
quantified under Sensitivity Analysis.

### Mortality improvement

Death rates have fallen steadily for decades and are assumed to keep falling.
The model reduces mortality at every age by 1.25 per cent a year from the
valuation date.

This means a member reaching 65 in twenty years time faces lower mortality
than a member who is 65 today. Valuing everyone on today's rates would
understate the cost of the scheme, and for the deferred members it would
understate it substantially, as shown under Results.

A flat improvement rate is a simplification. Published projections such as the
CMI model vary improvement by age and by year and would be used in practice.

### Terminal age

The model assumes no member survives beyond age 120. Some cut-off is needed to
make the calculation finite. The chance of reaching 120 under this basis is
around three in a billion, so the choice has almost no effect on the answer.

---

## Methodology

### Mortality

Published mortality tables give a death rate for each whole age. Working
directly from those figures is awkward, because a valuation needs mortality at
exact ages such as 74.46 and over fractions of a year.

The model therefore fits a smooth curve through the published rates. The curve
used is Gompertz-Makeham, which has two parts: a constant term representing
causes of death that do not depend on age, and a term that rises geometrically
with age representing the effects of ageing. Three parameters are fitted
separately for men and women, using ONS national life table data for 2022 to
2024.

Fitting a curve of this shape is standard actuarial practice and is called
graduation. It also makes the assumption visible: the fitted parameters state
in three numbers what the model believes about mortality, which a table of a
hundred rates does not.

### Discounting

Future pension payments are discounted using the Bank of England nominal gilt
spot curve at the valuation date, which is a market-based rate rather than an
assumed one.

The published curve runs from 1 year to 40 years. Rates between published
points are interpolated. Rates beyond 40 years have to be extrapolated, and
that choice is discussed under Assumptions because it is the single largest
judgement in the model.

### Valuing members who have not yet retired

The benefit of a member not yet in payment is valued as a single sum over every
future payment date, from retirement age to the terminal age of 120. Each term
is the pension payable at that date, multiplied by the chance the member lives
to receive it, multiplied by the discount factor at that date.

Two different clocks run through that calculation and they cannot be swapped.
Pension increases are counted from the retirement date, because that is when
the pension starts being paid. Survival and discounting are counted from the
valuation date, because that is when we know the member's age.

The same benefit can also be written as an annuity value at retirement,
discounted back to today and weighted by the chance of surviving to retirement.
Both versions were built and they agree to sixteen significant figures.

### Active members

Active members are valued as deferreds. Under the rules modelled here there is
no future accrual, so an active member and a deferred member of the same age
with the same accrued pension have exactly the same benefit. Both are put
through the same calculation on purpose, and a test checks that the actives
have not been dropped.

---

## Results

### Mortality improvement is more rate-sensitive than the liability it sits on

Moving from a flat 5 per cent discount curve to the actual gilt curve reduces
the period-basis annuity factor by 1.5453 per cent and the cohort-basis one by
2.0469 per cent. The cohort figure falls further because improvement adds
survival at long durations, and long durations are exactly what a higher
discount curve suppresses.

Consequence: the improvement uplift is 4.6125 per cent on a flat 5 per cent
curve but only 4.0795 per cent on the gilt curve, a gap of 0.5330 percentage
points. The value of longevity improvement is not a property of the mortality
basis alone, it depends on the discount curve it is measured against.

Predicts a longer liability duration on the cohort basis than the period basis,
which is the correct basis showing the scheme to be more interest-rate sensitive
rather than less. To be confirmed on Days 16 to 17.

### Pensioner liability

Total pensioner liability is 51,480,005.77 against pension in payment of
4,569,142.85, a ratio of 11.27 pounds of liability for each pound of annual
pension.

The ratio varies substantially by age and sex. The youngest male pensioner at
65.08 carries 15.03 pounds per pound of pension, the oldest at 95.24 carries
2.52. Mean values are 10.49 male and 11.78 female, a ratio of 1.12. That
difference is entirely the mortality basis: the same benefit costs 12 per cent
more for a woman than for a man of the same age because she is expected to
receive it for longer.

### The cost of a pension at retirement is not the cost of a pension in payment

A pension coming into payment in twenty years time is worth more, pound for
pound, than the same pension coming into payment today. For a male member aged
45 at the valuation date, one pound a year payable from age 65 is worth 16.06
at the point of retirement, against 15.07 for the same benefit valued for a man
who is 65 today. A difference of 6.57 per cent.

The gap decomposes into two effects working against each other:

  mortality improvement to 2046      +7.48 per cent
  forward rather than spot rates     -1.96 per cent
  interaction                        +1.14 per cent
  total                              +6.57 per cent

The first is the cohort basis doing its work. A man reaching 65 in 2046 is
expected to live materially longer than a man who is 65 in 2026, and his
pension costs correspondingly more.

The second is a feature of the current gilt curve. The deferred member's
pension is discounted at forward rates from year twenty onward, and those
forwards begin at 6.36 per cent against a twenty year spot rate of 5.70 per
cent. The early years of his retirement are therefore discounted harder than
the early years of a current pensioner's.

The interaction term is positive because both effects raise the value of
payments far in the future, and applying them together gains more than applying
them separately.

The practical consequence is that a scheme cannot value its deferred members by
applying a current pensioner annuity factor to them. Doing so here would
understate the deferred liability by 6.17 per cent. The error is not a small
approximation, it is the answer to a different question: the value of that
benefit to a person who is 65 today rather than to the member in question.

### Scheme liability

Before allowance for spouses' pensions, total liability is 92,287,196.64,
comprising 51,480,005.77 for members in payment and 40,807,190.87 for members
not yet in payment. Against a total annual pension roll of 8,130,201.07 that is
11.35 pounds of liability for each pound of pension.

Members not yet in payment account for 44.22 per cent of the liability and
43.80 per cent of the pension roll. The near equality is a coincidence of this
particular membership rather than a structural result. Those members are
younger, which raises their liability per pound of pension relative to
pensioners, but their pensions are also further from being paid, which lowers
it, and on this data the two effects happen to offset.

---

## Sensitivity Analysis

Nothing yet.

---

## Limitations and Further Work

See the Limitations section of notes.md, which is already structured for this.
Only additions and rewordings go here.

### The membership is not real

Every conclusion about this scheme is a conclusion about a set of members drawn
from assumed distributions. The methods are the point, not the numbers.

### One inflation rate, not a curve

Pension increases and deferred revaluation both use a flat 3.0 per cent, taken
from market implied inflation at the relevant maturities. Market inflation
expectations are not flat across terms, and a real valuation would use the
whole curve. Tested as a sensitivity rather than built into the main result.

### Deferred period measured in exact years

Statutory revaluation of deferred pensions operates in complete years from the
date of leaving. The membership data modelled here carries no date of leaving,
so revaluation is applied over the exact period from the valuation date to
normal retirement age. For the youngest member this overstates the revaluation
factor by 2.28 per cent relative to rounding down to complete years. A real
valuation would use the actual leaving dates.

### Benefit simplifications

A real scheme would have several tranches of pension with different increase
rules, members retiring early or late, and a proportion taking cash at
retirement. This model has one tranche, one retirement age and no cash option.
Each of these would change the liability, and the cash option in particular
usually reduces it.

### No death benefits before retirement

A member who dies before 65 is assumed to produce no payment at all. Real
schemes generally pay a spouse's pension or a return of contributions. This
understates the liability by a small amount.

---

## Phrasings worth keeping

Using a current pensioner annuity factor for a deferred member does not produce
a slightly wrong answer. It produces the correct answer to a different
question.

---

## Open questions for the report

- Whether to quote both period and cohort life expectancy at 65, and present the
  gap as longevity improvement expressed in years (D15 note, Day 15).
- How much of the D19 extrapolation section should be prose and how much a
  table of the three variants (F20, Day 15).