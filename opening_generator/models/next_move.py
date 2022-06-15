from sqlalchemy import Column, ForeignKey

from opening_generator.db import Base


class NextMove(Base):
    __tablename__ = "next_move"

    move_id = Column(ForeignKey('move.move_id'), primary_key=True)
    next_move_id = Column(ForeignKey('move.move_id'), primary_key=True)
