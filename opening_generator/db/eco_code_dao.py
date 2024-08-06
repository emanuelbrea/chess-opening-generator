import logging
from typing import List

from sqlalchemy.orm import Session

from opening_generator.models import Position
from opening_generator.models.eco_code import EcoCode


class EcoCodeDao:
    def __init__(self, session: Session) -> None:
        self.logger = logging.getLogger(__name__)
        self.session = session

    def get_eco_code(self, position: Position):
        return self.session.query(EcoCode).filter(EcoCode.position == position).first()

    def add_eco_codes(self, ecos: List[EcoCode]):
        self.session.add_all(ecos)
        self.session.commit()
        self.session.close()

    def get_eco_codes(self):
        ecos = self.session.query(EcoCode).all()
        return ecos
