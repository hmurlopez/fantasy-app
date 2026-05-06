from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Team(Base):
    """A user's fantasy squad (one per user per season)."""
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    season = Column(String(10), default="2024-25")
    # Remaining transfer budget
    budget_remaining = Column(Float, default=100.0)
    total_points = Column(Integer, default=0)
    # Transfers used this gameweek (>1 free transfer costs -4 pts each)
    transfers_this_week = Column(Integer, default=0)
    free_transfers = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="teams")
    players = relationship("TeamPlayer", back_populates="team", cascade="all, delete-orphan")
    picks = relationship("Pick", back_populates="team")


class TeamPlayer(Base):
    """15-man squad roster for a team."""
    __tablename__ = "team_players"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    # Purchase price locked at time of transfer
    purchase_price = Column(Float, nullable=False)
    # True = in starting XI, False = on bench
    is_starter = Column(Boolean, default=False)
    # 1-11 (starting order / bench order 12-15)
    position_order = Column(Integer, default=0)
    added_at = Column(DateTime(timezone=True), server_default=func.now())

    team = relationship("Team", back_populates="players")
    player = relationship("Player")
