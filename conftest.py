"""
Pytest configuration. Puts src on the import path so tests can
import the model modules the same way the notebooks do.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))