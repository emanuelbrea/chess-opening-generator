from sqlalchemy import (
    ForeignKey,
    Column,
    Integer,
    Table,
    Boolean,
    DateTime,
    func,
    Float,
)
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
    user_id = Column(ForeignKey("user.user_id"), nullable=False)
    color = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), server_default=func.now())

    user = relationship("User", back_populates="repertoire")

    moves = relationship("Move", secondary=association_table)


class RepertoireHistory(Base):
    __tablename__ = "repertoire_history"

    repertoire_history_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.user_id"), nullable=False)
    move_id = Column(ForeignKey("move.move_id"), nullable=False)
    old_move_id = Column(ForeignKey("move.move_id"), nullable=False)
    updated_at = Column(DateTime(timezone=False), server_default=func.now())


class RepertoireMetric(Base):
    __tablename__ = "repertoire_metric"

    repertoire_metric_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("user.user_id"), nullable=False)
    moves = Column(Integer, nullable=False)
    time_elapsed = Column(Float, nullable=False)
    updated_at = Column(DateTime(timezone=False), server_default=func.now())
