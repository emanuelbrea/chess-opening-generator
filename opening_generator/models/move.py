from typing import List

from sqlalchemy import Integer, Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class Move(Base):
    __tablename__ = "move"

    move_id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(move_id))
    move = Column(String)
    color = Column(Boolean)
    total_games = Column(Integer)
    white_wins = Column(Integer)
    draws = Column(Integer)
    black_wins = Column(Integer)
    average_year = Column(Integer)
    average_elo = Column(Integer)

    next_moves = relationship("Move")

    def __init__(self, move, color, total_games, white_wins, draws, black_wins, average_elo, average_year):
        self.move = move
        self.color = color
        self.total_games = total_games
        self.white_wins = white_wins
        self.draws = draws
        self.black_wins = black_wins
        self.average_elo = average_elo
        self.average_year = average_year

    def get_next_move(self, move_uci):
        for move in self.next_moves:
            if move.move == move_uci:
                return move
        return None

    def get_variation(self, moves: List[str]):
        if len(moves) == 0:
            return self
        next_move = self.get_next_move(moves.pop(0))
        if not next_move:
            return self
        return next_move.get_variation(moves)
