# Fantasy Soccer

A full-stack fantasy soccer app powered by real stats from FBRef.

## How It Works

1. **Register / Log in** — create your account.
2. **Create a team** — name your squad; you get a £100m budget.
3. **Build your squad** — browse the Transfer Market, pick 15 players
   (2 GK · 5 DEF · 5 MID · 3 FWD) within budget.
4. **Set your lineup** — choose your starting XI and captain each week before the gameweek deadline.
5. **Compete in leagues** — create a private league and share the invite code with friends,
   or join one with someone else's code.
6. **Scores update automatically** after each gameweek using FBRef data.

## Scoring Rules

| Event | Points |
|---|---|
| Playing 1–59 min | +1 |
| Playing 60+ min | +2 |
| GK / DEF goal | +10 / +6 |
| MID goal | +5 |
| FWD goal | +4 |
| Assist (all) | +3 |
| GK clean sheet | +6 |
| DEF clean sheet | +4 |
| MID clean sheet | +1 |
| Every 3 GK saves | +1 |
| Penalty save | +5 |
| GK/DEF — per 2 goals conceded | −1 |
| Yellow card | −1 |
| Red card | −3 |
| Own goal | −2 |
| Penalty miss | −2 |
| Each extra transfer | −4 |
| Captain | ×2 |

## Project Structure

```
fantasy-app/
├── backend/            # FastAPI + SQLAlchemy API
│   ├── app/
│   │   ├── core/       # Config, JWT security
│   │   ├── models/     # SQLAlchemy ORM models
│   │   ├── routers/    # API endpoints
│   │   ├── schemas/    # Pydantic request/response models
│   │   ├── services/   # Scoring engine + FBRef scraper
│   │   └── main.py     # App entry point
│   └── requirements.txt
├── frontend/           # Vanilla HTML/CSS/JS single-page app
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── api.js      # API client
│       └── app.js      # UI logic
└── scripts/
    ├── create_gameweeks.py   # Seed gameweek schedule
    ├── seed_players.py       # Populate players from FBRef
    └── update_scores.py      # Process a finished gameweek
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit SECRET_KEY
uvicorn app.main:app --reload
# API docs at http://localhost:8000/docs
```

### Seed data

```bash
# Create gameweeks for the season
python scripts/create_gameweeks.py --season 2024-25 --total 38 --start 2024-08-16

# Pull players from FBRef (requires internet)
python scripts/seed_players.py --league premier_league --season 2024-25
```

### Frontend

Open `frontend/index.html` in your browser (or serve with any static server):

```bash
cd frontend && python -m http.server 3000
# http://localhost:3000
```

### Update scores after a gameweek

```bash
python scripts/update_scores.py --gw 1
```

## League Formats

- **Classic** — all-season cumulative points, same as FPL.
- **Head-to-Head** — weekly matchup against one opponent; win/draw/loss points.

## Data Source

Stats are scraped from [FBRef](https://fbref.com) (Sports Reference).
The scraper respects FBRef's requested 3-second delay between requests.
Install `soccerdata` for a more robust, cached scraping experience:

```bash
pip install soccerdata
```
