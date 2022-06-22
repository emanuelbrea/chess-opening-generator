from sqlalchemy import Integer, Column, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

from opening_generator.db import Base
from opening_generator.models import Move

association_table = Table(
    "next_moves",
    Base.metadata,
    Column("pos_id", ForeignKey("position.pos_id"), primary_key=True),
    Column("move_id", ForeignKey("move.move_id"), primary_key=True),
)


class Position(Base):
    __tablename__ = "position"

    pos_id = Column(String, primary_key=True)

    total_games = Column(Integer)
    white_wins = Column(Integer)
    draws = Column(Integer)
    black_wins = Column(Integer)
    average_year = Column(Integer)
    average_elo = Column(Integer)
    turn = Column(Boolean)
    fen = Column(String)

    next_moves = relationship("Move", secondary=association_table)

    def __init__(self, pos_id, total_games, white_wins, draws, black_wins, average_year, average_elo, turn, fen):
        self.pos_id = pos_id
        self.total_games = total_games
        self.white_wins = white_wins
        self.draws = draws
        self.black_wins = black_wins
        self.average_elo = average_elo
        self.average_year = average_year
        self.turn = turn
        self.fen = fen
        self.next_moves = []

    def set_final_elo(self):
        self.average_elo = self.average_elo // self.total_games

    def set_final_year(self):
        self.average_year = self.average_year // self.total_games

    def set_popularity_weight(self):
        for move in self.next_moves:
            if move.popularity_weight == 0:
                move.popularity_weight = move.played / self.total_games

    def set_final_values(self):
        self.set_final_year()
        self.set_final_elo()
        self.set_popularity_weight()

    def add_move(self, move_san):
        for next_move in self.next_moves:
            if next_move.move_san == move_san:
                next_move.played += 1
                return next_move
        move = Move(move_san)
        self.next_moves.append(move)
        return move
