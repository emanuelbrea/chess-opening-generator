import logging
from typing import List

from opening_generator.db import db_session
from opening_generator.models.eco_code import EcoCode


class EcoCodeDao:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_eco_code(self, eco_code: str):
        return db_session.query(EcoCode).filter(EcoCode.eco_code == eco_code).first()

    def add_eco_codes(self, ecos: List[EcoCode]):
        db_session.add_all(ecos)
        db_session.commit()
        db_session.close()


eco_code_dao = EcoCodeDao()
