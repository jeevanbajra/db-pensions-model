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

### Spouses' pensions

On the death of a member, half of their pension continues to a surviving
spouse for the rest of that spouse's life, increasing on the same basis as
the member's own pension did.

Three assumptions are needed and none of them is observable in the data.
The spouse is assumed to be of the opposite sex and three years younger than
a male member, three years older than a female member. Eighty per cent of
male members and seventy per cent of female members are assumed to leave a
surviving spouse.

The first two are long standing conventions. The proportions are chosen
figures in the range used in practice rather than anything derived from
this scheme, and a real valuation would set them from the scheme's own
experience. They enter as a straight multiplier, so the liability moves in
exact proportion to them: reducing the male figure from 80 to 75 per cent
reduces the male spouse liability by 6.25 per cent and changes nothing else.

### Assets

The scheme is synthetic and holds no actual investments, so the asset value
is a chosen input rather than a measurement. It is set at 92.5 per cent of
the central liability, giving 94,317,503.07. Once set it is a fixed amount
in pounds and does not move when an assumption changes, which is what makes
the funding ratio meaningful under stress.

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

### Valuing the spouse's pension

A payment reaches the spouse at a given date only if two things are true at
once: the spouse is still alive, and the member has died. The probability of
both is taken as the product of the two, which assumes the lives are
independent.

For a member not yet retired there is a further condition. No benefit is
payable on death before retirement, so the member must first survive to
retirement and then die. The probability of a payment is the chance of
reaching retirement less the chance of still being alive at the date in
question.

The amount is straightforward. Because the spouse's pension inherits the
member's increase history rather than starting afresh at the date of death,
it is always exactly half of what the member's own pension would have been
at that date.

### Stress testing

Each stress recalculates the whole liability with one assumption changed and
everything else held. Assets are held fixed in pounds throughout, so the
funding ratio moves with the liability.

Four assumptions are stressed: the level of gilt yields, the general level
of mortality, the rate at which mortality is assumed to improve, and price
inflation. The interest rate stress moves the whole yield curve in parallel,
including the extrapolated portion beyond 40 years.

### Liability duration

Duration is the standard measure of how sensitive a liability is to interest
rates. It is quoted in years because the sensitivity of a single future
payment is its own maturity, and a stream of payments behaves like the
average of its payment dates weighted by present value. A duration of
fifteen years means a one percentage point fall in yields costs roughly
fifteen per cent.

It is measured here by moving the whole curve up and down by one basis point
and observing the response, rather than from a formula. This makes no
assumption about the shape of the cashflows and picks up the extrapolation
beyond 40 years automatically.

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

CONFIRMED (Day 16): cohort duration 14.42 years against period 13.32, longer
by 1.10 years or 8.27 per cent.

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

### The spouse's pension costs three times as much for a man as for a woman

Valued for each member individually, the spouse's pension adds 12.60 per
cent to the cost of a male pensioner's benefit and 3.96 per cent to a female
pensioner's, a ratio of 2.92.

The reason is entirely the age difference and the difference in life
expectancy. A male member typically has a younger wife who outlives him by a
decade, so the pension continuing to her is expensive. A female member
typically has an older husband who dies first, so the benefit often never
comes into payment at all.

The effect is visible before any money enters the calculation. Taking only
the probability that a payment is due at each date, the figure for a male
aged 65 peaks at 0.379 some 24 years out, against 0.150 at 19 years for a
female aged 65. Across the whole payment period the male figure is 2.89
times the female one, and the 2.92 in the liability barely moves from it.

Across the scheme as a whole, spouses' pensions add 10.49 per cent, or
9,677,671.55, bringing the total liability to 101,964,868.19. A scheme level
percentage of that kind is a blend of two very different numbers and it is
worth saying so, because the split of a membership between men and women
changes it materially.

### Funding position

Total liability 101,964,868.19 against assets of 94,317,503.07. A funding
level of 92.5 per cent and a deficit of 7,647,365.11, set against an annual
pension roll of 8,130,201.07.

### Sensitivity

  Stress                  Liability      Change      Funding level
  Central                101,964,868      0.00%          92.5%
  Yields fall 1%         118,470,979    +16.19%          79.6%
  Yields rise 1%          88,750,330    -12.96%         106.3%
  Mortality 10% heavier   98,729,053     -3.17%          95.5%
  Mortality 10% lighter  105,528,000     +3.49%          89.4%
  Improvement 1.75% pa   105,327,978     +3.30%          89.5%
  Inflation +0.5%        106,948,622     +4.89%          88.2%

Interest rates dominate. A one point fall in yields costs sixteen per cent of
the liability, five times the effect of a ten per cent change in mortality
and three times the effect of half a point on inflation.

### The scheme loses more from falling yields than it gains from rising ones

The yield stresses are not symmetric. A one point fall costs 16.19 per cent
and a one point rise saves 12.96 per cent, a gap of 3.23 percentage points
on moves of identical size.

This is convexity, and it is a property of discounting rather than an
artefact of the model. It is also the reason schemes hedge interest rate
risk rather than taking a view on it: the downside is larger than the
upside, so being unhedged is a losing bet even against a rate move that is
equally likely in either direction.

The same asymmetry appears in the mortality stresses, at 0.32 percentage
points, an order of magnitude smaller.

### Allowing for improving mortality makes the scheme more interest rate sensitive, not just more expensive

The liability duration is 14.42 years, meaning a one percentage point fall
in yields costs about 14.4 per cent of the liability.

Valued on current mortality with no allowance for future improvement, the
duration would be 13.32 years. Allowing for improvement lengthens it by 1.10
years, or 8.27 per cent.

The practical consequence matters more than the numbers. A scheme that
valued its members on today's mortality rates would believe its duration was
13.3 years and would hedge its interest rate exposure on that basis, leaving
around eight per cent of that exposure uncovered. The correct basis reveals
more risk rather than less.

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

### Spouses' lives are assumed independent of members' lives

The calculation multiplies the spouse's survival probability by the member's
probability of death, which treats the two lives as unrelated. They are not.
Couples share a household, an income and a way of living, and bereavement
itself raises mortality, so they die closer together than independence
implies.

The effect is that the periods where one is alive and the other is dead are
shorter than modelled, so the true cost of the benefit is lower than the
figure given here. The error is therefore in the conservative direction.
Modelling it properly would require a joint life basis.

### Every member is assumed to have an opposite sex spouse of a fixed age difference

The model assumes one spouse, of the opposite sex, exactly three years older
or younger, and alive at the valuation date. In reality some members are
single, some are widowed, some have a same sex spouse, and the age
difference varies. The proportion married assumption is a crude allowance
for the first two of these and nothing allows for the others.

---

## Phrasings worth keeping

Using a current pensioner annuity factor for a deferred member does not produce
a slightly wrong answer. It produces the correct answer to a different
question.

A scheme that valued its members on today's mortality would believe its
duration was 13.3 years and would hedge accordingly, leaving around eight
per cent of its interest rate exposure uncovered. The correct basis reveals
more risk, not less.

Being unhedged is a losing bet even against a rate move that is equally
likely in either direction, because the scheme loses more when yields fall
than it gains when they rise.

---

## Open questions for the report

- Whether to quote both period and cohort life expectancy at 65, and present the
  gap as longevity improvement expressed in years (D15 note, Day 15).
- How much of the D19 extrapolation section should be prose and how much a
  table of the three variants (F20, Day 15).