from sqlalchemy import Integer, Column, String, Table, ForeignKey
from sqlalchemy.orm import relationship

from opening_generator.db import Base

NextLineRelationship = Table(
    'next_line', Base.metadata,
    Column('line_id', ForeignKey('line.line_id')),
    Column('next_line_id', ForeignKey('line.line_id'))
)


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

    next_lines = relationship("Line",
                              secondary=NextLineRelationship,
                              primaryjoin=NextLineRelationship.c.line_id == line_id,
                              secondaryjoin=NextLineRelationship.c.next_line_id == line_id,
                              backref="children")

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

    def add_next_line(self, line):
        if line not in self.next_lines:
            self.next_lines.append(line)
