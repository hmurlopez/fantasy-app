#!/usr/bin/env python3
"""
Create gameweek records for a season.

Usage:
    cd backend
    python ../scripts/create_gameweeks.py --season 2024-25 --total 38 \
        --start 2024-08-16

Deadlines are set to 90 minutes before each gameweek's first kick-off.
You'll want to adjust the actual dates to match the real fixture list.
"""

import argparse
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal, engine, Base
from app.models.gameweek import Gameweek, GameweekStatus


def main(season: str, total: int, start_date: datetime) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        created = 0
        for i in range(1, total + 1):
            exists = db.query(Gameweek).filter(
                Gameweek.number == i, Gameweek.season == season
            ).first()
            if exists:
                continue
            gw_start = start_date + timedelta(weeks=i - 1)
            gw = Gameweek(
                number=i,
                season=season,
                status=GameweekStatus.upcoming,
                deadline=gw_start - timedelta(minutes=90),
                start_date=gw_start,
                end_date=gw_start + timedelta(days=3),
            )
            db.add(gw)
            created += 1
        db.commit()
        print(f"Created {created} gameweeks for {season}.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--season", default="2024-25")
    parser.add_argument("--total", type=int, default=38)
    parser.add_argument("--start", default="2024-08-16", help="YYYY-MM-DD of GW1 kick-off")
    args = parser.parse_args()
    main(args.season, args.total, datetime.fromisoformat(args.start))
