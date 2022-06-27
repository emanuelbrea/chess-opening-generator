from sqlalchemy import Integer, Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class Move(Base):
    __tablename__ = "move"

    move_id = Column(Integer, primary_key=True)
    next_pos_id = Column(ForeignKey('position.pos_id'), nullable=False)
    move_san = Column(String(15), nullable=False)
    played = Column(Integer, nullable=False)
    popularity_weight = Column(Float, nullable=False)

    next_position = relationship("Position")
