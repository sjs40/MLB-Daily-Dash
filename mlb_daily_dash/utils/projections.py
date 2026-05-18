"""Per-batter game projection model using matchup-adjusted, credibility-blended rates."""

from mlb_daily_dash.data.constants import LEAGUE_AVG, LINEUP_SLOT_PA

# Maps outcome codes to their field names in split dicts and LEAGUE_AVG keys
_SPLIT_FIELD: dict[str, str] = {"H": "hits", "TB": "tb", "HR": "hr"}
_LEAGUE_KEY: dict[str, str] = {"H": "H_per_PA", "TB": "TB_per_PA", "HR": "HR_per_PA"}


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------

def credibility_weight(pa: int, credibility_pa: int = 50) -> float:
    """Actuarial credibility weight for a split sample.

    Args:
        pa: Plate appearances observed in the split.
        credibility_pa: Full-credibility threshold (50 PA → 50 % weight at that point).

    Returns:
        Float in [0, 1]. Approaches 1 as the sample grows.
    """
    return pa / (pa + credibility_pa)


def blend_rates(split_rate: float, split_pa: int, season_rate: float) -> float:
    """Regress a small-sample split rate toward the full-season mean.

    At split_pa = 0 the result equals season_rate entirely.
    At split_pa >> credibility_pa the result approaches split_rate.

    Args:
        split_rate: Rate computed from the split (e.g. vsRHP hits/PA).
        split_pa: PA count in that split.
        season_rate: Full-season rate used as the Bayesian prior.

    Returns:
        Credibility-weighted blended rate.
    """
    w = credibility_weight(split_pa)
    return split_rate * w + season_rate * (1.0 - w)


def fatigue_multiplier(days_rest: int | None, last_pitch_count: int | None) -> float:
    """Additive pitcher-fatigue multiplier.

    Penalties stack: a pitcher who is short-rested AND had a high pitch count
    gets both adjustments (up to ~1.14).

    Args:
        days_rest: Full calendar days since the pitcher's last outing.
            None is treated as no rest penalty.
        last_pitch_count: Pitch count in the most recent start.
            None is treated as no workload penalty.

    Returns:
        Multiplier >= 1.0 — multiply against hitter's expected output.
    """
    m = 1.0
    if days_rest is not None and days_rest < 4:
        m += 0.06
    if last_pitch_count is not None and last_pitch_count > 95:
        m += 0.08
    return m


def pitcher_suppression(pitcher_splits: dict, handedness: str, outcome: str) -> float:
    """Ratio of pitcher's allowed rate vs. league average for one outcome.

    Values below 1.0 indicate the pitcher suppresses that outcome; above 1.0
    means they allow it at an above-average rate.

    Args:
        pitcher_splits: Full splits dict with vsLeft and vsRight keys from
            get_pitcher_splits().
        handedness: Batter's handedness ("L" or "R") — selects which pitcher
            split to use (pitcher vs lefties if batter is L, etc.).
        outcome: "H", "TB", or "HR".

    Returns:
        Suppression ratio. Returns 1.0 when PA data is missing or zero.
    """
    split_key = "vsLeft" if handedness == "L" else "vsRight"
    split = (pitcher_splits or {}).get(split_key, {})
    pa = split.get("pa", 0)
    if not pa:
        return 1.0

    field = _SPLIT_FIELD.get(outcome, "hits")
    league_key = _LEAGUE_KEY.get(outcome, "H_per_PA")
    league_rate = LEAGUE_AVG.get(league_key) or 1.0

    pitcher_rate = split.get(field, 0) / pa
    return pitcher_rate / league_rate


# ---------------------------------------------------------------------------
# Per-batter projection
# ---------------------------------------------------------------------------

