"""Streamlit component that renders game-time weather conditions."""

import streamlit as st


def render_weather_card(weather: dict, outfield_orientation_degrees: float) -> None:
    """Render a weather summary card for a venue at first-pitch time.

    Displays temperature, wind speed/direction, humidity, and a descriptive
    label for how wind aligns with the outfield (e.g. "blowing out to CF").

    Args:
        weather: Weather dict from fetcher.get_weather().
        outfield_orientation_degrees: Compass bearing from home plate to center
            field, used to compute relative wind direction.
    """
    pass


def classify_wind(
    wind_mph: float,
    wind_direction_degrees: float,
    outfield_orientation_degrees: float,
) -> str:
    """Classify wind relative to the outfield as a human-readable label.

    Args:
        wind_mph: Wind speed in miles per hour.
        wind_direction_degrees: Compass direction the wind is blowing FROM.
        outfield_orientation_degrees: Compass bearing from home plate to center field.

    Returns:
        A label such as "Blowing out to CF", "Blowing in from LF",
        "Cross wind (L→R)", "Cross wind (R→L)", or "Calm".
    """
    pass
