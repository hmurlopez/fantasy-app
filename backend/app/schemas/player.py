from pydantic import BaseModel
from typing import Optional


class PlayerOut(BaseModel):
    id: int
    fbref_id: Optional[str]
    name: str
    position: str
    club: Optional[str]
    nationality: Optional[str]
    price: float
    total_points: int
    points_per_game: float
    ownership_pct: float

    model_config = {"from_attributes": True}


class PlayerStatsOut(BaseModel):
    gameweek_id: int
    minutes_played: int
    goals: int
    assists: int
    clean_sheet: int
    goals_conceded: int
    saves: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    own_goals: int
    fantasy_points: int

    model_config = {"from_attributes": True}
