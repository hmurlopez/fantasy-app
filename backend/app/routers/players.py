from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from ..database import get_db
from ..models.player import Player, PlayerStats
from ..schemas.player import PlayerOut, PlayerStatsOut

router = APIRouter(prefix="/players", tags=["players"])


@router.get("/", response_model=List[PlayerOut])
def list_players(
    position: Optional[str] = Query(None, description="GK, DEF, MID, FWD"),
    club: Optional[str] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    q = db.query(Player)
    if position:
        q = q.filter(Player.position == position.upper())
    if club:
        q = q.filter(Player.club.ilike(f"%{club}%"))
    if max_price is not None:
        q = q.filter(Player.price <= max_price)
    if search:
        q = q.filter(Player.name.ilike(f"%{search}%"))
    q = q.order_by(Player.total_points.desc())
    return q.offset(skip).limit(limit).all()


@router.get("/{player_id}", response_model=PlayerOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(404, "Player not found")
    return player


@router.get("/{player_id}/stats", response_model=List[PlayerStatsOut])
def get_player_stats(player_id: int, db: Session = Depends(get_db)):
    return (
        db.query(PlayerStats)
        .filter(PlayerStats.player_id == player_id)
        .order_by(PlayerStats.gameweek_id.desc())
        .all()
    )
