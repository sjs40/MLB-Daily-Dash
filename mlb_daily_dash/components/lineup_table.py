"""Streamlit component that renders a team batting lineup with game projections."""

import math

import pandas as pd
import streamlit as st

from mlb_daily_dash.utils.projections import project_batter

# Display colours for projected-stat columns
_COLOR_XH  = "#4F8EF7"   # blue
_COLOR_XTB = "#2EB87E"   # green
_COLOR_XHR = "#F5A623"   # amber

# IL status codes that suppress projections entirely
_HARD_IL = {"IL10", "IL60"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _il_status(batter: dict, il_by_id: dict[int, str], il_by_name: dict[str, str]) -> str | None:
    """Return the batter's IL status string, or None if active."""
    pid = batter.get("personId")
    name = batter.get("fullName", "")
    return il_by_id.get(pid) or il_by_name.get(name)


def _name_with_dot(name: str, status: str | None) -> str:
    """Prefix the player name with a coloured Unicode dot for IL/DTD status."""
    if status in _HARD_IL:
        return f"\U0001f534 {name}"   # 🔴
    if status == "DTD":
        return f"\U0001f7e0 {name}"   # 🟠
    return name


def _safe_float(value: object) -> float:
    """Convert a value to float, returning 0.0 on failure (e.g. '.300' strings)."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def _style_proj_col(series: pd.Series, color: str) -> list[str]:
    """Return per-cell CSS for a projection column: coloured or grey for NaN."""
    return [
        f"color: {color}" if not (isinstance(v, float) and math.isnan(v)) else "color: #888888"
        for v in series
    ]


# ---------------------------------------------------------------------------
# Public component
# ---------------------------------------------------------------------------

def render_lineup_table(
    team_name: str,
    batters: list[dict],
    pitcher: dict,
    pitcher_splits: dict,
    pitcher_workload: dict,
    park_factors: dict,
    split_window: str,
    injury_report: list[dict],
) -> None:
    """Render a styled lineup table with game projections for one team.

    Each batter dict is expected to contain:
        personId, fullName, position (abbreviation),
        avg (str), homeRuns (int), totalBases (int), hits (int),
        plateAppearances (int),
        splits: {"vsLeft": {...}, "vsRight": {...}}  (from get_batter_splits),
        batter_hand: "L" or "R"  (defaults to "R" if absent).

    Args:
        team_name: Team display name used in the section header.
        batters: List of batter dicts in batting order (index 0 = slot 1).
        pitcher: Opposing pitcher dict with at minimum a "hand" key ("L" or "R").
        pitcher_splits: Full pitcher splits dict (vsLeft + vsRight).
        pitcher_workload: Dict from get_pitcher_workload().
        park_factors: Dict from get_park_factors().
        split_window: "season" or "rolling30" — shown as a caption.
        injury_report: List of injury dicts from get_injury_report().
    """
    pitcher_hand: str = (pitcher or {}).get("hand") or "R"
    hand_label = "LHP" if pitcher_hand == "L" else "RHP"

    st.subheader(f"{team_name} Lineup · vs {hand_label}")
    st.caption(f"Split window: {split_window}")

    # Pre-build IL lookups for O(1) access
    il_by_id: dict[int, str] = {
        e["personId"]: e["status"] for e in (injury_report or []) if "personId" in e
    }
    il_by_name: dict[str, str] = {
        e["fullName"]: e["status"] for e in (injury_report or []) if "fullName" in e
    }

    rows: list[dict] = []
    total_xh = total_xtb = total_xhr = 0.0

    for slot, batter in enumerate(batters, start=1):
        status = _il_status(batter, il_by_id, il_by_name)
        display_name = _name_with_dot(batter.get("fullName", "Unknown"), status)
        pos = (batter.get("position") or {}).get("abbreviation", "")

        avg_float = _safe_float(batter.get("avg", 0))
        hr = int(batter.get("homeRuns") or 0)
        tb = int(batter.get("totalBases") or 0)

        if status in _HARD_IL:
            xh = xtb = xhr = float("nan")
        else:
            splits = batter.get("splits") or {}
            batter_split = splits.get("vsLeft" if pitcher_hand == "L" else "vsRight") or {}

            batter_season = {
                "plateAppearances": batter.get("plateAppearances") or 0,
                "hits": batter.get("hits") or 0,
                "totalBases": tb,
                "homeRuns": hr,
            }

            proj = project_batter(
                batter_split=batter_split,
                batter_season=batter_season,
                pitcher_splits=pitcher_splits,
                pitcher_hand=pitcher_hand,
                batter_hand=batter.get("batter_hand") or "R",
                park_factors=park_factors,
                workload=pitcher_workload,
                lineup_slot=slot,
            )
            xh, xtb, xhr = proj["xH"], proj["xTB"], proj["xHR"]
            total_xh  += xh
            total_xtb += xtb
            total_xhr += xhr

        rows.append({
            "#":      slot,
            "Player": display_name,
            "Pos":    pos,
            "AVG":    avg_float,
            "HR":     hr,
            "TB":     tb,
            "xH":     xh,
            "xTB":    xtb,
            "xHR":    xhr,
        })

    df = pd.DataFrame(rows)

    styled = (
        df.style
        .apply(_style_proj_col, color=_COLOR_XH,  subset=["xH"])
        .apply(_style_proj_col, color=_COLOR_XTB, subset=["xTB"])
        .apply(_style_proj_col, color=_COLOR_XHR, subset=["xHR"])
        .format(
            {
                "AVG": "{:.3f}",
                "xH":  "{:.2f}",
                "xTB": "{:.2f}",
                "xHR": "{:.2f}",
            },
            na_rep="—",
        )
        .hide(axis="index")
    )

    st.dataframe(
        styled,
        column_config={
            "#":      st.column_config.NumberColumn(width="small"),
            "Player": st.column_config.TextColumn(width="medium"),
            "Pos":    st.column_config.TextColumn(width="small"),
            "HR":     st.column_config.NumberColumn(width="small"),
            "TB":     st.column_config.NumberColumn(width="small"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # Team totals with matching column colours
    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f"<span style='color:{_COLOR_XH}'><b>Team xH</b></span>&nbsp;&nbsp;{total_xh:.2f}",
        unsafe_allow_html=True,
    )
    c2.markdown(
        f"<span style='color:{_COLOR_XTB}'><b>Team xTB</b></span>&nbsp;&nbsp;{total_xtb:.2f}",
        unsafe_allow_html=True,
    )
    c3.markdown(
        f"<span style='color:{_COLOR_XHR}'><b>Team xHR</b></span>&nbsp;&nbsp;{total_xhr:.2f}",
        unsafe_allow_html=True,
    )
