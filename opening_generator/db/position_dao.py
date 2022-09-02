import logging

import chess
from chess.polyglot import zobrist_hash

from opening_generator.db import db_session
from opening_generator.models import Position


class PositionDao:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_initial_position(self):
        board: chess.Board = chess.Board()
        initial_pos_id: str = str(zobrist_hash(board=board))
        return (
            db_session.query(Position).filter(Position.pos_id == initial_pos_id).one()
        )

    def get_position(self, pos_id):
        return db_session.query(Position).filter(Position.pos_id == pos_id).first()

    def save_positions(self, positions):
        db_session.add_all(positions.values())
        db_session.commit()


position_dao = PositionDao()
