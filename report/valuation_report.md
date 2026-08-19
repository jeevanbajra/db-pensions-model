## Purpose and Scope 

This report presents a funding valuation of a defined benefit pension scheme at the 28th July 2026,
discovering whether the assets held are sufficient to meet the pensions promised
and by how much they fall short if not. The position moves with the markets. 
This document is designed to inform trustees and any other person that
may find it necessary to understand the funding position and what it depends on.
In this report I will cover the results of the model including the scheme's liability,
funding position and the sensitivity to the assumptions. Liabilities are discounted 
on the gilt curve at the date previously stated, and mortality from the ONS national
life tables with an allowance for future improvement. All market data, in particular
the gilt curve, is taken from the 28th July 2026. I will also go through my methodology,
assumptions I have used and limitations affecting the model. Every assumption is stated and,
where a choice was made, the effects of the alternative decision is quantified. This is not a
formal actuarial valuation. The membership is synthetic, no advice is being given. There is no
contribution recommendation, no recovery plan, no investment advice and no assessment against
the staturoty funding regime. Full decision log and code in the repository.

## The Scheme

The model values a synthetic scheme of 1,000 members: 500 pensioners already
receiving a pension, 350 deferred members who have left the scheme but not yet
retired, and 150 active members still employed. Active members are financially
identical to deferreds and are routed through the deffered path. Total pension roll is
8,130,201.07 a year.

The membership is generated rather than real, because no genuine scheme data is
publicly available at member level. Ages, pension amounts and sexes are drawn
from distributions chosen to resemble a mature private sector scheme closed to
new entrants: a pensioner population with a mean age in the mid seventies, a
deferred population in the mid fifties, and pension amounts skewed so that a
small number of members hold much larger pensions than the median.

The generator uses a fixed random seed, so the membership is identical every
time the model is run. This matters because a valuation that produced a
different answer on each run could not be checked or reviewed by anyone else.

A mean age of 74.46 at the valuation date, ranging from 65.08 to 95.31. 
The split is 324 male and 176 female. Total pension in payment is 4,569,142.85 a year.

The largest individual pensioner liability is 1,080,655.14, which is 2.10 per cent
of the pensioner total but only 1.06 per cent of the liability scheme of 102 million. 
The ten largest together account for 7.40 per cent of the scheme. With 500 pensioners
a perfect scheme would put 0.2 per cent on each, but the highest is 2.10 which is 10.5
per cent higher than the mean pensioner liability of 102,960. The median is 65,035.
The scheme is therefore not heavily exposed to the longevity of any one
individual. 

## Assumptions

Liabilities are discounted at the nominal gilt spot curve at the valuation date, using the Bank of 
England nominal GLC 28th July 2026. The Bank of England publishes on a continuously compounding 
basis so the discount factor is given as: v(t) = exp(-y(t) * t). I checked this convention against 
the data: under continuously compounding the instantanious forward satisfies f(t) = y(t) + t*y'(t) 
and a one year finite difference at 40 years gives 3.698 per cent against the published 3.641, 
which was justifiable to confirm the convention is the one to go forward with.

I interpolated linearly on spot rates between published points, holding y(1) flat under one year.
This was oppose to a flat forward interpolation, which is linear on log discount factors, and 
would have been more consistent with how I extrapolate beyond 40 years. I tested it across 781 
maturities from 1 to 40 years and the maximum difference between the the two is 0.647 basis points 
at t=1.2 which is worht 0.0084 per cent on the discount factor at that point. I chose linear on
spot as one simple stated method is easier to defend than two and the difference is minute.

One feature of the curve is the fact the long end is inverted: at 40 years, the instantaneous 
forward rate is 3.6414 per cent agaisnt a spot rate of 5.4880 per cent. Forward rates below spot 
rates at the long end looks like a data error, even though it is not. The spot rate curve stops 
rising as soon as the forward rate crosses it at 27 years where the spot peaks at 5.8092 per cent 
and forward at 5.8051 per cent. This is because a spot rate is the averafe of the forwards out to 
that maturity. The two curves are consistent with each other, which is evidence that the data is 
internally coherent.