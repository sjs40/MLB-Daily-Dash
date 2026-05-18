"""MLB Daily Dash — main Streamlit application."""

import datetime
from datetime import timezone, timedelta

import streamlit as st

from mlb_daily_dash.data.constants import STADIUM_COORDS
from mlb_daily_dash.data.fetcher import (
    get_batter_splits,
    get_injury_report,
    get_pitcher_splits,
    get_pitcher_workload,
    get_today_schedule,
    get_top_batters_by_pa,
)
from mlb_daily_dash.utils.park_factors import get_park_factors
from mlb_daily_dash.components.lineup_table import render_lineup_table
from mlb_daily_dash.components.pitcher_card import render_pitcher_card
from mlb_daily_dash.components.umpire import render_umpire
from mlb_daily_dash.components.weather import render_weather

_SEASON: int = datetime.date.today().year
_EDT = timezone(timedelta(hours=-4))  # EDT; approximation valid for the MLB season


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _format_game_time(game_date_utc: str) -> str:
    """Convert an ISO-8601 UTC timestamp to a short Eastern-time string."""
    try:
        dt = datetime.datetime.fromisoformat(game_date_utc.replace("Z", "+00:00"))
        et = dt.astimezone(_EDT)
        try:
            return et.strftime("%-I:%M %p ET")   # Linux/macOS
        except ValueError:
            return et.strftime("%I:%M %p ET").lstrip("0")  # Windows
    except Exception:
        return "TBD"


def _split_param(label: str) -> str:
    """Map radio label to fetcher window parameter."""
    return "rolling30" if label == "30-day" else "season"


def _augment_batters(batters: list[dict], split_window: str) -> list[dict]:
    """Attach split data to each batter dict returned by get_top_batters_by_pa."""
    result = []
    for b in batters:
        pid = b.get("personId")
        splits = get_batter_splits(pid, _SEASON, split_window) if pid else {}
        result.append({**b, "splits": splits, "batter_hand": b.get("batter_hand", "R")})
    return result


def _platoon_label(home_batters: list[dict], away_pitcher: dict) -> str:
    """Return a colour-coded platoon-advantage markdown string.

    Counts how many of the top-9 home batters have a handedness advantage vs the
    away (starting) pitcher.  Batter handedness defaults to 'R' when not fetched.
    """
    pitcher_hand = (away_pitcher or {}).get("hand")
    if not pitcher_hand:
        return "Platoon: **TBD**"
    # batter_hand defaults to 'R'; approximate until batter hand API call added
    count = sum(1 for b in home_batters if b.get("batter_hand", "R") != pitcher_hand)
    label = f"Platoon adv **{count}/9** vs {pitcher_hand}HP"
    if count >= 6:
        return f":green[{label}]"
    if count <= 3:
        return f":red[{label}]"
    return label


def _park_factor_label(factor: float, stat: str) -> str:
    """Return a colour-coded markdown string for a park factor."""
    badge = f"{stat} **{factor:.2f}×**"
    if factor > 1.05:
        return f":green[{badge}]"
    if factor < 0.95:
        return f":red[{badge}]"
    return badge


def _render_flags(home_batters: list[dict], away_pitcher: dict, park_fac: dict) -> None:
    """Render the four summary-flag tiles at the top of a game block."""
    hr_factor   = park_fac.get("hr_factor", 1.0)
    hits_factor = park_fac.get("hits_factor", 1.0)
    roof        = park_fac.get("roof", "open")
    roof_icon   = {"open": "☀️", "retractable": "🔄", "dome": "🏟️"}.get(roof, "")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(_platoon_label(home_batters, away_pitcher))
    c2.markdown(_park_factor_label(hr_factor, "HR"))
    c3.markdown(_park_factor_label(hits_factor, "Hits"))
    c4.markdown(f"{roof_icon} **{roof.capitalize()}**")


# ---------------------------------------------------------------------------
# Per-game renderer
# ---------------------------------------------------------------------------

