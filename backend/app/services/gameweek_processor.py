"""
Gameweek Processor
==================
Ties together the scraper and scoring engine.
Called by the `scripts/update_scores.py` cron job after each match round.
"""

import logging
from sqlalchemy.orm import Session
from ..models.player import Player, PlayerStats
from ..models.gameweek import Gameweek, GameweekStatus, Pick
from ..models.team import Team
from ..models.league import LeagueMembership
from .scoring import calculate_points
from .scraper import FBRefScraper

logger = logging.getLogger(__name__)


def process_gameweek(gw_id: int, db: Session) -> None:
    gw = db.query(Gameweek).filter(Gameweek.id == gw_id).first()
    if not gw:
        raise ValueError(f"Gameweek {gw_id} not found")

    logger.info("Processing GW%d", gw.number)
    scraper = FBRefScraper()

    # 1. Fetch and store player stats
    raw_stats = scraper.fetch_squad_stats()
    _upsert_player_stats(raw_stats, gw, db)

    # 2. Calculate fantasy points for each pick
    _score_all_picks(gw, db)

    # 3. Roll up team totals
    _update_team_totals(gw, db)

    # 4. Update league standings
    _update_league_standings(db)

    # 5. Reset weekly transfer counters and roll free transfer
    _reset_transfer_counts(db)

    gw.status = GameweekStatus.finished
    db.commit()
    logger.info("GW%d complete", gw.number)


def _upsert_player_stats(raw: list[dict], gw: Gameweek, db: Session) -> None:
    for row in raw:
        player = db.query(Player).filter(Player.name == row["name"]).first()
        if not player:
            continue
        stats = db.query(PlayerStats).filter(
            PlayerStats.player_id == player.id,
            PlayerStats.gameweek_id == gw.id,
        ).first()
        if not stats:
            stats = PlayerStats(player_id=player.id, gameweek_id=gw.id)
            db.add(stats)
        stats.minutes_played = row.get("minutes", 0)
        stats.goals = row.get("goals", 0)
        stats.assists = row.get("assists", 0)
        # Fields like clean_sheet / goals_conceded need a separate match-level
        # fetch; FBRef season tables don't include them directly.
        pts = calculate_points(stats, player.position)
        stats.fantasy_points = pts
        player.total_points += pts
    db.flush()


def _score_all_picks(gw: Gameweek, db: Session) -> None:
    picks = db.query(Pick).filter(Pick.gameweek_id == gw.id).all()
    for pick in picks:
        stats = db.query(PlayerStats).filter(
            PlayerStats.player_id == pick.player_id,
            PlayerStats.gameweek_id == gw.id,
        ).first()
        raw_pts = stats.fantasy_points if stats else 0
        # Captain gets double
        pick.points_earned = raw_pts * (2 if pick.is_captain else 1)
    db.flush()


def _update_team_totals(gw: Gameweek, db: Session) -> None:
    teams = db.query(Team).all()
    for team in teams:
        gw_pts = (
            db.query(Pick)
            .filter(Pick.team_id == team.id, Pick.gameweek_id == gw.id, Pick.is_starter == True)
            .all()
        )
        total = sum(p.points_earned for p in gw_pts)
        transfer_cost = max(0, (team.transfers_this_week - team.free_transfers)) * 4
        team.total_points += total - transfer_cost
    db.flush()


def _update_league_standings(db: Session) -> None:
    memberships = db.query(LeagueMembership).all()
    for m in memberships:
        if m.team:
            m.total_points = m.team.total_points
    db.flush()


def _reset_transfer_counts(db: Session) -> None:
    teams = db.query(Team).all()
    for team in teams:
        # Unused free transfer rolls over (max 2 banked)
        unused = max(0, team.free_transfers - team.transfers_this_week)
        team.free_transfers = min(2, 1 + unused)
        team.transfers_this_week = 0
    db.flush()
