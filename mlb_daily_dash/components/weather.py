"""Weather fetching and rendering for MLB venue first-pitch conditions."""

import os

import requests
import streamlit as st

from mlb_daily_dash.data.constants import STADIUM_COORDS

_OWM_URL = "https://api.openweathermap.org/data/2.5/weather"
_TIMEOUT = 8

# Wind classification zones (degrees relative to CF direction, 45° each)
# relative = (wind_destination - OF_angle) % 360
# wind_destination = (wind_deg_from + 180) % 360
_WIND_ZONES: list[tuple[float, float, str, bool]] = [
    (0.0,    22.5,  "Blowing out to CF",   True),
    (22.5,   67.5,  "Blowing out to RF",   True),
    (67.5,   112.5, "Cross wind (L→R)",    False),
    (112.5,  157.5, "Blowing in from LF",  False),
    (157.5,  202.5, "Blowing in from CF",  False),
    (202.5,  247.5, "Blowing in from RF",  False),
    (247.5,  292.5, "Cross wind (R→L)",    False),
    (292.5,  337.5, "Blowing out to LF",   True),
    (337.5,  360.0, "Blowing out to CF",   True),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_api_key() -> str | None:
    """Return the OpenWeatherMap API key from env or Streamlit secrets."""
    key = os.environ.get("OPENWEATHER_API_KEY")
    if key:
        return key
    try:
        return st.secrets.get("OPENWEATHER_API_KEY")
    except Exception:
        return None


def _deg_to_compass(degrees: int) -> str:
    """Convert a wind bearing to a 16-point compass abbreviation."""
    labels = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    return labels[round(degrees / 22.5) % 16]


def _classify_wind(
    wind_deg: int, of_angle: float, wind_mph: float
) -> tuple[str, bool]:
    """Return (label, wind_is_out) for a given wind vs outfield orientation.

    Uses meteorological convention: wind_deg is the direction the wind is
    blowing FROM. Converts to destination bearing before comparing against
    the outfield_orientation_degrees bearing from home plate to CF.

    Args:
        wind_deg: Compass degrees the wind is blowing FROM (0 = from North).
        of_angle: Compass bearing from home plate toward CF (from STADIUM_COORDS).
        wind_mph: Wind speed in mph; returns "Calm" when below 3 mph.

    Returns:
        Tuple of (human-readable label, wind_is_out bool).
    """
    if wind_mph < 3:
        return "Calm", False

    wind_to = (wind_deg + 180) % 360
    relative = (wind_to - of_angle + 360) % 360

    for lo, hi, label, is_out in _WIND_ZONES:
        if lo <= relative < hi:
            return label, is_out

    # Should never reach here, but guard against float edge cases
    return "Blowing out to CF", True


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

@st.cache_data(ttl=1800)
def get_weather(venue_id: int) -> dict | None:
    """Fetch current weather conditions for an MLB venue from OpenWeatherMap.

    Looks up latitude, longitude, and outfield orientation from STADIUM_COORDS,
    then calls the OpenWeatherMap current-weather endpoint.

    Args:
        venue_id: MLB Stats API venue ID (must be present in STADIUM_COORDS).

    Returns:
        Dict with temp_f, humidity, pressure_hpa, wind_speed_mph, wind_deg,
        description, wind_direction_label, wind_is_out.
        Returns None on API failure, missing API key, or unknown venue.
    """
    venue = STADIUM_COORDS.get(venue_id)
    if not venue:
        return None

    api_key = _get_api_key()
    if not api_key:
        return None

    try:
        resp = requests.get(
            _OWM_URL,
            params={
                "lat": venue["lat"],
                "lon": venue["lon"],
                "appid": api_key,
                "units": "imperial",  # temp °F, wind speed mph
            },
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return None

    wind = data.get("wind", {})
    wind_deg: int = wind.get("deg", 0)
    wind_mph: float = wind.get("speed", 0.0)
    of_angle: float = venue.get("outfield_orientation_degrees", 0.0)

    wind_label, wind_is_out = _classify_wind(wind_deg, of_angle, wind_mph)

    return {
        "temp_f": round(data.get("main", {}).get("temp", 0.0), 1),
        "humidity": data.get("main", {}).get("humidity", 0),
        "pressure_hpa": data.get("main", {}).get("pressure", 0),
        "wind_speed_mph": round(wind_mph, 1),
        "wind_deg": wind_deg,
        "description": (data.get("weather") or [{}])[0].get("description", "").title(),
        "wind_direction_label": wind_label,
        "wind_is_out": wind_is_out,
    }


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_weather(venue_id: int) -> None:
    """Render a weather card for an MLB venue.

    Shows four st.metric tiles (temp, humidity, pressure, wind speed),
    a colour-coded wind direction label, and the weather description.

    Args:
        venue_id: MLB Stats API venue ID looked up in STADIUM_COORDS.
    """
    venue = STADIUM_COORDS.get(venue_id, {})
    stadium_name = venue.get("name", "Unknown Venue")

    st.subheader(f"First-Pitch Weather — {stadium_name}")

    weather = get_weather(venue_id)

    if weather is None:
        st.warning("Weather data unavailable.")
        return

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🌡️ Temp", f"{weather['temp_f']}°F")
    col2.metric("💧 Humidity", f"{weather['humidity']}%")
    col3.metric("🔵 Pressure", f"{weather['pressure_hpa']} hPa")
    col4.metric(
        "💨 Wind",
        f"{weather['wind_speed_mph']} mph",
        delta=_deg_to_compass(weather["wind_deg"]),
        delta_color="off",
    )

    # Colour-coded wind direction label
    label = weather["wind_direction_label"]
    if label == "Calm":
        st.info(f"🍃 {label}")
    elif weather["wind_is_out"]:
        st.success(f"✅ {label}")
    else:
        st.error(f"❌ {label}")

    st.caption(f"☁️ {weather['description']}")
