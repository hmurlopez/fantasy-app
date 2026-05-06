from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class GameweekStatus(str, enum.Enum):
    upcoming = "upcoming"
    active = "active"
    finished = "finished"


class Gameweek(Base):
    __tablename__ = "gameweeks"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)  # GW1, GW2, ...
    season = Column(String(10), default="2024-25")
    status = Column(Enum(GameweekStatus), default=GameweekStatus.upcoming)
    deadline = Column(DateTime(timezone=True), nullable=False)
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))

    player_stats = relationship("PlayerStats", back_populates="gameweek")
    picks = relationship("Pick", back_populates="gameweek")


class Pick(Base):
    """Snapshot of a team's lineup for a specific gameweek."""
    __tablename__ = "picks"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    gameweek_id = Column(Integer, ForeignKey("gameweeks.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    is_starter = Column(Boolean, default=True)
    # Captain doubles points; vice-captain doubles if captain doesn't play
    is_captain = Column(Boolean, default=False)
    is_vice_captain = Column(Boolean, default=False)
    # Points earned by this pick this gameweek
    points_earned = Column(Integer, default=0)

    team = relationship("Team", back_populates="picks")
    gameweek = relationship("Gameweek", back_populates="picks")
    player = relationship("Player", back_populates="picks")
