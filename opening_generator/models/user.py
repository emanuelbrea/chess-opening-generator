from sqlalchemy import Column, Integer, String, DateTime, func, CheckConstraint
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    age = Column(Integer, CheckConstraint("user.age > 0"), nullable=False, default=0)
    playing_since = Column(
        Integer,
        CheckConstraint("user.playing_since > 0 and user.playing_since <= age"),
        nullable=False,
        default=0,
    )

    repertoire = relationship(
        "Repertoire", back_populates="user", cascade="all, delete-orphan"
    )

    style = relationship(
        "Style", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
