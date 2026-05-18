"""MLB Daily Dash — main Streamlit entry point."""

import datetime

import streamlit as st

from mlb_daily_dash.components.game_card import render_game_selector
from mlb_daily_dash.components.lineup_table import render_lineup_table
from mlb_daily_dash.components.pitcher_card import render_pitcher_card
from mlb_daily_dash.components.umpire import render_umpire_card
from mlb_daily_dash.components.weather import render_weather_card
from mlb_daily_dash.data.constants import STADIUM_COORDS
from mlb_daily_dash.data.fetcher import (
    get_batter_season_stats,
    get_pitcher_recent_stats,
    get_pitcher_season_stats,
    get_probable_pitchers,
    get_starting_lineup,
    get_todays_games,
    get_umpire,
    get_umpire_stats,
    get_weather,
)
from mlb_daily_dash.utils.park_factors import get_park_factors
from mlb_daily_dash.utils.projections import compute_fatigue_multiplier, project_lineup


def main() -> None:
    """Configure and render the full MLB Daily Dash application."""
    st.set_page_config(
        page_title="MLB Daily Dash",
        page_icon="⚾",
        layout="wide",
    )
    st.title("⚾ MLB Daily Dash")
    st.caption(f"Data for {datetime.date.today().strftime('%A, %B %d, %Y')}")

    with st.sidebar:
        st.header("Today's Games")
        games = get_todays_games()
        selected_game = render_game_selector(games)

    if selected_game is None:
        st.info("Select a game from the sidebar to view its dashboard.")
        return

    game_pk = selected_game["gamePk"]
    venue_id = selected_game.get("venue", {}).get("id")
    venue_info = STADIUM_COORDS.get(venue_id, {})

    pitchers = get_probable_pitchers(game_pk)
    lineups = get_starting_lineup(game_pk)
    umpire = get_umpire(game_pk)
    umpire_stats = get_umpire_stats(umpire.get("name", ""))

    weather = get_weather(
        lat=venue_info.get("lat", 0),
        lon=venue_info.get("lon", 0),
        game_time_utc=selected_game.get("gameDate", ""),
    )

    park_factors = get_park_factors(venue_id)

    col_env, col_ump = st.columns(2)
    with col_env:
        render_weather_card(weather, venue_info.get("outfield_orientation_degrees", 0))
    with col_ump:
        render_umpire_card(umpire, umpire_stats)

    st.divider()

    col_away, col_home = st.columns(2)

    for side, col in [("away", col_away), ("home", col_home)]:
        with col:
            pitcher = pitchers.get(side)
            if pitcher:
                recent = get_pitcher_recent_stats(pitcher["id"])
                season = get_pitcher_season_stats(pitcher["id"])
                render_pitcher_card(pitcher, recent, season)

            lineup = lineups.get(side, [])
            team_name = selected_game.get(side, {}).get("team", {}).get("name", side.title())
            render_lineup_table(lineup, team_name)


if __name__ == "__main__":
    main()
