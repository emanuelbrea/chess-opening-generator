import logging

import chess
from chess.polyglot import zobrist_hash
from sqlalchemy.exc import NoResultFound

from opening_generator import Position, PositionLoaderService
from opening_generator.db.position_dao import position_dao


class PositionService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def retrieve_initial_position(self) -> Position:
        try:
            initial_position = position_dao.get_initial_position()
        except NoResultFound:
            position_loader = PositionLoaderService()
            positions = position_loader.load_games()
            position_dao.save_positions(positions)
            initial_position = position_dao.get_initial_position()
        return initial_position

    def get_position(self, board: chess.Board):
        pos_id: str = str(zobrist_hash(board=board))
        return position_dao.get_position(pos_id)

    def get_next_moves(self, position):
        return [move.move_san for move in position.next_moves]

    def get_next_moves_stats(self, position):
        stats = {}
        for move in position.next_moves:
            next_position = move.next_position
            stats[move.move_san] = dict(total_games=next_position.total_games,
                                        white_wins=next_position.white_wins,
                                        black_wins=next_position.black_wins,
                                        draws=next_position.draws,
                                        year=next_position.average_year,
                                        average_elo=next_position.average_elo,
                                        )
        return stats


position_service = PositionService()
