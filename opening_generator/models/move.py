from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class Move(Base):
    __tablename__ = "move"

    move_id = Column(Integer, primary_key=True, autoincrement=True)
    move = Column(String)
    total_games = Column(Integer)
    white_wins = Column(Integer)
    draws = Column(Integer)
    black_wins = Column(Integer)
    average_year = Column(Integer)
    average_elo = Column(Integer)

    next_moves = relationship("NextMove", primaryjoin="Move.move_id == NextMove.move_id")

    def __init__(self, move, color, total_games, white_wins, draws, black_wins, average_elo, average_year):
        self.move = move
        self.color = color
        self.total_games = total_games
        self.white_wins = white_wins
        self.draws = draws
        self.black_wins = black_wins
        self.average_elo = average_elo
        self.average_year = average_year
