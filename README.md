# MLB Daily Dash

A Streamlit dashboard for analyzing today's MLB slate. For each game it surfaces probable pitchers (with fatigue indicators), confirmed lineups with projected hits/total bases/home runs, game-time weather with wind direction relative to the outfield, home plate umpire zone tendencies, and park factor adjustments — all in one view.

## Setup

```bash
pip install -r requirements.txt
```

## Run locally

```bash
streamlit run mlb_daily_dash/app.py
```

Then open `http://localhost:8501` in your browser. Select a game from the sidebar to load its full dashboard.

## Project structure

```
mlb_daily_dash/
  app.py                  # Streamlit entry point
  data/
    fetcher.py            # MLB Stats API + weather API calls
    constants.py          # League averages, park coords, fatigue thresholds
  components/
    game_card.py          # Game selector sidebar cards
    lineup_table.py       # Batting order + projected stats table
    pitcher_card.py       # Pitcher profile with fatigue badge
    weather.py            # First-pitch weather card
    umpire.py             # Home plate umpire tendencies card
  utils/
    projections.py        # Per-batter game projection model
    park_factors.py       # Park factor lookups and adjustments
```
