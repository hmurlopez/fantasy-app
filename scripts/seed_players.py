#!/usr/bin/env python3
"""
Seed the database with player data fetched from FBRef.

Usage:
    cd backend
    python ../scripts/seed_players.py --league premier_league --season 2024-25

This script is meant to be run once at the start of a season (or to refresh
the player pool). It upserts records so it's safe to re-run.
"""

import argparse
import sys
import os

# Allow importing from backend/app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal, engine, Base
from app.models.player import Player
from app.services.scraper import FBRefScraper, SUPPORTED_LEAGUES

# Price heuristics (rough starting values; you can refine these)
PRICE_MAP = {
    "GK":  5.0,
    "DEF": 5.5,
    "MID": 6.0,
    "FWD": 7.0,
}


def seed(league_key: str, season: str) -> None:
    Base.metadata.create_all(bind=engine)
    league = SUPPORTED_LEAGUES.get(league_key, "ENG-Premier League")
    print(f"Fetching player data for {league} {season}…")

    scraper = FBRefScraper()
    players_raw = scraper.fetch_squad_stats(league=league, season=season)

    if not players_raw:
        print("No player data returned — check your internet connection or FBRef availability.")
        sys.exit(1)

    db = SessionLocal()
    try:
        added = updated = 0
        for row in players_raw:
            existing = (
                db.query(Player).filter(Player.fbref_id == row["fbref_id"]).first()
                if row.get("fbref_id")
                else db.query(Player).filter(Player.name == row["name"]).first()
            )
            if existing:
                existing.club = row.get("club", existing.club)
                existing.nationality = row.get("nationality", existing.nationality)
                updated += 1
            else:
                pos = row.get("position", "MID")
                p = Player(
                    fbref_id=row.get("fbref_id") or None,
                    name=row["name"],
                    position=pos,
                    club=row.get("club"),
                    nationality=row.get("nationality"),
                    price=PRICE_MAP.get(pos, 5.5),
                )
                db.add(p)
                added += 1

        db.commit()
        print(f"Done. Added {added} players, updated {updated}.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed fantasy soccer player DB from FBRef")
    parser.add_argument("--league", default="premier_league", choices=list(SUPPORTED_LEAGUES.keys()))
    parser.add_argument("--season", default="2024-25")
    args = parser.parse_args()
    seed(args.league, args.season)
