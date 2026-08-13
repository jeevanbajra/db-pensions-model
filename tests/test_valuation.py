"""
Unit tests for the valuation module.
"""
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from mortality import survival_probability, load_gm_parameters
from valuation import (annuity_factor, deferred_epv, deferred_liability,
                       pensioner_epv, pensioner_liability)
from discounting import load_curve


A, B, C = 0.002, 5e-06, 1.12

TEST_PARAMS, _ = load_gm_parameters()

DATA = Path(__file__).resolve().parent.parent / "data" / "processed"

MEMBERS = pd.read_csv(DATA / "members.csv", parse_dates=["date_of_birth"])
CURVE = load_curve()


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


def test_all_members_valued_exactly_once():
    _, pensioner_epvs = pensioner_liability(MEMBERS, TEST_PARAMS, CURVE)
    _, deferred_epvs = deferred_liability(MEMBERS, TEST_PARAMS, CURVE)

    valued = len(pensioner_epvs) + len(deferred_epvs)

    assert len(MEMBERS) == 1000, (
        f"membership file has {len(MEMBERS)} rows, expected 1000"
    )
    assert valued == len(MEMBERS), (
        f"valued {valued} members ({len(pensioner_epvs)} pensioner, "
        f"{len(deferred_epvs)} non-pensioner) from {len(MEMBERS)} rows"
    )


def test_actives_valued_as_deferreds():
    _, deferred_epvs = deferred_liability(MEMBERS, TEST_PARAMS, CURVE)

    deferred_rows = (MEMBERS["status"] == "deferred").sum()

    assert len(deferred_epvs) > deferred_rows, (
        f"valued {len(deferred_epvs)} non-pensioners against {deferred_rows} "
        "rows with status deferred. Actives are valued through the deferred "
        "path under D7, so the filter should be != pensioner, not == deferred"
    )


def test_deferred_epv_increases_with_age():
    epv_50 = deferred_epv(50.0, 1000.0, *TEST_PARAMS["M"], CURVE)
    epv_60 = deferred_epv(60.0, 1000.0, *TEST_PARAMS["M"], CURVE)

    assert epv_60 > epv_50, (
        f"EPV at 60 is {epv_60}, at 50 is {epv_50}. A member closer to "
        "retirement has less discounting and less mortality to survive, "
        "so the EPV per pound must rise with age"
    )
