from sqlalchemy import Column, Float, ForeignKey, Integer, CheckConstraint
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class Style(Base):
    __tablename__ = "style"

    style_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(ForeignKey("user.user_id"), primary_key=True)
    popularity = Column(
        Float,
        CheckConstraint("popularity >= -1 and popularity <= 1"),
        nullable=False,
        default=0,
    )
    fashion = Column(
        Float,
        CheckConstraint("fashion >= -1 and fashion <= 1"),
        nullable=False,
        default=0,
    )
    risk = Column(
        Float,
        CheckConstraint("risk >= -1 and risk <= 1"),
        nullable=False,
        default=0,
    )
    rating = Column(
        Integer, CheckConstraint("rating >= 0"), nullable=False, default=0
    )

    user = relationship("User", back_populates="style")
