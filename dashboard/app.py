"""Deployment check. Confirms the packages install and the committed data loads."""

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import scipy
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"

st.title("DB Pension Funding Model")
st.write("Deployment check, not the dashboard.")

st.subheader("Package versions")
st.write({
    "numpy": np.__version__,
    "pandas": pd.__version__,
    "scipy": scipy.__version__,
    "matplotlib": matplotlib.__version__,
    "streamlit": st.__version__,
})

st.subheader("Committed data")
for name in ["gilt_curve.csv", "gm_parameters.csv", "members.csv"]:
    frame = pd.read_csv(PROCESSED / name)
    st.write(name, frame.shape)
