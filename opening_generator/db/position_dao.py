import logging

import chess
from chess.polyglot import zobrist_hash
from sqlalchemy.orm import Session

from opening_generator.models import Position


class PositionDao:
    def __init__(self, session: Session) -> None:
        self.logger = logging.getLogger(__name__)
        self.session = session

    def get_initial_position(self):
        board: chess.Board = chess.Board()
        initial_pos_id: str = str(zobrist_hash(board=board))
        return (
            self.session.query(Position).filter(Position.pos_id == initial_pos_id).first()
        )

    def get_position(self, pos_id):
        return self.session.query(Position).filter(Position.pos_id == pos_id).first()

    def save_positions(self, positions):
        self.session.add_all(positions.values())
        self.session.commit()

