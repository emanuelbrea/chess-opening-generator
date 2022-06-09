from sqlalchemy import Column, Float, ForeignKey
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class Style(Base):
    __tablename__ = "style"

    user_id = Column(ForeignKey('user.user_id'), primary_key=True)
    popularity = Column(Float)
    fashion = Column(Float)
    risk = Column(Float)

    user = relationship("User", back_populates="style")
