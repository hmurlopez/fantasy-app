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
    second_yellow_cards: int
    red_cards: int
    own_goals: int
    big_chances_created: int
    balls_into_box: int
    penalties_won: int
    penalties_committed: int
    effective_clearances: int
    goal_attempts: int
    effective_dribbles: int
    recoveries: int
    lost_balls: int
    fantasy_points: float

    model_config = {"from_attributes": True}
