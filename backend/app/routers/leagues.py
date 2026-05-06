import random
import string
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.league import League, LeagueMembership
from ..models.team import Team
from ..models.user import User
from ..schemas.league import LeagueCreate, LeagueOut, LeagueStandingEntry
from .deps import get_current_user

router = APIRouter(prefix="/leagues", tags=["leagues"])


def _make_invite_code(db: Session) -> str:
    while True:
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if not db.query(League).filter(League.invite_code == code).first():
            return code


@router.post("/", response_model=LeagueOut, status_code=201)
def create_league(
    body: LeagueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    league = League(
        name=body.name,
        invite_code=_make_invite_code(db),
        league_type=body.league_type,
        max_teams=body.max_teams,
        season=body.season,
        created_by=current_user.id,
    )
    db.add(league)
    db.flush()
    # Creator auto-joins
    team = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == body.season
    ).first()
    membership = LeagueMembership(
        league_id=league.id, user_id=current_user.id, team_id=team.id if team else None
    )
    db.add(membership)
    db.commit()
    db.refresh(league)
    return league


@router.post("/join/{invite_code}", response_model=LeagueOut)
def join_league(
    invite_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    league = db.query(League).filter(League.invite_code == invite_code.upper()).first()
    if not league:
        raise HTTPException(404, "League not found — check the invite code")
    if not league.is_active:
        raise HTTPException(400, "This league is no longer active")
    already = db.query(LeagueMembership).filter(
        LeagueMembership.league_id == league.id,
        LeagueMembership.user_id == current_user.id,
    ).first()
    if already:
        raise HTTPException(400, "You are already in this league")
    count = db.query(LeagueMembership).filter(LeagueMembership.league_id == league.id).count()
    if count >= league.max_teams:
        raise HTTPException(400, "League is full")
    team = db.query(Team).filter(
        Team.owner_id == current_user.id, Team.season == league.season
    ).first()
    membership = LeagueMembership(
        league_id=league.id, user_id=current_user.id, team_id=team.id if team else None
    )
    db.add(membership)
    db.commit()
    return league


@router.get("/", response_model=List[LeagueOut])
def my_leagues(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memberships = (
        db.query(LeagueMembership)
        .filter(LeagueMembership.user_id == current_user.id)
        .all()
    )
    return [m.league for m in memberships]


@router.get("/{league_id}/standings", response_model=List[LeagueStandingEntry])
def league_standings(
    league_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    memberships = (
        db.query(LeagueMembership)
        .filter(LeagueMembership.league_id == league_id)
        .order_by(LeagueMembership.total_points.desc())
        .all()
    )
    standings = []
    for rank, m in enumerate(memberships, start=1):
        standings.append(
            LeagueStandingEntry(
                rank=rank,
                username=m.user.username,
                team_name=m.team.name if m.team else "No team",
                total_points=m.total_points,
            )
        )
    return standings
