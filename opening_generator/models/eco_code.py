from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class EcoCode(Base):
    __tablename__ = "eco_code"

    eco_code_id = Column(Integer, primary_key=True)
    eco_code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    main_line = Column(String, nullable=False)
    pos_id = Column(ForeignKey('position.pos_id'), nullable=True, unique=True)

    position = relationship("Position", back_populates="eco_code")
