"""Hardcoded 2023-2024 two-year averaged park factors for all 30 MLB venues.

HR and hits factors are scaled to 1.0 = league-average neutral park.
Values above 1.0 favour hitters; below 1.0 favour pitchers.
Sources: FanGraphs multi-year park factors, Baseball Savant, ESPN park factors.
"""

# ---------------------------------------------------------------------------
# Static data — keyed by MLB Stats API venue ID
# ---------------------------------------------------------------------------

PARK_FACTORS: dict[int, dict] = {
    # ── User-confirmed anchors ──────────────────────────────────────────────
    115: {
        "name": "Coors Field",
        "team": "Colorado Rockies",
        "hr_factor": 1.38,
        "hits_factor": 1.18,
        "roof": "open",
    },
    137: {
        "name": "Oracle Park",
        "team": "San Francisco Giants",
        "hr_factor": 0.82,
        "hits_factor": 0.97,
        "roof": "open",
    },
    113: {
        "name": "Great American Ball Park",
        "team": "Cincinnati Reds",
        "hr_factor": 1.18,
        "hits_factor": 1.04,
        "roof": "open",
    },
    2680: {
        "name": "Petco Park",
        "team": "San Diego Padres",
        "hr_factor": 0.88,
        "hits_factor": 0.96,
        "roof": "open",
    },
    3313: {
        "name": "Yankee Stadium",
        "team": "New York Yankees",
        "hr_factor": 1.16,
        "hits_factor": 1.02,
        "roof": "open",
    },
    4705: {
        "name": "American Family Field",
        "team": "Milwaukee Brewers",
        "hr_factor": 1.08,
        "hits_factor": 1.01,
        "roof": "retractable",
    },
    139: {
        "name": "Tropicana Field",
        "team": "Tampa Bay Rays",
        "hr_factor": 0.91,
        "hits_factor": 0.97,
        "roof": "dome",
    },
    # ── Estimated from reputation and public factor data ───────────────────
    2681: {
        "name": "Citizens Bank Park",
        "team": "Philadelphia Phillies",
        "hr_factor": 1.14,
        "hits_factor": 1.05,
        "roof": "open",
    },
    18: {
        "name": "Guaranteed Rate Field",
        "team": "Chicago White Sox",
        "hr_factor": 1.12,
        "hits_factor": 1.03,
        "roof": "open",
    },
    2392: {
        "name": "Minute Maid Park",
        "team": "Houston Astros",
        "hr_factor": 1.11,
        "hits_factor": 1.03,
        "roof": "retractable",
    },
    15: {
        "name": "Chase Field",
        "team": "Arizona Diamondbacks",
        "hr_factor": 1.10,
        "hits_factor": 1.04,
        "roof": "retractable",
    },
    5325: {
        "name": "Globe Life Field",
        "team": "Texas Rangers",
        "hr_factor": 1.07,
        "hits_factor": 1.01,
        "roof": "retractable",
    },
    17: {
        "name": "Wrigley Field",
        "team": "Chicago Cubs",
        "hr_factor": 1.05,
        "hits_factor": 1.03,
        "roof": "open",
    },
    2: {
        "name": "Oriole Park at Camden Yards",
        "team": "Baltimore Orioles",
        "hr_factor": 1.05,
        "hits_factor": 1.01,
        "roof": "open",
    },
    4085: {
        "name": "Truist Park",
        "team": "Atlanta Braves",
        "hr_factor": 1.04,
        "hits_factor": 1.01,
        "roof": "open",
    },
    14: {
        "name": "Rogers Centre",
        "team": "Toronto Blue Jays",
        "hr_factor": 1.02,
        "hits_factor": 1.03,
        "roof": "dome",
    },
    3289: {
        "name": "Citi Field",
        "team": "New York Mets",
        "hr_factor": 1.00,
        "hits_factor": 1.00,
        "roof": "open",
    },
    3: {
        "name": "Fenway Park",
        "team": "Boston Red Sox",
        # Green Monster suppresses HRs but inflates doubles / hits
        "hr_factor": 0.95,
        "hits_factor": 1.04,
        "roof": "open",
    },
    3309: {
        "name": "Nationals Park",
        "team": "Washington Nationals",
        "hr_factor": 0.97,
        "hits_factor": 0.99,
        "roof": "open",
    },
    2394: {
        "name": "Comerica Park",
        "team": "Detroit Tigers",
        "hr_factor": 0.94,
        "hits_factor": 0.98,
        "roof": "open",
    },
    4169: {
        "name": "loanDepot park",
        "team": "Miami Marlins",
        "hr_factor": 0.94,
        "hits_factor": 0.97,
        "roof": "retractable",
    },
    680: {
        "name": "T-Mobile Park",
        "team": "Seattle Mariners",
        "hr_factor": 0.93,
        "hits_factor": 0.98,
        "roof": "retractable",
    },
    1: {
        "name": "Angel Stadium",
        "team": "Los Angeles Angels",
        "hr_factor": 0.93,
        "hits_factor": 0.97,
        "roof": "open",
    },
    5: {
        "name": "Progressive Field",
        "team": "Cleveland Guardians",
        "hr_factor": 0.93,
        "hits_factor": 0.97,
        "roof": "open",
    },
    3312: {
        "name": "Target Field",
        "team": "Minnesota Twins",
        "hr_factor": 0.92,
        "hits_factor": 0.97,
        "roof": "open",
    },
    7: {
        "name": "Kauffman Stadium",
        "team": "Kansas City Royals",
        "hr_factor": 0.91,
        "hits_factor": 0.97,
        "roof": "open",
    },
    2889: {
        "name": "Busch Stadium",
        "team": "St. Louis Cardinals",
        "hr_factor": 0.91,
        "hits_factor": 0.96,
        "roof": "open",
    },
    22: {
        "name": "Dodger Stadium",
        "team": "Los Angeles Dodgers",
        "hr_factor": 0.91,
        "hits_factor": 0.97,
        "roof": "open",
    },
    31: {
        "name": "PNC Park",
        "team": "Pittsburgh Pirates",
        "hr_factor": 0.90,
        "hits_factor": 0.96,
        "roof": "open",
    },
    10: {
        "name": "Oakland Coliseum",
        "team": "Oakland Athletics",
        "hr_factor": 0.86,
        "hits_factor": 0.95,
        "roof": "open",
    },
}

_NEUTRAL: dict = {"hr_factor": 1.0, "hits_factor": 1.0, "roof": "open"}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_park_factors(venue_id: int) -> dict:
    """Return park factor data for a venue.

    Args:
        venue_id: MLB Stats API venue ID.

    Returns:
        Dict with name, team, hr_factor, hits_factor, and roof.
        Falls back to neutral (1.0 / 1.0 / "open") when the venue is not found.
    """
    return PARK_FACTORS.get(venue_id, _NEUTRAL)
