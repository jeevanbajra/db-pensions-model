#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug  1 17:11:32 2026

@author: jeevanbajra
"""
"""
Gompertz-Makeham graduation of UK mortality.

Reads the ONS National Life Tables (2022-2024 period, see notes.md section
Data sources), converts the published q_x to the force of mortality mu_x
under a constant-force assumption within each year of age, and fits the
Gompertz-Makeham law mu_x = A + B * C^x separately for males and females.

Produces:
    - fitted A, B, C by sex
    - graduated q_x and p_x over the fitted range
    - a survival probability function t_p_x using the closed-form integral

Key decisions (notes.md): D1 population, D2 base period, D6 fitting range,
D10 upper limiting age, D11 fit weighting, D12 fitted parameters.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.optimize import curve_fit

# Path pattern as in membership.py: independent of working directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ONS_PATH = PROJECT_ROOT / "data" / "raw" / "nltuk198020223.xlsx"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "gm_parameters.csv"

ONS_SHEET = "2022-2024"          # D2
ONS_HEADER_ROW = 5               # real headers on Excel row 6
ONS_COLUMNS = ["age", "mx", "qx", "lx", "dx", "ex"]

FIT_AGE_MIN = 50                 # D6
FIT_AGE_MAX = 100                # D6, upper limit of ONS data
UPPER_LIMITING_AGE = 120         # D10

BASE_YEAR = 2023                 # D2, midpoint of the 2022-2024 period table
VALUATION_YEAR = 2026            # D3
BASE_TO_VALUATION = VALUATION_YEAR - BASE_YEAR
IMPROVEMENT_RATE = 0.0125         # D13, 1.25% a year
IMPROVEMENT_LOW = 0.0075          # D13, sensitivity
IMPROVEMENT_HIGH = 0.0175         # D13, sensitivity

def load_ons_table(path=ONS_PATH, sheet=ONS_SHEET):
    """
    Loads one period sheet from the ONS National Life Tables.

    Males and females are stored side by side under a single header row,
    so the two blocks are read separately and stacked.

    Returns DataFrame of 202 rows: age, mx, qx, lx, dx, ex, sex
    """
    ons_load_m = pd.read_excel(path, sheet_name= sheet, header= ONS_HEADER_ROW, usecols= "A:F")
    ons_load_f = pd.read_excel(path, sheet_name= sheet, header= ONS_HEADER_ROW, usecols= "H:M")
    ons_load_m.columns = ONS_COLUMNS
    ons_load_f.columns = ONS_COLUMNS
    ons_load_m["sex"]= "M"
    ons_load_f["sex"]= "F"
    ons_load_both = pd.concat([ons_load_m, ons_load_f], ignore_index=True)
    return ons_load_both
 
def add_force_of_mortality(table):
    """
    Adds the force of mortality mu_x to an ONS table

    Returns the same table as load_ons_table but with "mu_x" added.
    mu_x is the force of mortality under the constant-force assumption.
    This modifies the input in place.
    """
    #the force of mortality is assumed constant across each single year of age, 
    #so the integral of mu from x to x+1 equals mu_x, giving p_x = exp(-mu_x) 
    #and therefore mu_x = -ln(1 - q_x).
    table["mu_x"] = -np.log(1 - table["qx"]) 
    return table

def restrict_to_fit_range(retable, low=FIT_AGE_MIN, high=FIT_AGE_MAX):
    """
    Restricts the ONS table to spefific age ranges 

    Returns the same table but only including age range provided (D6).
    """
    restricted= retable[(retable["age"] >= low) & (retable["age"] <= high)]
    return restricted

def plot_log_mortality(restricted):
    m = restricted[restricted["sex"] == "M"]
    f = restricted[restricted["sex"] == "F"]
    plt.plot(m["age"], m["mu_x"], label= "Male")
    plt.plot(f["age"], f["mu_x"], label= "Female")
    plt.yscale("log")
    plt.title("Force of mortality against age, log scale")
    plt.xlabel("Age")
    plt.ylabel("mu_x log-scale")
    plt.legend()
    plt.show()

def fit_gompertz(table, sex): 
    """
    Fits a pure Gompertz, mu_x = B*C^x, by ordinary least squares on ln(mu)

    Takes a sex from the table, and returns sex-specific B and C values
    from the formula mu_x = B * C^x

    This is a baseline and a source of starting values for the GM fit
    """
    sex_specific = table[table["sex"] == sex]
    logged_mu = np.log(sex_specific["mu_x"])
    slope, intercept = np.polyfit(sex_specific["age"], logged_mu, 1)
    B = np.exp(intercept)
    C = np.exp(slope)
    return B, C

def gompertz_makeham_log(x, A, B, C):
    """
    Gompertz-makeham force of mortality.
    Returned on the log-scale as per D11
    """
    mu = A + B*C**x
    return np.log(mu)

