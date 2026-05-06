from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    fbref_id = Column(String(20), unique=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    # GK, DEF, MID, FWD
    position = Column(String(3), nullable=False)
    club = Column(String(80))
    nationality = Column(String(50))
    # Price in millions
    price = Column(Float, default=5.0)
    # Total points across all gameweeks
    total_points = Column(Integer, default=0)
    # Points per game
    points_per_game = Column(Float, default=0.0)
    # How many managers own this player (%)
    ownership_pct = Column(Float, default=0.0)

    stats = relationship("PlayerStats", back_populates="player", cascade="all, delete-orphan")
    picks = relationship("Pick", back_populates="player")


class PlayerStats(Base):
    """Per-gameweek statistics fetched from FBRef."""
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    gameweek_id = Column(Integer, ForeignKey("gameweeks.id"), nullable=False)
    # Raw stats from FBRef
    minutes_played = Column(Integer, default=0)
    goals = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    clean_sheet = Column(Integer, default=0)  # 1 if kept
    goals_conceded = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    penalties_saved = Column(Integer, default=0)
    penalties_missed = Column(Integer, default=0)
    yellow_cards = Column(Integer, default=0)
    red_cards = Column(Integer, default=0)
    own_goals = Column(Integer, default=0)
    # Computed
    fantasy_points = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    player = relationship("Player", back_populates="stats")
    gameweek = relationship("Gameweek", back_populates="player_stats")
