import logging
from typing import List

from opening_generator.db import db_session
from opening_generator.models import Position
from opening_generator.models.eco_code import EcoCode


class EcoCodeDao:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_eco_code(self, position: Position):
        return db_session.query(EcoCode).filter(EcoCode.position == position).first()

    def add_eco_codes(self, ecos: List[EcoCode]):
        db_session.add_all(ecos)
        db_session.commit()
        db_session.close()

    def get_eco_codes(self):
        ecos = db_session.query(EcoCode).all()
        return ecos


eco_code_dao = EcoCodeDao()
