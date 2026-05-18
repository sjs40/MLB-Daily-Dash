"""Streamlit component that renders home plate umpire tendencies."""

import streamlit as st


def render_umpire_card(umpire: dict, umpire_stats: dict) -> None:
    """Render a card showing the home plate umpire's historical zone tendencies.

    Displays umpire name, called strike rate, walks and strikeouts per game,
    and a run-impact score indicating whether the umpire's zone favors
    pitchers or hitters.

    Args:
        umpire: Umpire assignment dict from fetcher.get_umpire().
        umpire_stats: Historical stats dict from fetcher.get_umpire_stats().
    """
    pass


def classify_umpire_zone(run_impact_score: float) -> str:
    """Map a run-impact score to a human-readable zone label.

    Positive scores indicate a pitcher-friendly zone (fewer runs);
    negative scores indicate a hitter-friendly zone (more runs).

    Args:
        run_impact_score: Numeric run-impact value (positive = pitcher-friendly).

    Returns:
        One of: "Pitcher-friendly", "Neutral", or "Hitter-friendly".
    """
    pass
