from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.team import Team, TeamPlayer
from ..models.player import Player
from ..models.user import User
from ..schemas.team import TeamCreate, TeamOut, TransferRequest, SetLineupRequest
from ..core.config import get_settings
from .deps import get_current_user

router = APIRouter(prefix="/teams", tags=["teams"])
settings = get_settings()


@router.post("/", response_model=TeamOut, status_code=201)
def create_team(
    body: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == "2024-25"
    ).first()
    if existing:
        raise HTTPException(400, "You already have a team for this season")
    team = Team(
        name=body.name,
        owner_id=current_user.id,
        budget_remaining=settings.squad_budget,
    )
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("/me", response_model=TeamOut)
def my_team(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == "2024-25"
    ).first()
    if not team:
        raise HTTPException(404, "No team found — create one first")
    return team


@router.get("/me/squad")
def my_squad(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == "2024-25"
    ).first()
    if not team:
        raise HTTPException(404, "No team found")
    squad = []
    for tp in sorted(team.players, key=lambda x: (not x.is_starter, x.position_order)):
        p = tp.player
        squad.append({
            "player_id": p.id,
            "name": p.name,
            "position": p.position,
            "club": p.club,
            "price": tp.purchase_price,
            "is_starter": tp.is_starter,
            "total_points": p.total_points,
        })
    return {"team": TeamOut.model_validate(team), "squad": squad}


@router.post("/me/transfer")
def make_transfer(
    body: TransferRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == "2024-25"
    ).first()
    if not team:
        raise HTTPException(404, "No team found")

    out_tp = db.query(TeamPlayer).filter(
        TeamPlayer.team_id == team.id,
        TeamPlayer.player_id == body.player_out_id,
    ).first()
    if not out_tp:
        raise HTTPException(400, "Player to remove is not in your squad")

    player_in = db.query(Player).filter(Player.id == body.player_in_id).first()
    if not player_in:
        raise HTTPException(404, "Incoming player not found")

    already_in = db.query(TeamPlayer).filter(
        TeamPlayer.team_id == team.id,
        TeamPlayer.player_id == body.player_in_id,
    ).first()
    if already_in:
        raise HTTPException(400, "That player is already in your squad")

    cost = player_in.price - out_tp.purchase_price
    if team.budget_remaining < cost:
        raise HTTPException(400, f"Insufficient budget. Need {cost:.1f}M more")

    team.budget_remaining -= cost
    team.transfers_this_week += 1

    # Each extra transfer (beyond free) costs 4 points deducted at GW scoring
    db.delete(out_tp)
    db.flush()
    new_tp = TeamPlayer(
        team_id=team.id,
        player_id=player_in.id,
        purchase_price=player_in.price,
        is_starter=out_tp.is_starter,
        position_order=out_tp.position_order,
    )
    db.add(new_tp)
    db.commit()
    return {"message": "Transfer complete", "budget_remaining": team.budget_remaining}


@router.post("/me/lineup")
def set_lineup(
    body: SetLineupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    team = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == "2024-25"
    ).first()
    if not team:
        raise HTTPException(404, "No team found")
    if len(body.starters) != settings.starting_xi:
        raise HTTPException(400, f"Starting XI must have exactly {settings.starting_xi} players")
    if body.captain_id not in body.starters:
        raise HTTPException(400, "Captain must be in the starting XI")
    if body.vice_captain_id not in body.starters:
        raise HTTPException(400, "Vice-captain must be in the starting XI")

    squad_ids = {tp.player_id for tp in team.players}
    for pid in body.starters:
        if pid not in squad_ids:
            raise HTTPException(400, f"Player {pid} is not in your squad")

    for idx, tp in enumerate(team.players):
        tp.is_starter = tp.player_id in body.starters
        tp.position_order = (
            body.starters.index(tp.player_id) + 1 if tp.is_starter else idx + 20
        )
    db.commit()
    return {"message": "Lineup updated"}
