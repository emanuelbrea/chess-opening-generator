import logging

from opening_generator.db import db_session
from opening_generator.models import Move


class MoveDao:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_initial_position(self):
        return db_session.query(Move).filter(Move.move.is_(None)).one()


move_dao = MoveDao()
