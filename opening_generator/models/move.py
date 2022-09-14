from sqlalchemy import Integer, Column, String, ForeignKey, Float, DateTime, func
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class Move(Base):
    __tablename__ = "move"

    move_id = Column(Integer, primary_key=True)
    next_pos_id = Column(ForeignKey("position.pos_id"), nullable=False)
    move_san = Column(String(15), nullable=False)
    played = Column(Integer, nullable=False)
    popularity_weight = Column(Float, nullable=False)
    description = Column(String, nullable=True)

    next_position = relationship("Position")


class FavoriteMoves(Base):
    __tablename__ = "favorite_moves"

    user_id = Column(ForeignKey("user.user_id"), primary_key=True)
    move_id = Column(ForeignKey("move.move_id"), primary_key=True)
    updated_at = Column(DateTime(timezone=False), server_default=func.now())

    move = relationship("Move")
