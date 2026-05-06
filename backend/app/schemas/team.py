from pydantic import BaseModel
from typing import Optional, List
from .player import PlayerOut


class TeamCreate(BaseModel):
    name: str


class TeamOut(BaseModel):
    id: int
    name: str
    season: str
    budget_remaining: float
    total_points: int
    free_transfers: int

    model_config = {"from_attributes": True}


class TransferRequest(BaseModel):
    player_out_id: int
    player_in_id: int


class SetLineupRequest(BaseModel):
    # List of player IDs in the starting XI (exactly 11)
    starters: List[int]
    captain_id: int
    vice_captain_id: int
