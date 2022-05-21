from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from opening_generator.db import Base


class EcoCode(Base):
    __tablename__ = "eco_code"

    eco_code = Column(String, primary_key=True)
    name = Column(String)
    main_line = Column(String)
    line_id = Column(String, ForeignKey('line.line_id'))

    line = relationship("Line", back_populates="eco_code")
