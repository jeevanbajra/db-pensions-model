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
from membership import VALUATION_DATE, NORMAL_RETIREMENT_AGE


# Payment timing, D22. Annually in advance.
# Monthly in advance is the real-world basis; see F21.
PAYMENTS_IN_ADVANCE = True
CPI = 0.03 #D25
LPI_CAP = 0.05 #D7
LPI_FLOOR = 0.0 #D7
REVALUATION_RATE = 0.03
SPOUSE_PROPORTION = 0.5
SPOUSE_AGE_DIFFERENCE = 3.0
PROPORTION_MARRIED = {"M": 0.80, "F": 0.70}
OPPOSITE_SEX = {"M": "F", "F": "M"}

# Chosen input, not a valuation output. The scheme is synthetic, so the asset
# value is set as a proportion of the liability rather than the other way
# round. Stated at 92.5 per cent to give a deficit that is material but
# recoverable.
INITIAL_FUNDING_LEVEL = 0.925

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

def pensioner_epv(x, pension, A, B, C, curve, frequency=12, cpi=CPI,
                  survival_fn=survival_probability_cohort):
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

def pensioner_liability(members, params, curve, frequency=12, cpi=CPI,
                        survival_fn=survival_probability_cohort):
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


def deferred_epv(x, pension, A, B, C, curve, nra=NORMAL_RETIREMENT_AGE,
                 frequency=12, cpi=CPI, revaluation=REVALUATION_RATE,
                 survival_fn=survival_probability_cohort):
    """
    Expected present value of a deferred member's benefit at the valuation date.
    
    t_ret is measured from the retirement date and drives the pension amounts.
    t_val is measured from the valuation date and drives survival and discounting.
    
    x is the current exact age, not the retirement age.
    Survival is measured from the member's age today under the cohort basis,
    so that a life reaching 65 in 2046 is not treated as a life aged 65 in 2026.

    Parameters x is current exact age, pension is the annual rate at the valuation date.
    A, B, C are the three fitted Gompertz-Makeham parameters.
    Revaluation is deliberately separate from cpi, even though they are both 0.3 here,
    incase we want to move one, keeping the other constant.
    
    Returns the EPV in pounds, for a pension expressed in pounds per year,
    per member and before the spouse's pension loading.
    
    Monthly in advance (D24). In-payment increases at flat CPI capped and floored (D25).
    Revaluation at the same flat rate (D28). Exact non-integer deferred period (D29).
    Grid built at the retirement age and shifted (D30).
    
    No benefit is payable on death before retirement, which is a result of D7
    and is invisible in the code because it shows up as an absence.
    
    Raises ValueError if the member is already at or past NRA, such members belong in pensioner_epv.
    """
    n = nra - x
    if n <= 0:
        raise ValueError(f"deferred_epv called with age {x} at or past NRA {nra}")
    t_ret = payment_times(nra, frequency=frequency)
    t_val = t_ret + n
    pension_at_ret = pension * (1 + revaluation)**n
    amounts = pension_amounts(pension_at_ret, t_ret, cpi=cpi)
    survival_probs = survival_fn(x, t_val, A, B, C)
    discounts = discount_factor(t_val, curve)
    payment = (amounts * survival_probs * discounts) / frequency
    def_epv = payment.sum()
    return def_epv