def project_batter(
    batter_split: dict,
    batter_season: dict,
    pitcher_splits: dict,
    pitcher_hand: str,
    batter_hand: str,
    park_factors: dict,
    workload: dict,
    lineup_slot: int,
) -> dict:
    """Project a batter's expected hits, total bases, and home runs for one game.

    Model per outcome:
        x = blended_rate × pitcher_suppression × park_factor × fatigue × slot_PA

    Args:
        batter_split: Pre-selected single split dict for the batter vs. this
            pitcher's handedness (vsLeft when pitcher throws L, vsRight otherwise).
            Keys: pa, hits, tb, hr.
        batter_season: Full-season stats dict from get_top_batters_by_pa().
            Keys: plateAppearances, hits, totalBases, homeRuns.
        pitcher_splits: Full pitcher splits dict (vsLeft + vsRight) from
            get_pitcher_splits().
        pitcher_hand: Pitcher's throwing hand ("L" or "R").
        batter_hand: Batter's handedness ("L" or "R") — used for pitcher_suppression.
        park_factors: Park factor dict from get_park_factors(). Keys: hits_factor, hr_factor.
        workload: Dict from get_pitcher_workload(). Keys: days_rest, last_pitch_count.
        lineup_slot: Batting order position 1–9.

    Returns:
        Dict with xH, xTB, xHR rounded to 2 decimal places.
    """
    season_pa: int = batter_season.get("plateAppearances") or 0
    split_pa: int = batter_split.get("pa") or 0

    # Season rates (fallback to league average when no data)
    if season_pa:
        s_H = batter_season.get("hits", 0) / season_pa
        s_TB = batter_season.get("totalBases", 0) / season_pa
        s_HR = batter_season.get("homeRuns", 0) / season_pa
    else:
        s_H = LEAGUE_AVG["H_per_PA"]
        s_TB = LEAGUE_AVG["TB_per_PA"]
        s_HR = LEAGUE_AVG["HR_per_PA"]

    # Split rates (when PA = 0, blend_rates will fall back to season rate fully)
    if split_pa:
        sp_H = batter_split.get("hits", 0) / split_pa
        sp_TB = batter_split.get("tb", 0) / split_pa
        sp_HR = batter_split.get("hr", 0) / split_pa
    else:
        sp_H, sp_TB, sp_HR = s_H, s_TB, s_HR

    blended_H = blend_rates(sp_H, split_pa, s_H)
    blended_TB = blend_rates(sp_TB, split_pa, s_TB)
    blended_HR = blend_rates(sp_HR, split_pa, s_HR)

    # Pitcher suppression uses the batter's handedness to pick the right split
    sup_H = pitcher_suppression(pitcher_splits, batter_hand, "H")
    sup_TB = pitcher_suppression(pitcher_splits, batter_hand, "TB")
    sup_HR = pitcher_suppression(pitcher_splits, batter_hand, "HR")

    # Park factors — TB uses hits_factor same as H
    pf_hits = park_factors.get("hits_factor", 1.0)
    pf_hr = park_factors.get("hr_factor", 1.0)

    fatigue = fatigue_multiplier(
        workload.get("days_rest"),
        workload.get("last_pitch_count"),
    )

    slot_pa = LINEUP_SLOT_PA.get(lineup_slot, 4.0)

    xH_val   = blended_H  * sup_H  * pf_hits * fatigue * slot_pa
    xTB_val  = blended_TB * sup_TB * pf_hits * fatigue * slot_pa
    xHR_val  = blended_HR * sup_HR * pf_hr   * fatigue * slot_pa
    xTBH_val = max(0.0, xTB_val - xHR_val)

    return {
        "xH":   round(xH_val,   2),
        "xTB":  round(xTB_val,  2),
        "xHR":  round(xHR_val,  2),
        "xTBH": round(xTBH_val, 2),
    }


# ---------------------------------------------------------------------------
# Team-level projection
# ---------------------------------------------------------------------------

def project_team(
    batters: list[dict],
    pitcher_splits: dict,
    pitcher_hand: str,
    park_factors: dict,
    workload: dict,
) -> dict:
    """Sum projected stats across an entire batting lineup.

    Batters flagged on_il=True are skipped. Batters missing split or season
    data are also skipped silently.

    Each batter dict must contain:
        batter_split  — pre-selected vsLeft / vsRight split dict
        batter_season — season stats dict from get_top_batters_by_pa()
        batter_hand   — "L" or "R"
        lineup_slot   — int 1–9
        on_il         — bool (optional, default False)

    Args:
        batters: List of batter dicts in batting order.
        pitcher_splits: Full pitcher splits dict from get_pitcher_splits().
        pitcher_hand: Pitcher's throwing hand ("L" or "R").
        park_factors: Park factor dict from get_park_factors().
        workload: Dict from get_pitcher_workload().

    Returns:
        Dict with team-total xH, xTB, xHR rounded to 2 decimal places.
    """
    totals: dict[str, float] = {"xH": 0.0, "xTB": 0.0, "xHR": 0.0, "xTBH": 0.0}

    for batter in batters:
        if batter.get("on_il"):
            continue

        batter_split = batter.get("batter_split")
        batter_season = batter.get("batter_season")
        if not batter_split or not batter_season:
            continue

        proj = project_batter(
            batter_split=batter_split,
            batter_season=batter_season,
            pitcher_splits=pitcher_splits,
            pitcher_hand=pitcher_hand,
            batter_hand=batter.get("batter_hand", "R"),
            park_factors=park_factors,
            workload=workload,
            lineup_slot=batter.get("lineup_slot", 5),
        )

        for key in totals:
            totals[key] += proj[key]

    return {k: round(v, 2) for k, v in totals.items()}
