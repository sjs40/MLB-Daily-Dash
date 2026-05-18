"""Streamlit component that renders home plate umpire zone tendencies."""

import streamlit as st

from mlb_daily_dash.data.fetcher import get_umpire_for_game, get_umpire_stats


# ---------------------------------------------------------------------------
# Public component
# ---------------------------------------------------------------------------

def render_umpire(game_pk: int) -> None:
    """Render the HP umpire section for a game.

    Fetches the umpire assignment and career zone stats, then renders:
      - Four st.metric tiles: K%, K% Δ, BB%, BB% Δ
      - Run impact caption
      - Falls back gracefully when assignment or stats are unavailable.

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

    k_pct: float       = stats.get("k_pct", 0.0)
    k_pct_delta: float = stats.get("k_pct_delta", 0.0)
    bb_pct: float      = stats.get("bb_pct", 0.0)
    bb_pct_delta: float = stats.get("bb_pct_delta", 0.0)
    run_impact: float  = stats.get("run_impact", 0.0)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        label="K% (career)",
        value=f"{k_pct:.1%}",
    )
    # Fewer Ks than average is hitter-friendly → inverse coloring so
    # negative delta renders green.
    col2.metric(
        label="K% vs Avg",
        value=f"{k_pct_delta:+.1%}",
        delta=k_pct_delta,
        delta_color="inverse",
    )

    col3.metric(
        label="BB% (career)",
        value=f"{bb_pct:.1%}",
    )
    # More BBs than average is hitter-friendly → standard coloring so
    # positive delta renders green.
    col4.metric(
        label="BB% vs Avg",
        value=f"{bb_pct_delta:+.1%}",
        delta=bb_pct_delta,
        delta_color="normal",
    )

    _render_run_impact_caption(run_impact)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _render_run_impact_caption(run_impact: float) -> None:
    """Render the run-impact line as a caption with a zone label."""
    zone = _classify_run_impact(run_impact)
    sign = "+" if run_impact >= 0 else ""
    st.caption(
        f"Run impact: {sign}{run_impact:.2f} runs/game vs average "
        f"— **{zone}**"
    )


def _classify_run_impact(run_impact: float) -> str:
    """Map a run-impact score to a zone label.

    Positive run_impact means more runs than expected (hitter-friendly umpire);
    negative means fewer runs (pitcher-friendly umpire).

    Args:
        run_impact: Runs per game above league-average expectation.

    Returns:
        "Hitter-friendly", "Neutral", or "Pitcher-friendly".
    """
    if run_impact >= 0.15:
        return "Hitter-friendly"
    if run_impact <= -0.15:
        return "Pitcher-friendly"
    return "Neutral"
