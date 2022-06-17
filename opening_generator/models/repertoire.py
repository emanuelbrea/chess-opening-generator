from sqlalchemy import ForeignKey, Column, String
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class Repertoire(Base):
    __tablename__ = "repertoire"

    user_id = Column(ForeignKey('user.user_id'), primary_key=True)
    move_id = Column(ForeignKey('move.move_id'), primary_key=True)
    color = Column(String, primary_key=True)

    moves = relationship("Move")

    user = relationship("User", back_populates="repertoire")