def deferred_liability(members, params, curve, frequency=12, cpi=CPI,
                       revaluation=REVALUATION_RATE,
                       survival_fn=survival_probability_cohort):
    """
    Total expected present value of benefits for all members not yet in payment.

    The filter is status != "pensioner", which is deliberate. D7 establishes
    that active and deferred members are financially identical in this model:
    same revaluation, same normal retirement age, same benefit, no future
    accrual. The 150 actives are therefore valued through the deferred path
    alongside the 350 deferreds. Narrowing the filter to status == "deferred"
    would run without error and silently omit the actives.

    Loops over members and calls deferred_epv once each, per D31. Each call is
    vectorised across that member's own payment dates.

    Parameters
    members : DataFrame as written by membership.py.
    params : dict keyed on "M" and "F", each holding an (A, B, C) tuple of
        fitted Gompertz-Makeham parameters. Built by the caller, per D27.
    curve : gilt curve frame as returned by discounting.load_curve.
    frequency : payments per year, monthly under D24.
    cpi : in-payment increase assumption, D25.
    revaluation : pre-retirement revaluation assumption, D28. Separate from cpi
        by design, although the two are equal on the current basis.
    survival_fn : mortality basis, defaulting to the cohort basis under D23.

    Returns
    total : float, the liability in pounds, before the spouse's pension loading.
    per_member : array of individual EPVs in the order the members were valued.
    """
    non_pensioners = members[members["status"] != "pensioner"].copy()
    non_pensioners["age"] = exact_ages(non_pensioners)
    epvs_non_pensioners = []
    for row in non_pensioners.itertuples():
        each_epv = deferred_epv(
            row.age, row.annual_pension, *params[row.sex], curve, row.normal_retirement_age,
            frequency=frequency, revaluation=revaluation, cpi=cpi, survival_fn=survival_fn,
        )
        epvs_non_pensioners.append(each_epv)
    def_member_epvs = np.array(epvs_non_pensioners)
    def_liability = def_member_epvs.sum()
    return def_liability, def_member_epvs


def spouse_epv(x, sex, pension, params, curve, nra=NORMAL_RETIREMENT_AGE,
               deferred=False, frequency=12, cpi=CPI,
               revaluation=REVALUATION_RATE, proportion=SPOUSE_PROPORTION,
               age_difference=SPOUSE_AGE_DIFFERENCE,
               proportion_married=PROPORTION_MARRIED,
               survival_fn=survival_probability_cohort):
    """
    Expected present value of the spouse's pension for one member.

    On the member's death, a proportion of their pension continues to their
    surviving spouse for the rest of the spouse's life. This function values
    that benefit. The member's own pension is valued separately by
    pensioner_epv or deferred_epv.

    A payment is made at time t only if the spouse is alive at t and the
    member has died by t. Assuming the two lives are independent, the
    probability of that is the spouse's survival probability multiplied by
    the member's probability of death. For a member not yet in payment, D7
    gives no benefit on death before retirement, so the member must have
    survived to retirement first and the death probability is n_p_x - t_p_x
    rather than 1 - t_p_x. Setting n to zero for a pensioner makes the same
    expression cover both cases.

    Independence is not true in practice. Spouses share a household, an
    income and a lifestyle, and bereavement itself raises mortality, so
    couples die closer together than independence implies. That means the
    periods where one is alive and the other dead are shorter than modelled,
    so this calculation overstates the cost of the benefit. The direction of
    the error is conservative, which is the direction to be wrong in.

    The spouse's pension is the member's pension amounts scaled by
    proportion. This works because the spouse's pension inherits the
    member's increase history rather than starting afresh at the date of
    death, so the two tracks never diverge and one array serves both.

    Parameters:
    x : member's exact age at the valuation date.
    sex : "M" or "F", the member's sex. The spouse is assumed to be of the
        opposite sex, and is assumed alive at the valuation date.
    pension : the member's own annual pension at the valuation date. The
        spouse's share is applied inside this function.
    params : dict keyed on "M" and "F", each holding an (A, B, C) tuple of
        fitted Gompertz-Makeham parameters. Both sets are used, one for the
        member and one for the spouse.
    curve : gilt curve frame as returned by discounting.load_curve.
    nra : normal retirement age, used only when deferred is True.
    deferred : True for any member not yet in payment. Actives are passed as
        True alongside deferreds, since D7 makes them financially identical.
    frequency : payments per year, monthly under D24.
    cpi : in-payment increase assumption, D25.
    revaluation : pre-retirement revaluation assumption, D28.
    proportion : share of the member's pension continuing to the spouse.
    age_difference : assumed age gap, husband older.
    proportion_married : dict keyed on the member's sex, giving the assumed
        proportion of members with a surviving spouse. Applied as a straight
        multiplier at the end, so the sensitivity to it is proportional.
    survival_fn : mortality basis, defaulting to the cohort basis under D23.

    Returns:
    float, the EPV of the spouse's pension in pounds.

    Raises ValueError if deferred is True but the member is already at or past NRA.
    """
    spouse_sex = OPPOSITE_SEX[sex]
    spouse_age = x - age_difference if sex == "M" else x + age_difference
    A_mem, B_mem, C_mem = params[sex]
    A_sp, B_sp, C_sp = params[spouse_sex]
    if deferred:
        n = nra - x
        if n <= 0:
            raise ValueError(f"spouse_epv called with deferred=True at age {x}, NRA {nra}")
        t_ret = payment_times(nra, frequency=frequency)
        t_val = t_ret + n
    else:
        n = 0.0
        t_ret = payment_times(x, frequency=frequency)
        t_val = t_ret
    pension_at_start = pension * (1 + revaluation) ** n
    member_amounts = pension_amounts(pension_at_start, t_ret, cpi=cpi)
    spouse_amounts = member_amounts * proportion
    spouse_survival = survival_fn(spouse_age, t_val, A_sp, B_sp, C_sp)
    member_survival = survival_fn(x, t_val, A_mem, B_mem, C_mem)
    survival_to_start = survival_fn(x, n, A_mem, B_mem, C_mem)
    weight = spouse_survival * (survival_to_start - member_survival)
    discount = discount_factor(t_val, curve)
    pay = (spouse_amounts * weight * discount) / frequency
    sp_epv = pay.sum() * proportion_married[sex]
    return sp_epv


