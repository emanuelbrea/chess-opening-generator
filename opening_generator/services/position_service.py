import logging

import chess
from chess.polyglot import zobrist_hash
from sqlalchemy.exc import NoResultFound

from opening_generator.db.position_dao import position_dao
from opening_generator.models import Position, Move
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
        position_stats = self.get_position_stats(position=position)
        moves = []
        for move in position.next_moves:
            moves.append(self.get_move_stats(move=move))
        moves = sorted(moves, key=lambda d: d['played'], reverse=True)
        return dict(position=position_stats, moves=moves)

    def get_move_stats(self, move: Move):
        next_position: Position = move.next_position
        return dict(played=move.played,
                    frequency=move.popularity_weight,
                    white_wins=next_position.white_wins,
                    black_wins=next_position.black_wins,
                    draws=next_position.draws,
                    winning_rate=next_position.winning_rate,
                    year=next_position.average_year,
                    average_elo=next_position.average_elo,
                    performance=next_position.performance,
                    fen=next_position.fen,
                    move=move.move_san
                    )

    def get_position_stats(self, position: Position):
        return dict(total_games=position.total_games,
                    white_wins=position.white_wins,
                    black_wins=position.black_wins,
                    draws=position.draws,
                    winning_rate=position.winning_rate,
                    year=position.average_year,
                    average_elo=position.average_elo,
                    performance=position.performance,
                    fen=position.fen
                    )


position_service = PositionService()
