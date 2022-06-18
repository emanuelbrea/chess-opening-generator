from sqlalchemy import ForeignKey, Column, String, Integer, Table
from sqlalchemy.orm import relationship

from opening_generator.db import Base

association_table = Table(
    "association",
    Base.metadata,
    Column("repertoire_id", ForeignKey("repertoire.repertoire_id")),
    Column("move_id", ForeignKey("move.move_id")),
)


class Repertoire(Base):
    __tablename__ = "repertoire"

    repertoire_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.user_id'))
    color = Column(String)

    user = relationship("User", back_populates="repertoire")

    moves = relationship("Move", secondary=association_table)
