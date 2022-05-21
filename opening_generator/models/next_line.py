from sqlalchemy import Column, String, ForeignKey

from opening_generator.db import Base


class NextLine(Base):
    __tablename__ = "next_line"

    line_id = Column(ForeignKey('line.line_id'), primary_key=True)
    move = Column(String, primary_key=True)
