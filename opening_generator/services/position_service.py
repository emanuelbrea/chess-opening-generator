import logging

import chess
from chess.polyglot import zobrist_hash
from sqlalchemy.exc import NoResultFound

from opening_generator.db.position_dao import position_dao
from opening_generator.models import Position
from opening_generator.services.position_loader_service import PositionLoaderService


class PositionService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retrieve_initial_position()

    def retrieve_initial_position(self) -> Position:
        try:
            initial_position = position_dao.get_initial_position()
        except NoResultFound:
            position_loader = PositionLoaderService()
            initial_position = position_loader.load_games()
            position_dao.save_positions(initial_position)
        return initial_position

    def get_position(self, board: chess.Board):
        pos_id: str = str(zobrist_hash(board=board))
        return position_dao.get_position(pos_id)

    def get_next_moves(self, position):
        return [move.move_san for move in position.next_moves]

    def get_next_moves_stats(self, position):
        stats = {'position': dict(total_games=position.total_games,
                                  white_wins=position.white_wins,
                                  black_wins=position.black_wins,
                                  draws=position.draws,
                                  winning_rate=position.winning_rate,
                                  year=position.average_year,
                                  average_elo=position.average_elo,
                                  performance=position.performance,
                                  fen=position.fen
                                  ), 'moves': {}}
        for move in position.next_moves:
            next_position = move.next_position
            stats['moves'][move.move_san] = dict(played=move.played,
                                                 frequency=move.played / position.total_games,
                                                 white_wins=next_position.white_wins,
                                                 black_wins=next_position.black_wins,
                                                 draws=next_position.draws,
                                                 winning_rate=next_position.winning_rate,
                                                 year=next_position.average_year,
                                                 average_elo=next_position.average_elo,
                                                 performance=position.performance,
                                                 fen=next_position.fen
                                                 )
        return stats


position_service = PositionService()
