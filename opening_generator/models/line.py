from sqlalchemy import Integer, Column, String
from sqlalchemy.orm import relationship

from opening_generator.db import Base
from opening_generator.models.next_line import NextLine


class Line(Base):
    __tablename__ = "line"

    line_id = Column(String, primary_key=True)
    fen = Column(String)
    total_games = Column(Integer)
    white_wins = Column(Integer)
    draws = Column(Integer)
    black_wins = Column(Integer)
    last_year = Column(Integer)
    average_elo = Column(Integer)

    next_moves = relationship("NextLine")

    eco_code = relationship("EcoCode", back_populates="line", uselist=False)

    def __init__(self, line_id, fen, total_games, white_wins, draws, black_wins, average_elo, last_year):
        self.line_id = line_id
        self.fen = fen
        self.total_games = total_games
        self.white_wins = white_wins
        self.draws = draws
        self.black_wins = black_wins
        self.average_elo = average_elo
        self.last_year = last_year
        self._total_ranked_games: int = 1 if average_elo > 0 else 0

    def add_elo(self, new_elo: int):
        if new_elo > 0:
            self.average_elo += new_elo
            self._total_ranked_games += 1

    def set_final_elo(self):
        self.average_elo = self.average_elo // self._total_ranked_games if self._total_ranked_games > 0 else 0

    def add_next_move(self, move: str):
        if move not in [next_move.move for next_move in self.next_moves]:
            self.next_moves.append(NextLine(line_id=self.line_id, move=move))
