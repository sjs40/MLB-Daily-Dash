"""Functions for projecting per-game batter and pitcher performance."""

import pandas as pd

from mlb_daily_dash.data.constants import FATIGUE_THRESHOLDS, LEAGUE_AVG, LINEUP_SLOT_PA


def project_batter_game(
    lineup_slot: int,
    batter_stats: dict,
    pitcher_stats: dict,
    park_factors: dict,
    fatigue_multiplier: float = 1.0,
) -> dict:
    """Project a batter's hits, total bases, and home runs for a single game.

    Uses a matchup-adjusted rate model: league-average rates are scaled by
    the batter's and pitcher's individual performance relative to league average,
    then adjusted for park factors and expected PA from the lineup slot.

    Args:
        lineup_slot: Batting order position (1–9).
        batter_stats: Dict with batter H_per_PA, TB_per_PA, HR_per_PA rates.
        pitcher_stats: Dict with pitcher opponent H_per_PA, TB_per_PA, HR_per_PA rates.
        park_factors: Dict with H, TB, HR multipliers from park_factors.get_park_factors().
        fatigue_multiplier: Pitcher fatigue multiplier (≥1.0 means pitcher is more hittable).

    Returns:
        Dict with proj_H, proj_TB, proj_HR for the game.
    """
    pass


def project_lineup(
    lineup: list[dict],
    pitcher_stats: dict,
    park_factors: dict,
    pitcher_fatigue_multiplier: float = 1.0,
) -> pd.DataFrame:
    """Project game stats for every batter in a lineup.

    Args:
        lineup: List of player dicts in batting order, each containing
            batter_stats and lineup_slot.
        pitcher_stats: Opposing pitcher stats dict.
        park_factors: Park factor dict for the venue.
        pitcher_fatigue_multiplier: Fatigue multiplier for the opposing pitcher.

    Returns:
        DataFrame with one row per batter and columns: name, slot,
        proj_H, proj_TB, proj_HR.
    """
    pass


def compute_fatigue_multiplier(days_rest: int, last_pitch_count: int) -> float:
    """Compute a pitcher fatigue multiplier from rest and recent workload.

    A value of 1.0 means no fatigue adjustment. Values above 1.0 mean
    the pitcher is expected to allow more hits/runs due to fatigue.

    Args:
        days_rest: Full days since the pitcher's last outing.
        last_pitch_count: Pitch count in the pitcher's most recent start.

    Returns:
        Fatigue multiplier ≥ 1.0.
    """
    pass
