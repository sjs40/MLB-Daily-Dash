"""Functions for fetching MLB game, player, and environmental data."""

import datetime
from typing import Optional

import pandas as pd
import requests


def get_todays_games(date: Optional[datetime.date] = None) -> list[dict]:
    """Fetch the schedule of MLB games for a given date.

    Args:
        date: The date to fetch games for. Defaults to today.

    Returns:
        List of game dicts containing gamePk, teams, venue, status, and game time.
    """
    pass


def get_probable_pitchers(game_pk: int) -> dict:
    """Fetch the probable starting pitchers for a game.

    Args:
        game_pk: The MLB Stats API game primary key.

    Returns:
        Dict with 'home' and 'away' keys, each containing pitcher info or None.
    """
    pass


def get_starting_lineup(game_pk: int) -> dict:
    """Fetch the confirmed starting lineups for a game.

    Args:
        game_pk: The MLB Stats API game primary key.

    Returns:
        Dict with 'home' and 'away' keys, each a list of player dicts in batting order.
        Returns an empty list for a side if the lineup is not yet posted.
    """
    pass


def get_pitcher_recent_stats(player_id: int, n_games: int = 5) -> pd.DataFrame:
    """Fetch a starting pitcher's stats across their most recent starts.

    Args:
        player_id: MLB Stats API player ID.
        n_games: Number of most recent games to include.

    Returns:
        DataFrame with columns: date, opponent, IP, H, ER, BB, K, pitches.
    """
    pass


def get_pitcher_season_stats(player_id: int, season: Optional[int] = None) -> dict:
    """Fetch a pitcher's season-level stats (ERA, FIP, K/9, BB/9, HR/9, WHIP).

    Args:
        player_id: MLB Stats API player ID.
        season: Season year. Defaults to current season.

    Returns:
        Dict of aggregated season stats.
    """
    pass


def get_batter_season_stats(player_id: int, season: Optional[int] = None) -> dict:
    """Fetch a batter's season-level stats (AVG, OBP, SLG, wOBA, wRC+).

    Args:
        player_id: MLB Stats API player ID.
        season: Season year. Defaults to current season.

    Returns:
        Dict of aggregated season stats.
    """
    pass


def get_batter_vs_pitcher(batter_id: int, pitcher_id: int) -> dict:
    """Fetch career head-to-head stats between a batter and pitcher.

    Args:
        batter_id: MLB Stats API player ID for the batter.
        pitcher_id: MLB Stats API player ID for the pitcher.

    Returns:
        Dict with PA, H, HR, BB, K, AVG, OBP, SLG.
    """
    pass


def get_weather(lat: float, lon: float, game_time_utc: str) -> dict:
    """Fetch weather forecast for a venue at the time of first pitch.

    Args:
        lat: Venue latitude.
        lon: Venue longitude.
        game_time_utc: ISO-8601 UTC datetime string for first pitch.

    Returns:
        Dict with temp_f, wind_mph, wind_direction_degrees, condition, humidity_pct.
    """
    pass


def get_umpire(game_pk: int) -> dict:
    """Fetch the home plate umpire assignment for a game.

    Args:
        game_pk: The MLB Stats API game primary key.

    Returns:
        Dict with umpire name and official_id, or empty dict if not yet assigned.
    """
    pass


def get_umpire_stats(umpire_name: str) -> dict:
    """Fetch historical zone-tendency stats for a home plate umpire.

    Uses cached/scraped data; not available via the official MLB API.

    Args:
        umpire_name: Full name of the umpire.

    Returns:
        Dict with called_strike_rate, bb_per_game, k_per_game, run_impact_score.
    """
    pass
