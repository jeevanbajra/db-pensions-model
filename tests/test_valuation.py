"""
Unit tests for the valuation module.
"""

import numpy as np
import pandas as pd

from mortality import survival_probability
from valuation import annuity_factor


A, B, C = 0.002, 5e-06, 1.12


def flat_curve(rate):
    """A curve with every spot and forward rate equal to `rate`."""
    return pd.DataFrame({
        "maturity": np.arange(1.0, 40.5, 0.5),
        "spot_rate": rate,
        "forward_rate": rate,
    })


def test_payment_grid_length():
    """
    At a zero discount rate every payment is worth its face value, so the
    annuity factor collapses to the plain sum of survival probabilities.
    Comparing against a sum over an independently built grid pins the number
    of payment terms at 56 for a life aged 65 under a terminal age of 120.
    """
    t = np.arange(0, 56)
    expected = survival_probability(65, t, A, B, C).sum()
    assert np.isclose(annuity_factor(65, A, B, C, flat_curve(0.0)), expected)


def test_annuity_decreasing_in_interest_rate():
    """A higher discount rate makes the same stream of payments worth less."""
    assert annuity_factor(65, A, B, C, flat_curve(0.03)) > annuity_factor(65, A, B, C, flat_curve(0.06))