def spouse_liability(members, params, curve, frequency=12, cpi=CPI,
                     revaluation=REVALUATION_RATE,
                     survival_fn=survival_probability_cohort):
    """
    Total expected present value of spouses' pensions across the whole scheme.

    Every member is included, in payment or not, since every member is
    assumed to have a spouse's pension attached to their benefit. There is
    no filter on this frame, unlike pensioner_liability and
    deferred_liability which split the membership between them.

    The deferred flag passed to spouse_epv is set per member as
    status != "pensioner". Actives are therefore treated as deferreds, per
    D7, which is the same routing used for their own pensions.

    Parameters:
    members : DataFrame as written by membership.py.
    params : dict keyed on "M" and "F", each holding an (A, B, C) tuple.
        Both sets are used for every member, one for the member and one for
        the spouse.
    curve : gilt curve frame as returned by discounting.load_curve.
    frequency : payments per year, monthly under D24.
    cpi : in-payment increase assumption, D25.
    revaluation : pre-retirement revaluation assumption, D28.
    survival_fn : mortality basis, defaulting to the cohort basis under D23.

    The spouse proportion, age difference and proportion married are left on
    the defaults set in spouse_epv.

    Returns:
    total : float, the liability in pounds.
    per_member : array of individual EPVs in the order the members were
        valued, one per member of the scheme.
    """
    all_members = members.copy()
    all_members["age"] = exact_ages(all_members)
    all_epvs = []
    for row in all_members.itertuples():
        indiv_epv = spouse_epv(
            row.age, row.sex, row.annual_pension, params, curve,
            nra=row.normal_retirement_age,
            deferred=row.status != "pensioner",
            frequency=frequency, cpi=cpi, revaluation=revaluation,
            survival_fn=survival_fn,
        )
        all_epvs.append(indiv_epv)
    all_member_epvs = np.array(all_epvs)
    total_liability = all_member_epvs.sum()
    return total_liability, all_member_epvs


def funding_position(total_liability, assets):
    """
    Funding ratio and deficit for a given liability and asset value.
    Funding ratio is asset diveded by liability. Deficit is liability - assets
    which is positive if the scheme is underfunded.

    In this case, assets are not derived, they are passed in and fixed.
    Deriving assets inside the function would mean the ratio would stay constant
    and stress test would have no impact on the funding position.

    Parameters:
    total_liability: total scheme liability in pounds.
    assets: market value of schemes assets in pounds.

    Returns: 
    funding ratio: float, assets divided by liability
    deficit: float, assets less liability. 
    """
    funding_ratio = assets / total_liability
    deficit = total_liability - assets
    return funding_ratio, deficit