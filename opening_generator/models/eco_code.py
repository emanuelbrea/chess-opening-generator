from sqlalchemy import Column, String, ForeignKey

from opening_generator.db import Base


class EcoCode(Base):
    __tablename__ = "eco_code"

    eco_code = Column(String, primary_key=True)
    name = Column(String)
    pos_id = Column(ForeignKey('position.pos_id'))
