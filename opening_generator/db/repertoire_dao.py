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
        self.logger.info("Created %s repertoire for user %s.", "white" if color else "black", user.email)

    def delete_repertoire(self, user, color):
        db_session.query(Repertoire).filter(
            Repertoire.user_id == user.user_id,
            Repertoire.color == color
        ).delete()
        self.logger.info("Deleted %s repertoire for user %s.", "white" if color else "black", user.email)

    def delete_moves_from_repertoire(self, repertoire, moves, user, color):
        repertoire.moves = list(set(repertoire.moves) - set(moves))
        db_session.commit()
        self.logger.info("Deleted %d moves from %s repertoire for user %s.", len(moves), "white" if color else "black",
                         user.email)

    def insert_new_moves(self, repertoire, moves, user, color):
        repertoire.moves += moves
        db_session.commit()
        self.logger.info("Inserted %d moves from %s repertoire for user %s.", len(moves), "white" if color else "black",
                         user.email)


repertoire_dao = RepertoireDao()
