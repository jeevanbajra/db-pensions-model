"""
Valuation engine: annuity factors and member liabilities.

Combines the fitted mortality basis from mortality.py with the gilt
discount curve from discounting.py. This is the first module that
depends on both.
"""
import numpy as np

from mortality import (survival_probability, survival_probability_cohort,
                       UPPER_LIMITING_AGE)
from discounting import load_curve, discount_factor
from membership import VALUATION_DATE


# Payment timing, D22. Annually in advance.
# Monthly in advance is the real-world basis; see F21.
PAYMENTS_IN_ADVANCE = True
CPI = 0.03 #D25
LPI_CAP = 0.05 #D7
LPI_FLOOR = 0.0 #D7

def payment_times(x, frequency=12, upper_age=UPPER_LIMITING_AGE):
    """
    Takes a member's exact age x at the valuation date and returns the array of times, 
    measured in years from the valuation date - when members recieve payments.
    Payments are in advance so the first is at t = 0 and the final one falling on or 
    before upper_age.
    The grid is built from integer month indices divided once rather than by accumulating
    a fractional step.
    """
    payments = int(np.floor((upper_age-x) * frequency)) + 1
    years = np.arange(payments) / frequency
    return years
    

def annuity_factor(x, A, B, C, curve, survival_fn=survival_probability):
    """
    Returns annuity factor at age x, paid annually in advance until the terminal age (D10).
    Payments are annual in advance (D22).
    survival_fn is the swap point for the mortality basis.
    x is an age and t is years from the valuation date.
    """
    payment_times = np.arange(0, UPPER_LIMITING_AGE - x + 1)
    survival = survival_fn(x, payment_times, A, B, C)
    discount = discount_factor(payment_times, curve)
    payments = survival * discount
    annuity = payments.sum()
    return annuity


def pension_amounts(pension, times, cpi=CPI, cap=LPI_CAP, floor=LPI_FLOOR):
    """
    Taking a member's pension as at the valuation date, plus the payment times array, 
    returns the annual pension rate applicable at each payment time; the payment itself 
    is this divided by the frequency, applied by the caller.
    LPI increases are annual in comparison to the payments which are monthly.
    CPI at 0.03 (D25), and the LPI bounded above 0 and below 0.05 (D7).
    The count is the number of whole years elapsed: the payment time rounded down using np.floor.
    """
    annual_increase = np.maximum(np.minimum(cpi, cap), floor)
    increases_granted = np.floor(times)
    amounts = ((1 + annual_increase)**increases_granted) * pension
    return amounts

def pensioner_epv(x, pension, A, B, C, curve, frequency=12, cpi=CPI, survival_fn=survival_probability_cohort):
    """
    Returns the expected value of all the future payements, given a memebers age, sex and pensions.
    'pension' is the annual rate at the valuation date, and the annual rate is
    divided by frequency to get each payment.
    The default basis is cohort (D23).
    """
    pay_times = payment_times(x, frequency)
    annual_rates = pension_amounts(pension, pay_times, cpi)
    survival = survival_fn(x, pay_times, A, B, C)
    discount = discount_factor(pay_times, curve)
    payment_pvs = (annual_rates * survival * discount) / frequency 
    epv = payment_pvs.sum()
    return epv

def exact_ages(members, valuation_date=VALUATION_DATE):
    """
    Returns the exact ages of the to the day. 
    age_at_valuation is the the difference between the date of birth and the valuation date.
    It is then converted to days, using dt.days. This can lose up to 1 day on their age,
    which is under three thousandths of a per cent of one payment.
    Converted to years by dividing by 365.25 (D7). 
    """
    dobs = members["date_of_birth"]
    age_at_valuation = valuation_date - dobs
    days_old = age_at_valuation.dt.days
    years_old = days_old / 365.25
    return years_old.rename("age")

def pensioner_liability(members, params, curve, frequency=12, cpi=CPI, survival_fn=survival_probability_cohort):
    """
    Returns the total pensioner liability and the array of member epvs.
    The total is the pensioner Technical Provisions on the cohort basis (D23).
    With frequency 12 (D24) and increases as per D25.
    params is a dictionary keyed on the sex codes in the members frame.
    """
    pensioners = members[members["status"] == "pensioner"].copy()
    pensioners["age"] = exact_ages(pensioners)
    epvs = []
    for row in pensioners.itertuples():
        individual_epv = pensioner_epv(
            row.age, row.annual_pension, *params[row.sex], curve,
            frequency=frequency, cpi=cpi, survival_fn=survival_fn,
        )
        epvs.append(individual_epv)
    member_epvs = np.array(epvs)
    liability = member_epvs.sum()
    return liability, member_epvs
    