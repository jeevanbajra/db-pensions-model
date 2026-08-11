"""
Synthetic membership generator for a closed UK DB pension scheme.

Produces a member-level dataset as at the valuation date, written to
data/processed/members.csv. Scheme is closed to new entrants and to
future accrual; the salary link is broken, so actives and deferreds
are financially identical and the status field is for reporting only.
See notes.md D7 for the scheme design and D9 for the seed.
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Reproducibility (D9). Every random draw must come from this generator.
SEED = 42
rng = np.random.default_rng(SEED)

# Scheme design (D7)
N_PENSIONERS = 500
N_DEFERREDS = 350
N_ACTIVES = 150
MEAN_AGE_PENSIONERS = 72
MEAN_AGE_DEFERREDS = 54
MEAN_AGE_ACTIVES = 56
SD_AGE_PENSIONERS = 8
SD_AGE_DEFERREDS = 7
SD_AGE_ACTIVES = 6
MIN_AGE_PENSIONERS = 65
MIN_AGE_DEFERREDS = 43
MIN_AGE_ACTIVES = 43
MAX_AGE_PENSIONERS = 100
MAX_AGE_DEFERREDS = 64
MAX_AGE_ACTIVES = 64

# Log Normal values (D7)
MEDIAN_PENSIONS_PENSIONERS = 6000
MEDIAN_PENSIONS_DEFERREDS = 3500
MEDIAN_PENSIONS_ACTIVES = 8000
SIGMA_PENSIONS_PENSIONERS = 0.9
SIGMA_PENSIONS_DEFERREDS = 0.9
SIGMA_PENSIONS_ACTIVES = 0.9

# Sex split (D7). Proportion male, by member category.
PROP_MALE_PENSIONERS = 0.65
PROP_MALE_DEFERREDS = 0.55
PROP_MALE_ACTIVES = 0.50

VALUATION_DATE = pd.Timestamp("2026-07-28")   # D3
NORMAL_RETIREMENT_AGE = 65

# Resolve paths relative to this file, not the working directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT_ROOT / "data" / "processed" / "members.csv"

def draw_ages(n, rng, mean, sd, low, high):
    """
    Draw n exact ages from a normal distribution truncated to [low, high].

    Parameters are supplied by the caller so that the same function serves
    all three member categories (D7). The bounds are not arbitrary: the
    lower bound for deferreds and actives follows from the scheme having
    closed to new entrants, and the upper bound for pensioners is the
    limit of the ONS life table.

    Out-of-range values are rejected rather than clipped. Clipping would
    set every low draw to exactly the lower bound, producing an
    artificial spike of members at one age. Rejection preserves the
    shape of the distribution across the retained range.

    Draws are taken 3n at a time and filtered. Roughly 80 per cent
    survive the filter at the parameters used here, so 3n is
    comfortable; the assertion is the tripwire if a future change to the
    parameters makes the filter reject more than expected.

    Note that truncation compresses the spread: the standard deviation
    of the returned ages will be materially below the sd argument
    wherever the bounds sit close to the mean.
    """

    draws = rng.normal(mean, sd, 3*n)
    draws = draws[(draws >= low) & (draws <= high)]
    ages = draws[:n]
    assert len(ages) == n, "the filter rejected more than expected and the oversampling factor needs raising"
    return ages



def ages_to_dates_of_birth(ages, valuation_date):
    """
    Convert exact ages at the valuation date into dates of birth.

    Dates of birth are stored rather than ages because age is a fact
    about a particular date: if the valuation date moves (D3), stored
    ages would silently become wrong while dates of birth stay correct.

    365.25 days per year accounts for leap years. The exact Gregorian
    year is 365.2425 days, so this overstates by roughly 0.0075 days
    per year of age - under a day even for the oldest member.
    """
    return valuation_date - pd.to_timedelta(ages * 365.25, unit="D")



def draw_pension_amounts(n, rng, median, sigma):
    """
    Draw n annual pension amounts in pounds from a lognormal distribution.

    Lognormal rather than normal for three reasons. It cannot produce
    negative amounts. It is right skewed, matching real scheme membership
    where most members hold modest pensions and a small number hold very
    large ones. And it follows from how a pension is calculated: service
    multiplied by accrual rate multiplied by final salary is a product of
    positive quantities, and products of positive quantities tend towards
    lognormal in the same way sums tend towards normal.

    Note the parameterisation. numpy's first two arguments describe the
    underlying normal distribution, not the pension amounts themselves,
    so the first argument is the natural log of the median pension rather
    than the mean pension. Passing a pound amount directly would produce
    nonsense.

    The median is supplied by the caller because it differs by category
    (D7): deferreds left after shorter service and hold the smallest
    pensions, actives were the long stayers at closure and hold the
    largest, and pensioners sit between. Sigma is held constant across
    categories, so all three share the same degree of skew.

    Amounts are drawn independently of age and of sex. Both are
    simplifications recorded in Limitations: in practice longer service
    correlates with both, and historic earnings patterns mean male
    members tend to hold larger pensions.

    No truncation is applied. Very small pensions from short service and
    very large ones from long senior careers are both real features of
    UK DB schemes.
    """
    amounts = rng.lognormal(np.log(median), sigma, n)
    return amounts



def draw_sexes(n, rng, proportion_male):
    """
    Draw n member sexes as "M" or "F".

    Coded "M"/"F" to match the ONS National Life Tables as loaded on
    Day 2, so the mortality lookup joins on this column directly
    without recoding.

    The proportion male varies by category (D7): pensioners 0.65,
    deferreds 0.55, actives 0.50. Pensioners retired from a workforce
    formed decades ago, when full-career scheme membership was heavily
    male; actives are the most recent cohort and are close to even.
    This is worth distinguishing because sex drives the mortality
    basis, and pensioners carry the largest share of the liability.

    Sex is drawn independently of age and pension amount. That is a
    simplification: in practice male members tend to hold larger
    pensions, reflecting historic earnings and service patterns.
    """
    return rng.choice(["M", "F"], size=n, p=[proportion_male, 1 - proportion_male])

if __name__ == "__main__":
    # --- build the scheme ---
    # All draws happen here, in this order. Order matters: the seeded generator
    # produces one sequence, so reordering these calls changes the scheme (D9).
    
    # Pensioners
    ages_p = draw_ages(N_PENSIONERS, rng,
                       mean=MEAN_AGE_PENSIONERS, sd=SD_AGE_PENSIONERS,
                       low=MIN_AGE_PENSIONERS, high=MAX_AGE_PENSIONERS)
    sexes_p = draw_sexes(N_PENSIONERS, rng, PROP_MALE_PENSIONERS)
    pensions_p = draw_pension_amounts(N_PENSIONERS, rng,
                                      MEDIAN_PENSIONS_PENSIONERS, SIGMA_PENSIONS_PENSIONERS)
    dobs_p = ages_to_dates_of_birth(ages_p, VALUATION_DATE)
    
    # Deferreds
    ages_d = draw_ages(N_DEFERREDS, rng,
                       mean=MEAN_AGE_DEFERREDS, sd=SD_AGE_DEFERREDS,
                       low=MIN_AGE_DEFERREDS, high=MAX_AGE_DEFERREDS)
    sexes_d = draw_sexes(N_DEFERREDS, rng, PROP_MALE_DEFERREDS)
    pensions_d = draw_pension_amounts(N_DEFERREDS, rng,
                                      MEDIAN_PENSIONS_DEFERREDS, SIGMA_PENSIONS_DEFERREDS)
    dobs_d = ages_to_dates_of_birth(ages_d, VALUATION_DATE)
    
    # Actives
    ages_a = draw_ages(N_ACTIVES, rng,
                       mean=MEAN_AGE_ACTIVES, sd=SD_AGE_ACTIVES,
                       low=MIN_AGE_ACTIVES, high=MAX_AGE_ACTIVES)
    sexes_a = draw_sexes(N_ACTIVES, rng, PROP_MALE_ACTIVES)
    pensions_a = draw_pension_amounts(N_ACTIVES, rng,
                                      MEDIAN_PENSIONS_ACTIVES, SIGMA_PENSIONS_ACTIVES)
    dobs_a = ages_to_dates_of_birth(ages_a, VALUATION_DATE)
    
    # --- assemble ---
    
    pensioners = pd.DataFrame({
        "status": "pensioner",
        "sex": sexes_p,
        "date_of_birth": dobs_p,
        "annual_pension": pensions_p,
        "normal_retirement_age": NORMAL_RETIREMENT_AGE,
    })
    
    deferreds = pd.DataFrame({
        "status": "deferred",
        "sex": sexes_d,
        "date_of_birth": dobs_d,
        "annual_pension": pensions_d,
        "normal_retirement_age": NORMAL_RETIREMENT_AGE,
    })
    
    actives = pd.DataFrame({
        "status": "active",
        "sex": sexes_a,
        "date_of_birth": dobs_a,
        "annual_pension": pensions_a,
        "normal_retirement_age": NORMAL_RETIREMENT_AGE,
    })
    
    members = pd.concat([pensioners, deferreds, actives], ignore_index=True)
    members.insert(0, "member_id", [f"M{i:04d}" for i in range(1, len(members) + 1)])
    
    # --- storage tidy-ups (presentation, not modelling) ---
    members["date_of_birth"] = members["date_of_birth"].dt.normalize()
    members["annual_pension"] = members["annual_pension"].round(2)
    
    # --- save ---
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    members.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(members)} members to {OUT_PATH}")
    
    # --- checks ---
    print(members.shape)
    print(members["status"].value_counts())
    print(members.head())
    print(members.dtypes)
    print(members.groupby("status")["annual_pension"].agg(["count", "sum", "mean"]))
    print("Total annual pension:", members["annual_pension"].sum())
