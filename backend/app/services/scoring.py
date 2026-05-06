"""
Fantasy Soccer Scoring Engine
==============================
Points are calculated from raw stats stored in PlayerStats.
Adjust the SCORING_RULES dict to customise your league's point system.
"""

from ..models.player import PlayerStats

# ---------------------------------------------------------------------------
# Configurable point rules
# ---------------------------------------------------------------------------

SCORING_RULES = {
    # Minutes played
    "minutes_1_to_59": 1,
    "minutes_60_plus": 2,

    # Goals (by position)
    "goal_gk": 6,
    "goal_def": 6,
    "goal_mid": 5,
    "goal_fwd": 4,

    # Assists (all positions)
    "assist": 3,

    # Big chances created (all positions): 1 pt each
    "big_chance_created": 1,

    # Balls into the box (all positions): 0.5 pts each
    "ball_into_box": 0.5,

    # Penalties won (all positions): 2 pts each
    "penalty_won": 2,

    # Penalties committed (all positions): -2 pts each
    "penalty_committed": -2,

    # Penalties saved (all positions): 3 pts each
    "penalty_save": 3,

    # Saves (all positions): 0.5 pts each
    "save": 0.5,

    # Effective clearances (all positions): 0.5 pts each
    "effective_clearance": 0.5,

    # Penalties missed (all positions): -2 pts each
    "penalty_miss": -2,

    # Own goals (all positions): -2 pts each
    "own_goal": -2,

    # Goals against tiers indexed by goals_conceded count.
    # The last entry covers that value and all higher values.
    # GK/DEF: clean sheet=+3, 1 conceded=0, 2+=−1
    "goals_against_gk":  [3, 0, -1],
    "goals_against_def": [3, 0, -1],
    # MID: clean sheet=+2, 1=0, 2=−1, 3=−1, 4+=−2
    "goals_against_mid": [2, 0, -1, -1, -2],
    # FWD: clean sheet=+1, 1=0, 2=−1, 3=−1, 4+=−2
    "goals_against_fwd": [1, 0, -1, -1, -2],

    # Cards
    "yellow_card": -1,
    "second_yellow_card": -2,
    "red_card": -2,

    # Goal attempts (all positions): 0.5 pts each
    "goal_attempt": 0.5,

    # Effective dribbles (all positions): 0.5 pts each
    "effective_dribble": 0.5,

    # Recoveries (all positions): 0.2 pts each
    "recovery": 0.2,

    # Lost balls (all positions): -0.1 pts each
    "lost_ball": -0.1,

    # Transfer deduction (applied separately at GW level)
    "extra_transfer": -4,
}


def calculate_points(stats: PlayerStats, position: str) -> float:
    """Return fantasy points for one player's stats in a single gameweek."""
    pts = 0.0
    pos = position.upper()

    # Minutes played
    if stats.minutes_played >= 60:
        pts += SCORING_RULES["minutes_60_plus"]
    elif stats.minutes_played >= 1:
        pts += SCORING_RULES["minutes_1_to_59"]
    else:
        return 0.0  # Didn't play — no points

    # Goals
    goal_key = f"goal_{pos.lower()}"
    pts += stats.goals * SCORING_RULES.get(goal_key, SCORING_RULES["goal_fwd"])

    # Assists
    pts += stats.assists * SCORING_RULES["assist"]

    # Big chances created
    pts += stats.big_chances_created * SCORING_RULES["big_chance_created"]

    # Balls into the box
    pts += stats.balls_into_box * SCORING_RULES["ball_into_box"]

    # Penalties won
    pts += stats.penalties_won * SCORING_RULES["penalty_won"]

    # Penalties committed
    pts += stats.penalties_committed * SCORING_RULES["penalty_committed"]

    # Penalties saved
    pts += stats.penalties_saved * SCORING_RULES["penalty_save"]

    # Saves
    pts += stats.saves * SCORING_RULES["save"]

    # Effective clearances
    pts += stats.effective_clearances * SCORING_RULES["effective_clearance"]

    # Penalties missed
    pts += stats.penalties_missed * SCORING_RULES["penalty_miss"]

    # Own goals
    pts += stats.own_goals * SCORING_RULES["own_goal"]

    # Goals against (tiered): last tier covers all higher counts
    ga_key = f"goals_against_{pos.lower()}"
    ga_tiers = SCORING_RULES.get(ga_key, SCORING_RULES["goals_against_fwd"])
    tier_idx = min(stats.goals_conceded, len(ga_tiers) - 1)
    pts += ga_tiers[tier_idx]

    # Cards
    pts += stats.yellow_cards * SCORING_RULES["yellow_card"]
    pts += stats.second_yellow_cards * SCORING_RULES["second_yellow_card"]
    pts += stats.red_cards * SCORING_RULES["red_card"]

    # Goal attempts
    pts += stats.goal_attempts * SCORING_RULES["goal_attempt"]

    # Effective dribbles
    pts += stats.effective_dribbles * SCORING_RULES["effective_dribble"]

    # Recoveries
    pts += stats.recoveries * SCORING_RULES["recovery"]

    # Lost balls
    pts += stats.lost_balls * SCORING_RULES["lost_ball"]

    return pts


def apply_captain_multiplier(pts: float, is_captain: bool) -> float:
    return pts * 2 if is_captain else pts
