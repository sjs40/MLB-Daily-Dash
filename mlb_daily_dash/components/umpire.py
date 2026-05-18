"""Streamlit component that renders home plate umpire zone tendencies."""

import streamlit as st

from mlb_daily_dash.data.fetcher import get_umpire_for_game, get_umpire_stats


# ---------------------------------------------------------------------------
# Public component
# ---------------------------------------------------------------------------

def render_umpire(game_pk: int) -> None:
    """Render the HP umpire section for a game.

    Fetches the umpire assignment and career zone stats from UmpScorecards,
    then renders four st.metric tiles: Games, Accuracy %, vs Expected %,
    Consistency %. Falls back gracefully when assignment or stats are
    unavailable.

    The UmpScorecards API provides accuracy/consistency metrics rather than
    K%/BB% directly. Zone classification is derived from accuracy vs model.

    Args:
        game_pk: MLB Stats API game primary key.
    """
    umpire = get_umpire_for_game(game_pk)

    if umpire is None:
        st.info("Umpire assignment not yet posted.")
        return

    name: str = umpire.get("name", "Unknown")
    st.subheader(f"HP Umpire · {name}")

    stats = get_umpire_stats(name)

    if stats is None:
        st.write(f"No career stats found for {name}.")
        return

    games: int         = stats.get("games", 0)
    accuracy: float    = stats.get("accuracy", 0.0)
    acc_above_x: float = stats.get("accuracy_above_x", 0.0)
    consistency: float = stats.get("consistency", 0.0)
    run_impact: float  = stats.get("run_impact", 0.0)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Games (career)", str(games))
    col2.metric("Accuracy", f"{accuracy:.1f}%")
    col3.metric(
        label="vs Expected",
        value=f"{acc_above_x:+.2f}%",
        delta=acc_above_x,
        delta_color="normal",
    )
    col4.metric("Consistency", f"{consistency:.1f}%")

    zone = _classify_zone(acc_above_x)
    st.caption(
        f"Avg run impact: {run_impact:.2f} runs/game · **{zone}**"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify_zone(acc_above_x: float) -> str:
    """Classify umpire tendency based on accuracy relative to model expectation.

    Positive acc_above_x → ump calls more correct pitches than expected →
    tighter/correct zone → slight pitcher-friendly tendency.
    Negative → fewer correct calls → expanded effective zone → hitter-friendly.
    """
    if acc_above_x >= 0.5:
        return "Pitcher-friendly"
    if acc_above_x <= -0.5:
        return "Hitter-friendly"
    return "Neutral"
