from sqlalchemy import Column, Integer, String, DateTime, func

from opening_generator.db import Base


class Contact(Base):
    __tablename__ = "contact"

    contact_id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    message = Column(String)
    rating = Column(Integer)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
