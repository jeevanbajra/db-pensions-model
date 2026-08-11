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

Nothing yet.

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

---

## Methodology

Nothing yet.

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

---

## Sensitivity Analysis

Nothing yet.

---

## Limitations and Further Work

See the Limitations section of notes.md, which is already structured for this.
Only additions and rewordings go here.

---

## Phrasings worth keeping

Nothing yet. Sentences that came out well in conversation and should survive
into the final draft.

---

## Open questions for the report

- Whether to quote both period and cohort life expectancy at 65, and present the
  gap as longevity improvement expressed in years (D15 note, Day 15).
- How much of the D19 extrapolation section should be prose and how much a
  table of the three variants (F20, Day 15).