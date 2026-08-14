"""
Unit tests for the mortality module.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from mortality import (survival_probability, survival_probability_cohort,
                       improved_force_of_mortality, load_gm_parameters)

TEST_PARAMS, _ = load_gm_parameters()


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

def test_improved_force_at_a_point():
    A, B, C = TEST_PARAMS["M"]
    force = improved_force_of_mortality(85.0, 20.0, A, B, C)
    assert force == 0.07399580786141326, (
        f"improved force at attained age 85, 20 years from valuation, is "
        f"{force}. This is exact arithmetic with no integration, so any "
        "change here means the parameters or the improvement offset moved"
    )


def test_cohort_survival_matches_improved_force():
    A, B, C = TEST_PARAMS["M"]
    closed = -np.log(survival_probability_cohort(65.0, 20.0, A, B, C))
    t = np.linspace(0.0, 20.0, 20001)
    numerical = np.trapezoid(improved_force_of_mortality(65.0 + t, t, A, B, C), t)
    assert closed == pytest.approx(numerical, rel=1e-6), (
        f"closed form gives {closed}, numerical integration of the force "
        f"gives {numerical}. The cohort survival function was derived by "
        "integrating the improved force by hand, so a mismatch means that "
        "integration is wrong"
    )