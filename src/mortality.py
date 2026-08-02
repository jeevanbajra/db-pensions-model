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

ONS_SHEET = "2022-2024"          # D2
ONS_HEADER_ROW = 5               # real headers on Excel row 6
ONS_COLUMNS = ["age", "mx", "qx", "lx", "dx", "ex"]

FIT_AGE_MIN = 50                 # D6
FIT_AGE_MAX = 100                # D6, upper limit of ONS data
UPPER_LIMITING_AGE = 120         # D10

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