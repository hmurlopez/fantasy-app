from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.gameweek import Gameweek, GameweekStatus, Pick
from ..models.team import Team
from ..models.user import User
from .deps import get_current_user

router = APIRouter(prefix="/gameweeks", tags=["gameweeks"])


@router.get("/")
def list_gameweeks(db: Session = Depends(get_db)):
    return db.query(Gameweek).order_by(Gameweek.number).all()


@router.get("/current")
def current_gameweek(db: Session = Depends(get_db)):
    gw = (
        db.query(Gameweek)
        .filter(Gameweek.status == GameweekStatus.active)
        .first()
    )
    if not gw:
        gw = (
            db.query(Gameweek)
            .filter(Gameweek.status == GameweekStatus.upcoming)
            .order_by(Gameweek.number)
            .first()
        )
    if not gw:
        raise HTTPException(404, "No active or upcoming gameweek")
    return gw


@router.get("/{gw_id}/my-picks")
def my_picks(
    gw_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == "2024-25"
    ).first()
    if not team:
        raise HTTPException(404, "No team found")
    picks = db.query(Pick).filter(
        Pick.team_id == team.id,
        Pick.gameweek_id == gw_id,
    ).all()
    result = []
    for p in picks:
        result.append({
            "player_id": p.player_id,
            "name": p.player.name,
            "position": p.player.position,
            "is_starter": p.is_starter,
            "is_captain": p.is_captain,
            "is_vice_captain": p.is_vice_captain,
            "points_earned": p.points_earned,
        })
    return result


@router.get("/{gw_id}/points")
def gameweek_points(
    gw_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == "2024-25"
    ).first()
    if not team:
        raise HTTPException(404, "No team found")
    picks = db.query(Pick).filter(
        Pick.team_id == team.id,
        Pick.gameweek_id == gw_id,
        Pick.is_starter == True,
    ).all()
    total = sum(
        p.points_earned * (2 if p.is_captain else 1) for p in picks
    )
    transfer_cost = max(0, (team.transfers_this_week - team.free_transfers)) * 4
    return {
        "gameweek_id": gw_id,
        "gross_points": total,
        "transfer_deduction": transfer_cost,
        "net_points": total - transfer_cost,
    }
