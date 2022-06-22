from sqlalchemy import Column, Float, ForeignKey, Integer, CheckConstraint
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class Style(Base):
    __tablename__ = "style"

    style_id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey('user.user_id'), unique=True, nullable=False)
    popularity = Column(Float, CheckConstraint('style.popularity >= -1 and style.popularity <= 1'), nullable=False,
                        default=0)
    fashion = Column(Float, CheckConstraint('style.fashion >= -1 and style.fashion <= 1'), nullable=False, default=0)
    risk = Column(Float, CheckConstraint('style.risk >= -1 and style.risk <= 1'), nullable=False, default=0)
    rating = Column(Integer, CheckConstraint('style.rating >= 0'), nullable=False, default=0)

    user = relationship("User", back_populates="style")