def _render_game(game: dict, split_window: str) -> None:
    """Render the full data block for one MLB game inside an expander."""
    game_pk   = game["gamePk"]
    venue_id  = (game.get("venue") or {}).get("id")
    away      = game.get("away", {})
    home      = game.get("home", {})
    away_pid  = (away.get("pitcher") or {}).get("id")
    home_pid  = (home.get("pitcher") or {}).get("id")

    with st.spinner("Loading game data…"):
        # Batters
        away_batters_raw = get_top_batters_by_pa(away["teamId"], _SEASON)
        home_batters_raw = get_top_batters_by_pa(home["teamId"], _SEASON)
        away_batters = _augment_batters(away_batters_raw, split_window)
        home_batters = _augment_batters(home_batters_raw, split_window)

        # Pitcher splits + workload
        away_splits   = get_pitcher_splits(away_pid, _SEASON, split_window) if away_pid else {}
        home_splits   = get_pitcher_splits(home_pid, _SEASON, split_window) if home_pid else {}
        away_workload = get_pitcher_workload(away_pid, _SEASON) if away_pid else {}
        home_workload = get_pitcher_workload(home_pid, _SEASON) if home_pid else {}

        # Injuries
        away_il = get_injury_report(away["teamId"])
        home_il = get_injury_report(home["teamId"])

    park_fac = get_park_factors(venue_id)

    # ── Flag row ─────────────────────────────────────────────────────────────
    _render_flags(home_batters, away.get("pitcher") or {}, park_fac)

    # ── Environment row ──────────────────────────────────────────────────────
    env_col, ump_col = st.columns(2)
    with env_col:
        render_weather(venue_id)
    with ump_col:
        render_umpire(game_pk)

    st.divider()

    # ── Lineup columns ───────────────────────────────────────────────────────
    # Left:  away batters face the HOME pitcher
    # Right: home batters face the AWAY pitcher
    left_col, right_col = st.columns(2)

    with left_col:
        render_pitcher_card(
            pitcher=home.get("pitcher") or {},
            splits=home_splits,
            workload=home_workload,
            split_window=split_window,
        )
        render_lineup_table(
            team_name=away.get("teamName", "Away"),
            batters=away_batters,
            pitcher=home.get("pitcher") or {},
            pitcher_splits=home_splits,
            pitcher_workload=home_workload,
            park_factors=park_fac,
            split_window=split_window,
            injury_report=away_il,
        )

    with right_col:
        render_pitcher_card(
            pitcher=away.get("pitcher") or {},
            splits=away_splits,
            workload=away_workload,
            split_window=split_window,
        )
        render_lineup_table(
            team_name=home.get("teamName", "Home"),
            batters=home_batters,
            pitcher=away.get("pitcher") or {},
            pitcher_splits=away_splits,
            pitcher_workload=away_workload,
            park_factors=park_fac,
            split_window=split_window,
            injury_report=home_il,
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Configure the page and render the full MLB Daily Dash."""
    st.set_page_config(
        page_title="MLB Daily Dash",
        page_icon="⚾",
        layout="wide",
    )

    st.title("⚾ MLB Daily Dash")
    st.markdown(
        f"**{datetime.date.today().strftime('%A, %B %d, %Y')}** · "
        "Lineup intelligence · Season & 30-day splits · Park-adjusted projections"
    )

    split_label = st.radio("Split window", ["Season", "30-day"], horizontal=True)
    split_window = _split_param(split_label)

    st.divider()

    with st.spinner("Loading today's schedule…"):
        games = get_today_schedule()

    if not games:
        st.info("No games scheduled today.")
        return

    for game in games:
        away      = game.get("away", {})
        home      = game.get("home", {})
        away_abbr = away.get("abbreviation", "AWY")
        home_abbr = home.get("abbreviation", "HME")
        game_time = _format_game_time(game.get("gameDate", ""))

        with st.expander(f"{away_abbr} @ {home_abbr}  ·  {game_time}"):
            _render_game(game, split_window)

    st.divider()
    st.caption(
        "MLB Daily Dash · Data: MLB Stats API · Umpire Scorecards · OpenWeatherMap · "
        "Projections: credibility-weighted splits × pitcher suppression × park factor × fatigue"
    )


if __name__ == "__main__":
    main()
