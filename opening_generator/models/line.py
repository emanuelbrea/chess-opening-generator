from sqlalchemy import Integer, Column, String, Index
from sqlalchemy.orm import relationship

from opening_generator.db import Base
from opening_generator.models.next_line import NextLine


class Line(Base):
    __tablename__ = "line"

    line_id = Column(String, primary_key=True)
    total_games = Column(Integer)
    white_wins = Column(Integer)
    draws = Column(Integer)
    black_wins = Column(Integer)
    average_year = Column(Integer)
    average_elo = Column(Integer)

    next_moves = relationship("NextLine", primaryjoin="Line.line_id == NextLine.line_id")

    eco_code = relationship("EcoCode", back_populates="line", uselist=False)

    line_index = Index('line_index', line_id)

    def __init__(self, line_id, total_games, white_wins, draws, black_wins, average_elo, average_year):
        self.line_id = line_id
        self.total_games = total_games
        self.white_wins = white_wins
        self.draws = draws
        self.black_wins = black_wins
        self.average_elo = average_elo
        self.average_year = average_year

    def set_final_elo(self):
        self.average_elo = self.average_elo // self.total_games

    def set_final_year(self):
        self.average_year = self.average_year // self.total_games

    def add_next_move(self, move: str, next_line_id: str):
        if move not in [next_move.move for next_move in self.next_moves]:
            self.next_moves.append(NextLine(line_id=self.line_id, move=move, next_line_id=next_line_id))