def fit_gompertz_makeham(table, sex, p0=None):
    """
    Fits Gompertz-Makeham, mu_x = A + B·C^x, by least squares on ln(mu) via curve_fit
    Fit is log scale and fitted separately per sex (D11, D12 respectively)

    Takes the table, sex and p0. When p0 is None, the starting values come from fit_gompertz,
    with A guessed at 1e-4. It is an override for when the fit misbehaves.

    Returns A, B, C, and the standard errors. Standard errors come from the square root
    of the diagonal of the covariance matrix, arrive as an array in the same order as A, B, C.

    in the Returns block: the log-scale objective is undefined where A + B·C^x goes negative,
    so curve_fit can emit a RuntimeWarning while exploring. Use 'bound' to fix.
    """
    m_or_f = table[table["sex"] == sex]
    logged_mu = np.log(m_or_f["mu_x"])
    if p0 is None:
        B, C = fit_gompertz(table, sex)
        p0 = [1e-4, B, C]
    params, covariance = curve_fit(gompertz_makeham_log, m_or_f["age"], logged_mu, p0=p0)
    A, B, C = params
    se = np.sqrt(np.diag(covariance))
    return A, B, C, se

def fitted_against_raw(table):
    m_raw = table[table["sex"] == "M"]
    f_raw = table[table["sex"] == "F"]
    A_m, B_m, C_m, se_m = fit_gompertz_makeham(table, "M")
    A_f, B_f, C_f, se_f = fit_gompertz_makeham(table, "F")
    m_fitted = gompertz_makeham_log(m_raw["age"], A_m, B_m, C_m)
    f_fitted = gompertz_makeham_log(f_raw["age"], A_f, B_f, C_f)
    plt.plot(m_raw["age"], np.log(m_raw["mu_x"]), "o", markersize = 3, label= "Male raw")
    plt.plot(f_raw["age"], np.log(f_raw["mu_x"]), "o", markersize = 3, label= "Female raw")
    plt.plot(m_raw["age"], m_fitted, label= "Male fitted")
    plt.plot(f_raw["age"], f_fitted, label= "Female fitted")
    plt.title("Gompertz-Makeham vs raw")
    plt.xlabel("Age")
    plt.ylabel("mu_x log-scale")
    plt.legend()
    plt.show()

def plot_residuals(table):
    m_raw = table[table["sex"] == "M"]
    f_raw = table[table["sex"] == "F"]
    A_m, B_m, C_m, se_m = fit_gompertz_makeham(table, "M")
    A_f, B_f, C_f, se_f = fit_gompertz_makeham(table, "F")
    m_fitted = gompertz_makeham_log(m_raw["age"], A_m, B_m, C_m)
    f_fitted = gompertz_makeham_log(f_raw["age"], A_f, B_f, C_f)
    plt.plot(m_raw["age"], np.log(m_raw["mu_x"]) - m_fitted, "o", markersize=3, label= "Male")
    plt.plot(f_raw["age"], np.log(f_raw["mu_x"]) - f_fitted, "o", markersize=3, label= "Female")
    plt.axhline(0, color="black", linewidth=0.8)
    plt.title("Gompertz-Makeham residuals against age")
    plt.xlabel("Age")
    plt.ylabel("Residual, ln(mu) observed minus fitted")
    plt.legend()
    plt.show()

def survival_probability(x, t, A, B, C):
    """
    Computes the probability that a life aged x survives a further t years,
    under the fitted Gompertz-Makeham force of mortality.
    
    t_p_x = exp(-(A*t + (B*C^x / ln(C)) * (C^t - 1)))
    
    Closed form obtained by integrating the GM force of mortality analytically
    from x to x+t, rather than approximating by chaining one-year survival probabilities.
    
    x is age in years, t (need not be an integer) is the number of years survived, 
    and A, B, C are the fitted parameters for the relevant sex.

    The survival probability, between 0 and 1, with 1 at t=0 exactly.

    Above age 100 this extrapolates the fitted curve beyond the ONS data (D10)
    and GM overstates mortality at the oldest ages,so survival to very
    high ages is understated (limitations).
    """
    term_1 = A*t
    term_2 = (B*C**x)/np.log(C)
    term_3 = C**t - 1
    t_p_x = np.exp(-(term_1 + term_2*term_3))
    return t_p_x

def life_expectancy(x, A, B, C):
    """
    Computes complete period life expectancy at age x, under the fitted Gompertz-Makeham.
    Period in this instance means current mortality rates held fixed for all future ages,
    with no allowance for improvement, ONS table is a period table and the published e(65)
    is a period figure, so the comparison is like for like.
    
    Numerical integration of t_p_x from t = 0 to the upper limiting age,
    using the trapezoidal rule.
    The integral is truncated at the upper limiting age of 120 (D10),
    understating the result very slightly.
    Trapezoidal integration over integer steps gives the complete expectation
    rather than the curtate one, so no half-year adjustment is applied.

    Age x, and the fitted A, B, C for the relevant sex.

    Returns expected further years of life.

    At x = 65 this gives 18.26 male and 20.66 female against published ONS figures of 
    18.73 and 21.16, so within half a year. Both understate, consistent with the old-age 
    flattening limitation.
    """
    t_vals = np.arange(0, 56)
    s_prob = survival_probability(x, t_vals, A, B, C)
    p_life = np.trapezoid(s_prob, t_vals)
    return p_life

