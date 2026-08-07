"""
Unit tests for the discounting module.
"""

import numpy as np
import pandas as pd

from discounting import discount_factor


def flat_curve(rate):
    """A curve with every spot and forward rate equal to `rate`."""
    return pd.DataFrame({
        "maturity": np.arange(1.0, 40.5, 0.5),
        "spot_rate": rate,
        "forward_rate": rate,
    })


def test_discount_factor_at_zero_is_one():
    """A payment made today is not discounted."""
    assert discount_factor(0, flat_curve(0.05)) == 1.0


def test_discount_factors_decreasing():
    """Later payments are worth strictly less than earlier ones."""
    t = np.arange(0, 56)
    v = discount_factor(t, flat_curve(0.05))
    assert (np.diff(v) < 0).all()