"""Functions for retrieving and applying park factor adjustments."""

import pandas as pd


def get_park_factors(venue_id: int, season: int | None = None) -> dict:
    """Return park factor multipliers for hits, total bases, and home runs.

    A factor of 1.0 is neutral. Values above 1.0 indicate the park inflates
    that stat relative to a league-average environment.

    Args:
        venue_id: MLB Stats API venue ID.
        season: Season year to pull factors for. Defaults to current season.

    Returns:
        Dict with keys H, TB, HR containing float multipliers.
    """
    pass


def load_historical_park_factors(seasons: int = 3) -> pd.DataFrame:
    """Load multi-season park factor data for all MLB venues.

    Averages across recent seasons to smooth small-sample noise.

    Args:
        seasons: Number of most recent seasons to average over.

    Returns:
        DataFrame indexed by venue_id with columns: H, TB, HR, season_range.
    """
    pass


def apply_park_factors(raw_projections: dict, park_factors: dict) -> dict:
    """Scale raw per-PA rate projections by park factor multipliers.

    Args:
        raw_projections: Dict with proj_H, proj_TB, proj_HR before park adjustment.
        park_factors: Dict with H, TB, HR multipliers.

    Returns:
        Adjusted projections dict with the same keys.
    """
    pass