def improved_force_of_mortality(x, years_from_valuation, A, B, C, improvement=IMPROVEMENT_RATE):
    """
    The force of mortality at age x, projected forward to a calendar year years_from_valuation
    after the valuation date, with mortality improvement applied (mu_at_x).

    Constant annual improvement of 1.25% per D13, compounding, 
    replacing the Lee-Carter projection that was cut from scope.
    0.75% and 1.75% provide the sensitivity range, with improvement being a parameter,
    so it may be varied in the future.

    Improvement compounds from the 2023 base year (2022-2024 period table centred on 2023), 
    the three years between the base year and the 2026 valuation date are added internally.
    years_from_valuation = 0 gets mortality already improved by three years, which is deliberate.

    Gompertz-Makeham is a law about the force of mortality, so improvement is applied there 
    and converted to q afterwards if needed (q = 1 - exp(-mu)).

    Args: Age x, and the fitted A, B, C for the relevant sex, years_from_valuation and improvement.
    Returns mu_at_x, stated above
    """
    GM_at_x = A + B*C**x
    compounding_factor = (1 - improvement)**(BASE_TO_VALUATION + years_from_valuation)
    mu_at_x = GM_at_x * compounding_factor
    return mu_at_x

def survival_probability_cohort(x, t, A, B, C, improvement=IMPROVEMENT_RATE):
    """
    Intgrated the improved_force_of_mortality by hand and produced the closed form:
    d^k[A/ln(d) (d^t -1) + BC^x / ln(Cd) ((Cd)^t -1)].
    d^k carries the three years from the 2023 base year to the valuation date.
    if improvement = 0, it divides by ln(1) = 0 and returns nan,
    the period function is what to use instead.
    Returns the survival probability for cohort which is the closed form negated and exponentiated
    """
    d = 1 - improvement
    Cd = C * d
    base_factor = d ** BASE_TO_VALUATION
    term_2 = (A/np.log(d)) * (d**t - 1)
    term_3 = ((B*C**x)/np.log(Cd)) * (Cd**t -1)
    cumulative_hazard = base_factor * (term_2 + term_3)
    survival_cohort = np.exp(- cumulative_hazard)
    return survival_cohort

def extract_gm_parameters(out_path=PROCESSED_PATH):
    """
    Fits the Gompertz-Makeham parameters for both sexes from the ONS national life tables,
    and commits them to a CSV.

    It is only written once and is not called by the model in the same way that extract_curve
    works for the gilt curve. This is because the source file is gitignored (D4) so Streamlit
    Cloud cannot see it (F11), and a valuation whose mortality basis is not reproducable is
    not checkable. 

    Parameter: out_path

    Returns the frame.
    """
    table = restrict_to_fit_range(add_force_of_mortality(load_ons_table()))
    A_m, B_m, C_m, se_m = fit_gompertz_makeham(table, "M")
    A_f, B_f, C_f, se_f = fit_gompertz_makeham(table, "F")
    parameters = pd.DataFrame({
        "sex": ["M", "F"],
        "A": [A_m, A_f],
        "B": [B_m, B_f],
        "C": [C_m, C_f],
        "se_A": [se_m[0], se_f[0]],
        "se_B": [se_m[1], se_f[1]],
        "se_C": [se_m[2], se_f[2]],
    })
    assert parameters.shape == (2, 7), f"expected (2, 7), got {parameters.shape}"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    parameters.to_csv(out_path, index=False)
    return parameters

def load_gm_parameters(path=PROCESSED_PATH):
    """
    Reads the commited CSV: gm_parameters.csv and returns the fitted parameters.

    Two return values: a dictionary keyed on "M" and "F" holding (A, B, C) tuples for the caller,
    and the full frame including standard errors for anything that needs them.

    Deliberately no fallback to re-fitting if the file is missing because a silent fallback would
    work locally and fail in deployment, which is the failure this pair of functions exists to prevent.
    """
    parameters = pd.read_csv(path, float_precision="round_trip")
    assert list(parameters.columns) == ["sex", "A", "B", "C", "se_A", "se_B", "se_C"], "unexpected columns in gm_parameters.csv"
    indexed = parameters.set_index("sex")
    params = {
        sex: (indexed.loc[sex, "A"], indexed.loc[sex, "B"], indexed.loc[sex, "C"])
        for sex in ("M", "F")
    }
    return params, parameters


def scale_params(params, multiplier):
    """
    Scale the force of mortality at every age by multiplier.

    mu = A + B * C^x, so multiplying A and B by the same factor multiplies
    mu by that factor exactly. C is the rate at which mortality accelerates
    with age and is left alone: a level stress should not change the shape
    of the curve.
    """
    return {sex: (A * multiplier, B * multiplier, C)
            for sex, (A, B, C) in params.items()}