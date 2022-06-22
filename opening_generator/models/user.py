from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    rating = Column(Integer, default=0)

    repertoire = relationship("Repertoire", back_populates="user")

    style = relationship("Style", back_populates="user", uselist=False)
