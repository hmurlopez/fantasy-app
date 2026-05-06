"""
Fantasy Soccer Scoring Engine
==============================
Points are calculated from raw FBRef stats stored in PlayerStats.
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
    "goal_gk": 10,
    "goal_def": 6,
    "goal_mid": 5,
    "goal_fwd": 4,

    # Assists (all positions)
    "assist": 3,

    # Clean sheets (full match, by position)
    "clean_sheet_gk": 6,
    "clean_sheet_def": 4,
    "clean_sheet_mid": 1,
    "clean_sheet_fwd": 0,

    # Goals conceded (GK + DEF only): -1 per every 2 goals let in
    "goals_conceded_per_2_gk": -1,
    "goals_conceded_per_2_def": -1,

    # GK-specific
    "saves_per_3": 1,        # +1 for every 3 saves
    "penalty_save": 5,

    # Negative events (all positions)
    "yellow_card": -1,
    "red_card": -3,
    "own_goal": -2,
    "penalty_miss": -2,

    # Transfer deduction (applied separately at GW level)
    "extra_transfer": -4,
}


def calculate_points(stats: PlayerStats, position: str) -> int:
    """Return fantasy points for one player's stats in a single gameweek."""
    pts = 0
    pos = position.upper()

    # Minutes played
    if stats.minutes_played >= 60:
        pts += SCORING_RULES["minutes_60_plus"]
    elif stats.minutes_played >= 1:
        pts += SCORING_RULES["minutes_1_to_59"]
    else:
        return 0  # Didn't play — no points

    # Goals
    goal_key = f"goal_{pos.lower()}"
    pts += stats.goals * SCORING_RULES.get(goal_key, SCORING_RULES["goal_fwd"])

    # Assists
    pts += stats.assists * SCORING_RULES["assist"]

    # Clean sheet (only awarded if player played 60+ minutes)
    if stats.clean_sheet and stats.minutes_played >= 60:
        cs_key = f"clean_sheet_{pos.lower()}"
        pts += SCORING_RULES.get(cs_key, 0)

    # Goals conceded penalty (GK and DEF only)
    if pos in ("GK", "DEF"):
        conceded_key = f"goals_conceded_per_2_{pos.lower()}"
        pts += (stats.goals_conceded // 2) * SCORING_RULES.get(conceded_key, 0)

    # GK saves bonus
    if pos == "GK":
        pts += (stats.saves // 3) * SCORING_RULES["saves_per_3"]
        pts += stats.penalties_saved * SCORING_RULES["penalty_save"]

    # Negative events
    pts += stats.yellow_cards * SCORING_RULES["yellow_card"]
    pts += stats.red_cards * SCORING_RULES["red_card"]
    pts += stats.own_goals * SCORING_RULES["own_goal"]
    pts += stats.penalties_missed * SCORING_RULES["penalty_miss"]

    return pts


def apply_captain_multiplier(pts: int, is_captain: bool) -> int:
    return pts * 2 if is_captain else pts
