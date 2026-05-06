from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..models.league import LeagueType


class LeagueCreate(BaseModel):
    name: str
    league_type: LeagueType = LeagueType.classic
    max_teams: int = 20
    season: str = "2024-25"


class LeagueOut(BaseModel):
    id: int
    name: str
    invite_code: str
    league_type: LeagueType
    max_teams: int
    season: str
    created_at: datetime

    model_config = {"from_attributes": True}


class LeagueStandingEntry(BaseModel):
    rank: int
    username: str
    team_name: str
    total_points: int
    gameweek_points: int = 0
