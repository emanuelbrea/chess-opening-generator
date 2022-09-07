import logging
from datetime import datetime
from typing import List

from opening_generator.db import db_session
from opening_generator.models import Repertoire, Move, User


class RepertoireDao:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_repertoire(self, user: User, color: bool, moves: List[Move]):
        self.delete_repertoire(user, color)
        repertoire = Repertoire(user=user, color=color, moves=moves)
        db_session.add(repertoire)
        db_session.commit()
        self.logger.info(
            "Created %s repertoire for user %s.",
            "white" if color else "black",
            user.email,
        )

    def delete_repertoire(self, user: User, color: bool):
        user.repertoire = [
            repertoire for repertoire in user.repertoire if repertoire.color != color
        ]
        self.logger.info(
            "Deleted %s repertoire for user %s.",
            "white" if color else "black",
            user.email,
        )

    def insert_new_moves(
        self,
        repertoire: Repertoire,
        moves: List[Move],
        user: User,
        color: bool,
        old_moves: List[Move],
    ):
        repertoire.moves = list(set(repertoire.moves) - set(old_moves))
        repertoire.moves += moves
        repertoire.updated_at = datetime.now()
        db_session.commit()
        self.logger.info(
            "Deleted %d moves from %s repertoire for user %s.",
            len(set(old_moves)),
            "white" if color else "black",
            user.email,
        )
        self.logger.info(
            "Inserted %d moves from %s repertoire for user %s.",
            len(set(moves)),
            "white" if color else "black",
            user.email,
        )


repertoire_dao = RepertoireDao()
