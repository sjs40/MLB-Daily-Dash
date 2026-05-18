"""Streamlit component that renders a starting pitcher's profile card."""

import streamlit as st


def render_pitcher_card(pitcher: dict, recent_stats: object, season_stats: dict) -> None:
    """Render a pitcher profile card with season stats, recent form, and fatigue indicator.

    Shows ERA, FIP, K/9, BB/9, WHIP, a sparkline of recent starts, and a
    colour-coded fatigue badge based on days of rest and last start pitch count.

    Args:
        pitcher: Pitcher info dict (name, player_id, handedness, headshot_url).
        recent_stats: DataFrame of recent starts from fetcher.get_pitcher_recent_stats().
        season_stats: Dict of season aggregates from fetcher.get_pitcher_season_stats().
    """
    pass


def render_fatigue_badge(days_rest: int, last_pitch_count: int) -> None:
    """Render a colour-coded badge reflecting pitcher fatigue level.

    Green = well-rested & low count, yellow = moderate concern,
    red = fatigue flag triggered by thresholds in FATIGUE_THRESHOLDS.

    Args:
        days_rest: Number of full days since the pitcher's last outing.
        last_pitch_count: Pitch count in the pitcher's most recent start.
    """
    pass
