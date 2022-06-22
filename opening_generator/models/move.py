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

    def __init__(self, move_san):
        self.move_san = move_san
        self.played = 1
        self.popularity_weight = 0

    def set_popularity_weight(self):
        if self.popularity_weight == 0:
            self.popularity_weight = self.played / self.next_position.total_games
