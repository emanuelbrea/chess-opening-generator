import logging

from opening_generator.db import db_session
from opening_generator.models import Repertoire


class RepertoireDao:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_repertoire(self, user, color, moves):
        self.delete_repertoire(user, color)
        repertoire = Repertoire(user=user, color=color, moves=moves)
        db_session.add(repertoire)
        db_session.commit()

    def delete_repertoire(self, user, color):
        db_session.query(Repertoire).filter(
            Repertoire.user_id == user.user_id,
            Repertoire.color == color
        ).delete()


repertoire_dao = RepertoireDao()
