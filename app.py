"""Top-level entry point so `streamlit run app.py` works from the project root."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from mlb_daily_dash.app import main

if __name__ == "__main__":
    main()
