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