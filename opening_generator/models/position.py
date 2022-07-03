from sqlalchemy import Integer, Column, String, Boolean, Table, ForeignKey, CheckConstraint, Float
from sqlalchemy.orm import relationship

from opening_generator.db import Base

association_table = Table(
    "next_moves",
    Base.metadata,
    Column("pos_id", ForeignKey("position.pos_id"), primary_key=True),
    Column("move_id", ForeignKey("move.move_id"), primary_key=True),
)


class Position(Base):
    __tablename__ = "position"

    pos_id = Column(String, primary_key=True)

    total_games = Column(Integer,
                         CheckConstraint(
                             'position.white_wins + position.draws + position.black_wins = position.total_games'),
                         nullable=False)
    white_wins = Column(Integer, CheckConstraint('position.white_wins >= 0'), nullable=False)
    draws = Column(Integer, CheckConstraint('position.draws >= 0'), nullable=False)
    black_wins = Column(Integer, CheckConstraint('position.black_wins >= 0'), nullable=False)
    average_year = Column(Integer, CheckConstraint('position.average_year > 0'), nullable=False)
    average_elo = Column(Integer, CheckConstraint('position.average_elo > 0'), nullable=False)
    performance = Column(Integer, CheckConstraint('position.performance > 0'), nullable=False)
    winning_rate = Column(Float, nullable=False)
    turn = Column(Boolean)
    fen = Column(String(100))

    next_moves = relationship("Move", secondary=association_table)
    eco_code = relationship("EcoCode", back_populates="position", uselist=False)

    def set_final_elo(self):
        self.average_elo = self.average_elo // self.total_games

    def set_final_performance(self):
        self.performance = self.performance // self.total_games

    def set_final_year(self):
        self.average_year = self.average_year // self.total_games

    def set_winning_rate(self):
        self.winning_rate = (self.white_wins + 0.5 * self.draws) / self.total_games

    def set_popularity_weight(self):
        for move in self.next_moves:
            if move.popularity_weight is None:
                move.popularity_weight = move.played / self.total_games

    def set_final_values(self):
        self.set_final_year()
        self.set_final_elo()
        self.set_popularity_weight()
        self.set_final_performance()
        self.set_winning_rate()
