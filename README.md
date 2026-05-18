# MLB Daily Dash

A Streamlit dashboard for analyzing today's MLB slate. For each game it surfaces probable pitchers (with fatigue indicators), batting lineups with projected hits/total bases/home runs, game-time weather with wind direction relative to the outfield, home plate umpire zone tendencies, and park factor adjustments — all in one view.

## Requirements

- Python 3.11+
- OpenWeatherMap API key (free tier works fine — sign up at openweathermap.org)

## Setup

**1. Install dependencies**

```bash
pip install -r requirements.txt
```

**2. Set your OpenWeatherMap API key**

Either export it as an environment variable:

```bash
export OPENWEATHER_API_KEY=your_key_here   # macOS/Linux
set OPENWEATHER_API_KEY=your_key_here      # Windows cmd
$env:OPENWEATHER_API_KEY="your_key_here"   # Windows PowerShell
```

Or create `.streamlit/secrets.toml` (copy the example):

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# then edit .streamlit/secrets.toml and replace your_key_here
```

## Run locally

```bash
streamlit run app.py
```

Then open `http://localhost:8501` in your browser.

On macOS/Linux you can also use the convenience script:

```bash
bash run.sh
```

## Data sources

| Source | What it provides | Auth required |
|---|---|---|
| MLB Stats API | Schedule, lineups, splits, injuries | None (free) |
| Umpire Scorecards API | HP umpire zone stats | None (free) |
| OpenWeatherMap | First-pitch weather | Free API key |

All data is cached: schedule/umpire assignments for 1 hour, weather for 30 minutes, player stats for 1 hour.

## Project structure

```
app.py                        # Top-level entry point (streamlit run app.py)
mlb_daily_dash/
  app.py                      # Main Streamlit application
  data/
    fetcher.py                # MLB Stats API + Umpire Scorecards calls
    constants.py              # League averages, stadium coords, fatigue thresholds
  components/
    lineup_table.py           # Batting order + projected stats table
    pitcher_card.py           # Pitcher profile with fatigue flags and platoon splits
    weather.py                # First-pitch weather card
    umpire.py                 # Home plate umpire tendencies card
  utils/
    projections.py            # Per-batter game projection model
    park_factors.py           # Hardcoded park factor lookup for all 30 venues
```

## Projection model

For each batter the model computes **xH**, **xTB**, and **xHR** for the game:

```
projected_rate = blend(split_rate, season_rate, credibility_pa=50)
              × pitcher_suppression(pitcher_splits, batter_hand)
              × park_factor
              × fatigue_multiplier(days_rest, last_pitch_count)

xStat = projected_rate × expected_PA(lineup_slot)
```

Credibility weighting (`w = pa / (pa + 50)`) shrinks volatile small-sample splits toward the season baseline. Park factors and fatigue adjustments are multiplicative.
