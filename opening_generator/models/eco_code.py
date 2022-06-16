from sqlalchemy import Column, String

from opening_generator.db import Base


class EcoCode(Base):
    __tablename__ = "eco_code"

    eco_code = Column(String, primary_key=True)
    name = Column(String)
    main_line = Column(String)
