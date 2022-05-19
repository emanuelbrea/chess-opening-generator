from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    email = Column(String)

    repertoire = relationship("Repertoire", back_populates="user")
