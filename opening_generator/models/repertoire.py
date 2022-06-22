from sqlalchemy import ForeignKey, Column, Integer, Table, Boolean
from sqlalchemy.orm import relationship

from opening_generator.db import Base

association_table = Table(
    "repertoire_moves",
    Base.metadata,
    Column("repertoire_id", ForeignKey("repertoire.repertoire_id"), primary_key=True),
    Column("move_id", ForeignKey("move.move_id"), primary_key=True),
)


class Repertoire(Base):
    __tablename__ = "repertoire"

    repertoire_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.user_id'), nullable=False)
    color = Column(Boolean, nullable=False)

    user = relationship("User", back_populates="repertoire")

    moves = relationship("Move", secondary=association_table)
