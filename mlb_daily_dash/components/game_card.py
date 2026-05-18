"""Streamlit component that renders a compact game summary card."""

import streamlit as st


def render_game_card(game: dict) -> None:
    """Render a summary card for a single MLB game.

    Displays matchup, venue, game time, and status. Acts as a clickable
    selector when multiple games are listed on the sidebar.

    Args:
        game: Game dict as returned by fetcher.get_todays_games().
    """
    pass


def render_game_selector(games: list[dict]) -> dict | None:
    """Render a list of game cards in the sidebar and return the selected game.

    Args:
        games: List of game dicts for today.

    Returns:
        The game dict the user selected, or None if no games are available.
    """
    pass
