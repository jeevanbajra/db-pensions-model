"""
Gilt curve loading, interpolation and discounting.

Extracts the Bank of England nominal spot and instantaneous forward
curves at the valuation date from the raw daily file, persists them to
data/processed, and converts spot rates into discount factors.
"""

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "GLC_nominal_daily_current_month.xlsx"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "gilt_curve.csv"

SPOT_SHEET = "4. spot curve"     # D2
FWD_SHEET = "2. fwd curve"       # D18
GLC_HEADER_ROW = 3               # real headers on Excel row 4
DATE_COLUMN = "years:"           # BoE label on the date column

VALUATION_DATE = pd.Timestamp("2026-07-28")   # D3

def read_curve_sheet(sheet, path=RAW_PATH):
    """
    Return one BoE curve at the valuation date as maturity and rate.

    Reads a single sheet of the daily GLC file, selects the valuation
    date row, and transposes it so maturities run down the rows.
    Rates are returned as decimals, not percentages, since every
    formula downstream expects decimals. Percentages are for display
    only.
    """
    boe = pd.read_excel(path, sheet_name=sheet, header=GLC_HEADER_ROW)
    boe = boe.rename(columns={DATE_COLUMN: "date"})
    boe = boe[boe["date"].notna()]
    row = boe[boe["date"] == VALUATION_DATE]
    assert len(row) == 1, f"expected 1 row for {VALUATION_DATE}, got {len(row)}"
    curve = row.drop(columns=["date"]).T
    curve.columns = ["rate"]
    curve = curve.reset_index().rename(columns={"index": "maturity"})
    curve = curve.dropna().reset_index(drop=True)
    curve["rate"] = curve["rate"] / 100
    return curve

def extract_curves(path=RAW_PATH, out_path=PROCESSED_PATH):
    """
    Extract the valuation date curves and persist them to CSV (data/processed/gilt_curve.csv).
    
    Returns 1 row per maturity, columns: maturity, spot_rate, forward_rate.
    Rates in decimals.

    The source is a rolling monthly file which will not contain 28 July 2026 next month,
    so the committed CSV is the only durable copy of the valuation basis (D18).
    """
    spot = read_curve_sheet(SPOT_SHEET, path=path)
    fwd = read_curve_sheet(FWD_SHEET, path=path)
    spot = spot.rename(columns={"rate": "spot_rate"})
    fwd = fwd.rename(columns={"rate": "forward_rate"})
    assert fwd["maturity"].equals(spot["maturity"]), "spot and forward maturity grids differ"
    curve = pd.merge(spot, fwd, on="maturity", how="inner")
    assert len(curve) == len(spot), "merge changed the row count"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    curve.to_csv(out_path, index=False)
    return curve

def load_curve(path=PROCESSED_PATH):
    """
    Return the extracted gilt curve from data/processed.
    Reading the CSV, confirming the three expected columns are present.
    The three expected columns being maturity, spot_rate, forward_rate.
    Reads data/raw.
    """
    # round_trip forces the exact float parser; the default one loses the
    # last bit and breaks equality against the frame that was written.
    curve = pd.read_csv(path, float_precision="round_trip")
    assert list(curve.columns) == ["maturity", "spot_rate", "forward_rate"], "unexpected columns in gilt_curve.csv"
    return curve

def spot_rate(t, curve):
    """
    Returns the spot rate at maturity t.
    It interpolates linearly between published points (D16).
    Below one year it holds the one-year rate flat (D17).
    Above the last published maturity the instantaneous forward is held flat
    at its 40-year value and the spot follows (D19).
    """
    assert curve["maturity"].is_monotonic_increasing, "maturity is not monotonic increasing"
    xp = curve["maturity"]
    fp = curve["spot_rate"]
    last_maturity = xp.iloc[-1]
    last_spot = fp.iloc[-1]
    last_forward = curve["forward_rate"].iloc[-1]
    interpolated = np.interp(t, xp, fp)
    extrapolated = (last_spot * last_maturity + last_forward * (t - last_maturity)) / np.maximum(t, last_maturity)
    rates = np.where(t <= last_maturity , interpolated, extrapolated)
    return rates

def discount_factor(t, curve):
    """
    Returns the discount factor at maturity t.
    BoE rates are continuously compounded, hence exp(-y*t) rather than 1/(1+y)^t (F1)
    """
    yt = spot_rate(t, curve)
    vt = np.exp(-yt * t)
    return vt

def shift_curve(curve, shift):
    """
    Returns a copy of the origional curve with all the rates shifted in paralell.
    A copy is returned as it will leave the origional one unmodified and safe for reuse.

    Both the spot and forward columns are shifted by the same magnitude. This is the case as
    the spot_rate interpolates up until 40 years and extrapolates above it using the 40 year forward.
    So shifting only the spot column would leave the extrapolated part unmoved, which is where
    over half of the discount horizon is covered for the younger members.

    The extrapolation is y(t) = (y(40)*40 + f(40)*(t-40)) / t, so adding d to both y(40) and
    f(40) adds d*40 + d*(t-40) = d*t to the numerator, and y(t) gains exactly d. 

    Parameters
    curve : gilt curve frame as returned by load_curve.
    shift : parallel shift in decimals, so -0.01 is a one percentage point
        fall. Zero returns an unchanged copy.

    Returns
    A new frame with the same columns and the rates shifted.
    """
    shifted = curve.copy()
    shifted[["spot_rate", "forward_rate"]] += shift
    return shifted

def extend_flat_spot(curve):
    extended_flat = curve.copy()
    extra_maturities = np.arange(40.5, 90.5, 0.5)
    y40 = extended_flat.loc[extended_flat["maturity"] == 40.0, "spot_rate"].iloc[0]
    extension = pd.DataFrame({
        "maturity": extra_maturities,
        "spot_rate": y40,
        "forward_rate": y40,
    })
    return pd.concat([extended_flat, extension], ignore_index = True)
    