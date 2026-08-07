"""
Valuation engine: annuity factors and member liabilities.

Combines the fitted mortality basis from mortality.py with the gilt
discount curve from discounting.py. This is the first module that
depends on both.
"""

import numpy as np

from mortality import survival_probability, UPPER_LIMITING_AGE
from discounting import load_curve, discount_factor


# Payment timing, D22. Annually in advance.
# Monthly in advance is the real-world basis; see F21.
PAYMENTS_IN_ADVANCE = True

def annuity_factor(x, A, B, C, curve, survival_fn=survival_probability):
    """
    Returns annuity factor at age x, paid annually in advance until the terminal age (D10).
    Payments are annual in advance (D22)
    survival_fn is the swap point for the mortality basis.
    x is an age and t is years from the valuation date.
    """
    payment_times = np.arange(0, UPPER_LIMITING_AGE - x + 1)
    survival = survival_fn(x, payment_times, A, B, C)
    discount = discount_factor(payment_times, curve)
    payments = survival * discount
    annuity = annuity = payments.sum()
    return annuity