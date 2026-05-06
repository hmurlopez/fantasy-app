#!/usr/bin/env python3
"""
Gameweek Score Updater
======================
Run this after a gameweek's matches are complete to:
  1. Fetch player stats from FBRef
  2. Calculate fantasy points
  3. Update team totals and league standings
  4. Roll free transfers

Usage:
    cd backend
    python ../scripts/update_scores.py --gw 1

Typically scheduled via cron or a task queue (e.g. Celery) after the last
match of each gameweek finishes.
"""

import argparse
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal, engine, Base
from app.services.gameweek_processor import process_gameweek


def main(gw_number: int) -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.models.gameweek import Gameweek
        gw = db.query(Gameweek).filter(Gameweek.number == gw_number).first()
        if not gw:
            logging.error("Gameweek %d not found in DB. Seed gameweeks first.", gw_number)
            sys.exit(1)
        process_gameweek(gw.id, db)
        logging.info("Gameweek %d processed successfully.", gw_number)
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update fantasy scores for a gameweek")
    parser.add_argument("--gw", type=int, required=True, help="Gameweek number to process")
    args = parser.parse_args()
    main(args.gw)
