"""
Unit tests for the mortality module.
"""

import numpy as np

from mortality import survival_probability


# Stand-in Gompertz-Makeham parameters. Roughly the right shape, but not
# the fitted values, because the fitted values need the gitignored ONS file.
A, B, C = 0.002, 5e-06, 1.12


def test_survival_at_zero_is_one():
    """Survival over zero years must be exactly 1, for any age and basis."""
    assert survival_probability(65, 0, A, B, C) == 1.0


def test_survival_decreasing_in_t():
    """Survival must fall as the projection period lengthens."""
    assert survival_probability(65, 10, A, B, C) < survival_probability(65, 5, A, B, C)


def test_survival_between_zero_and_one():
    """Survival is a probability, so it must lie in (0, 1] at every duration."""
    t = np.arange(0, 56)
    s = survival_probability(65, t, A, B, C)
    assert (s > 0).all()
    assert (s <= 1).all()