"""Streamlit component that renders a team's batting lineup as a styled table."""

import pandas as pd
import streamlit as st


def render_lineup_table(lineup: list[dict], team_name: str) -> None:
    """Render a batting order with per-player season stats and projections.

    Displays slot, name, position, AVG/OBP/SLG, projected H, projected TB,
    and projected HR for the game.

    Args:
        lineup: List of player dicts in batting order from fetcher.get_starting_lineup().
        team_name: Display name for the team (used as the table header).
    """
    pass


def build_lineup_dataframe(lineup: list[dict]) -> pd.DataFrame:
    """Convert a raw lineup list into a display-ready DataFrame.

    Args:
        lineup: List of player dicts in batting order.

    Returns:
        DataFrame with columns: Slot, Name, Pos, AVG, OBP, SLG, Proj H, Proj TB, Proj HR.
    """
    pass
