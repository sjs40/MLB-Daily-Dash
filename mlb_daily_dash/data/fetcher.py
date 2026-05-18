"""Functions for fetching MLB data from the free MLB Stats API (statsapi.mlb.com)."""

import datetime

import requests
import streamlit as st

BASE_URL = "https://statsapi.mlb.com"
_TIMEOUT = 10


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get(path: str, params: dict | None = None) -> dict:
    """GET from the MLB Stats API and return parsed JSON."""
    resp = requests.get(f"{BASE_URL}{path}", params=params, timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _ip_to_float(ip_str: str) -> float:
    """Convert baseball innings-pitched notation to a real decimal.

    "6.1" → 6.333 (6 full innings + 1 out = 1/3 of an inning).
    """
    try:
        whole, frac = str(ip_str).split(".")
        return int(whole) + int(frac) / 3
    except (ValueError, AttributeError):
        try:
            return float(ip_str)
        except (ValueError, TypeError):
            return 0.0


def _parse_pitcher(node: dict | None) -> dict:
    """Extract id, name, and throwing hand from a probablePitcher node."""
    if not node:
        return {"id": None, "name": None, "hand": None}
    return {
        "id": node.get("id"),
        "name": node.get("fullName"),
        "hand": (node.get("pitchHand") or {}).get("code"),
    }


def _to_float(value: object) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _zero_split() -> dict:
    return {"pa": 0, "hits": 0, "hr": 0, "tb": 0, "avg": 0.0}


def _empty_splits() -> dict:
    return {"vsLeft": _zero_split(), "vsRight": _zero_split()}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@st.cache_data(ttl=3600)
def get_today_schedule() -> list[dict]:
    """Fetch today's MLB schedule with probable pitchers and venue details.

    Returns:
        List of game dicts, each with keys: gamePk, gameDate,
        venue (id, name), away and home each containing teamId, teamName,
        abbreviation, and pitcher (id, name, hand). Pitcher fields are None
        when no probable starter has been announced.
    """
    today = datetime.date.today().strftime("%Y-%m-%d")
    try:
        data = _get(
            "/api/v1/schedule",
            params={
                "sportId": 1,
                "date": today,
                "hydrate": "probablePitcher,team,venue",
            },
        )
    except Exception:
        return []

    games: list[dict] = []
    for date_block in data.get("dates", []):
        for g in date_block.get("games", []):
            teams = g.get("teams", {})
            away_raw = teams.get("away", {})
            home_raw = teams.get("home", {})
            games.append({
                "gamePk": g.get("gamePk"),
                "gameDate": g.get("gameDate"),
                "venue": {
                    "id": (g.get("venue") or {}).get("id"),
                    "name": (g.get("venue") or {}).get("name"),
                },
                "away": {
                    "teamId": (away_raw.get("team") or {}).get("id"),
                    "teamName": (away_raw.get("team") or {}).get("name"),
                    "abbreviation": (away_raw.get("team") or {}).get("abbreviation"),
                    "pitcher": _parse_pitcher(away_raw.get("probablePitcher")),
                },
                "home": {
                    "teamId": (home_raw.get("team") or {}).get("id"),
                    "teamName": (home_raw.get("team") or {}).get("name"),
                    "abbreviation": (home_raw.get("team") or {}).get("abbreviation"),
                    "pitcher": _parse_pitcher(home_raw.get("probablePitcher")),
                },
            })
    return games


@st.cache_data(ttl=3600)
def get_team_roster(team_id: int) -> list[dict]:
    """Fetch the active roster for a team, excluding pitchers (position code "1").

    Args:
        team_id: MLB Stats API team ID.

    Returns:
        List of dicts with personId, fullName, position (code, abbreviation).
    """
    try:
        data = _get(f"/api/v1/teams/{team_id}/roster", params={"rosterType": "active"})
    except Exception:
        return []

    players: list[dict] = []
    for entry in data.get("roster", []):
        pos = entry.get("position", {})
        if pos.get("code") == "1":
            continue
        players.append({
            "personId": entry["person"]["id"],
            "fullName": entry["person"]["fullName"],
            "position": {
                "code": pos.get("code"),
                "abbreviation": pos.get("abbreviation"),
            },
        })
    return players


@st.cache_data(ttl=3600)
def get_top_batters_by_pa(team_id: int, season: int, n: int = 9) -> list[dict]:
    """Return the top n non-pitcher roster members ranked by plate appearances.

    Makes one API call per non-pitcher on the active roster; results are cached.

    Args:
        team_id: MLB Stats API team ID.
        season: Season year.
        n: Number of batters to return (default 9).

    Returns:
        List of up to n dicts with personId, fullName, position,
        plateAppearances, avg, hits, homeRuns, totalBases.
    """
    roster = get_team_roster(team_id)
    if not roster:
        return []

    batters: list[dict] = []
    for player in roster:
        pid = player["personId"]
        try:
            data = _get(
                f"/api/v1/people/{pid}/stats",
                params={"stats": "season", "group": "hitting", "season": season},
            )
        except Exception:
            continue

        stat_blocks = data.get("stats") or []
        splits = stat_blocks[0].get("splits", []) if stat_blocks else []
        if not splits:
            continue

        s = splits[0].get("stat", {})
        batters.append({
            "personId": pid,
            "fullName": player["fullName"],
            "position": player["position"],
            "plateAppearances": s.get("plateAppearances", 0),
            "avg": s.get("avg", ".000"),
            "hits": s.get("hits", 0),
            "homeRuns": s.get("homeRuns", 0),
            "totalBases": s.get("totalBases", 0),
        })

    batters.sort(key=lambda b: b["plateAppearances"], reverse=True)
    return batters[:n]


def _fetch_splits(player_id: int, season: int, group: str, window: str) -> dict:
    """Shared logic for batter and pitcher vs-hand splits."""
    params: dict = {
        "stats": "statSplits",
        "group": group,
        "season": season,
        "sitCodes": "vl,vr",
    }
    if window == "rolling30":
        today = datetime.date.today()
        start = today - datetime.timedelta(days=30)
        params["startDate"] = start.strftime("%m/%d/%Y")
        params["endDate"] = today.strftime("%m/%d/%Y")

    try:
        data = _get(f"/api/v1/people/{player_id}/stats", params=params)
    except Exception:
        return _empty_splits()

    result = _empty_splits()
    for stat_block in data.get("stats", []):
        for split in stat_block.get("splits", []):
            code = (split.get("split") or {}).get("code", "")
            s = split.get("stat", {})
            entry = {
                "pa": s.get("plateAppearances", 0),
                "hits": s.get("hits", 0),
                "hr": s.get("homeRuns", 0),
                "tb": s.get("totalBases", 0),
                "avg": _to_float(s.get("avg", ".000")),
            }
            if code == "vl":
                result["vsLeft"] = entry
            elif code == "vr":
                result["vsRight"] = entry
    return result


@st.cache_data(ttl=3600)
def get_batter_splits(player_id: int, season: int, window: str = "season") -> dict:
    """Return a batter's hitting splits vs left-handed and right-handed pitchers.

    Args:
        player_id: MLB Stats API player ID.
        season: Season year.
        window: "season" for full-season splits, "rolling30" for last 30 days.

    Returns:
        Dict with vsLeft and vsRight keys, each containing pa, hits, hr, tb, avg.
    """
    return _fetch_splits(player_id, season, "hitting", window)


@st.cache_data(ttl=3600)
def get_pitcher_splits(player_id: int, season: int, window: str = "season") -> dict:
    """Return a pitcher's allowed-hit splits vs left-handed and right-handed batters.

    Args:
        player_id: MLB Stats API player ID.
        season: Season year.
        window: "season" for full-season splits, "rolling30" for last 30 days.

    Returns:
        Dict with vsLeft and vsRight keys, each containing pa, hits, hr, tb, avg.
    """
    return _fetch_splits(player_id, season, "pitching", window)


@st.cache_data(ttl=3600)
def get_pitcher_workload(player_id: int, season: int) -> dict:
    """Return rest days, last pitch count, and rolling IP total for a pitcher.

    Args:
        player_id: MLB Stats API player ID.
        season: Season year.

    Returns:
        Dict with days_rest (int), last_pitch_count (int), last_3_ip (float).
        All values are 0 / 0.0 when no game log entries are found.
    """
    empty: dict = {"days_rest": 0, "last_pitch_count": 0, "last_3_ip": 0.0}
    try:
        data = _get(
            f"/api/v1/people/{player_id}/stats",
            params={"stats": "gameLog", "group": "pitching", "season": season},
        )
    except Exception:
        return empty

    entries: list[dict] = []
    for stat_block in data.get("stats", []):
        for split in stat_block.get("splits", []):
            raw_date = split.get("date", "")
            s = split.get("stat", {})
            try:
                game_date = datetime.date.fromisoformat(raw_date)
            except ValueError:
                continue
            entries.append({
                "date": game_date,
                "pitches": s.get("numberOfPitches", 0),
                "ip": _ip_to_float(s.get("inningsPitched", "0.0")),
            })

    if not entries:
        return empty

    entries.sort(key=lambda e: e["date"])
    most_recent = entries[-1]
    last_3_ip = sum(e["ip"] for e in entries[-3:])

    return {
        "days_rest": (datetime.date.today() - most_recent["date"]).days,
        "last_pitch_count": most_recent["pitches"],
        "last_3_ip": round(last_3_ip, 2),
    }


_UMP_SCORECARDS_URL = "https://umpscorecards.com/api/umpires/"

_STATUS_MAP: dict[str, str] = {
    "10-day il": "IL10",
    "15-day il": "IL10",
    "7-day il": "IL10",
    "60-day il": "IL60",
    "day-to-day": "DTD",
}


@st.cache_data(ttl=3600)
def get_injury_report(team_id: int) -> list[dict]:
    """Fetch the injured list / day-to-day roster for a team.

    Args:
        team_id: MLB Stats API team ID.

    Returns:
        List of dicts with personId, fullName, and status ("IL10", "IL60", "DTD",
        or the raw description string when the status is not recognised).
    """
    try:
        data = _get(f"/api/v1/teams/{team_id}/roster", params={"rosterType": "injuries"})
    except Exception:
        return []

    injured: list[dict] = []
    for entry in data.get("roster", []):
        raw = (entry.get("status") or {}).get("description", "")
        injured.append({
            "personId": entry["person"]["id"],
            "fullName": entry["person"]["fullName"],
            "status": _STATUS_MAP.get(raw.lower(), raw),
        })
    return injured


@st.cache_data(ttl=3600)
def get_umpire_for_game(game_pk: int) -> dict | None:
    """Return the home plate umpire for a game from the boxscore officials list.

    Umpire assignments are typically posted a few hours before first pitch;
    this function returns None rather than raising when they are not yet available.

    Args:
        game_pk: MLB Stats API game primary key.

    Returns:
        Dict with name (str) and id (int), or None if not yet assigned.
    """
    try:
        data = _get(f"/api/v1/game/{game_pk}/boxscore")
    except Exception:
        return None

    for official in data.get("officials", []):
        if official.get("officialType") == "Home Plate":
            person = official.get("official", {})
            return {
                "name": person.get("fullName"),
                "id": person.get("id"),
            }
    return None


@st.cache_data(ttl=86400)
def get_umpire_stats(umpire_name: str) -> dict | None:
    """Fetch career zone-tendency stats for an umpire from UmpScorecards.

    Career aggregates change slowly, so results are cached for 24 hours.

    Args:
        umpire_name: Full name of the umpire (e.g. "Angel Hernandez").

    Returns:
        Dict with name, k_pct, bb_pct, k_pct_delta, bb_pct_delta, run_impact,
        or None when the umpire is not found or the API is unavailable.
    """
    if not umpire_name:
        return None

    try:
        resp = requests.get(
            _UMP_SCORECARDS_URL,
            params={"name": umpire_name},
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception:
        return None

    # The endpoint returns a list; take the closest name match (first result).
    if isinstance(payload, list):
        if not payload:
            return None
        record = payload[0]
    elif isinstance(payload, dict):
        record = payload
    else:
        return None

    return {
        "name": record.get("name", umpire_name),
        "k_pct": _to_float(record.get("k_pct")),
        "bb_pct": _to_float(record.get("bb_pct")),
        "k_pct_delta": _to_float(record.get("k_pct_delta")),
        "bb_pct_delta": _to_float(record.get("bb_pct_delta")),
        "run_impact": _to_float(record.get("run_impact")),
    }
