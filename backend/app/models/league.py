from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base


class LeagueType(str, enum.Enum):
    classic = "classic"    # Cumulative points all season
    head_to_head = "h2h"   # Weekly matchups against one opponent


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    # 6-char invite code friends use to join
    invite_code = Column(String(10), unique=True, nullable=False, index=True)
    league_type = Column(Enum(LeagueType), default=LeagueType.classic)
    max_teams = Column(Integer, default=20)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    # Which season (e.g. "2024-25")
    season = Column(String(10), default="2024-25")

    memberships = relationship("LeagueMembership", back_populates="league", cascade="all, delete-orphan")
    creator = relationship("User", foreign_keys=[created_by])


class LeagueMembership(Base):
    __tablename__ = "league_memberships"

    id = Column(Integer, primary_key=True, index=True)
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    # Cumulative league points (classic)
    total_points = Column(Integer, default=0)
    rank = Column(Integer)

    league = relationship("League", back_populates="memberships")
    user = relationship("User", back_populates="memberships")
    team = relationship("Team")
