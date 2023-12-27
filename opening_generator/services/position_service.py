import logging

import chess
from chess import svg
from chess.polyglot import zobrist_hash
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from opening_generator.db.position_dao import PositionDao
from opening_generator.models import Position, Move
from opening_generator.services.position_loader_service import PositionLoaderService


class PositionService:
    def __init__(self, session: Session):
        self.logger = logging.getLogger(__name__)
        self.position_dao = PositionDao(session)
        # self.retrieve_initial_position()

    def get_position_by_board(self, board: chess.Board) -> Position:
        position: Position = self.get_position(board=board)
        if not position:
            raise HTTPException(status_code=404, detail="Position not found in database")
        return position

    def retrieve_initial_position(self) -> Position:
        try:
            initial_position = self.position_dao.get_initial_position()
        except NoResultFound:
            position_loader = PositionLoaderService()
            initial_position = position_loader.load_games()
            self.position_dao.save_positions(initial_position)
        return initial_position

    def get_position(self, board: chess.Board):
        pos_id: str = str(zobrist_hash(board=board))
        return self.position_dao.get_position(pos_id)

    def get_next_moves(self, position):
        return [move.move_san for move in position.next_moves]

    def get_next_moves_stats(self, position):
        position_stats = self.get_position_stats(position=position)
        moves = []
        for move in position.next_moves:
            moves.append(self.get_move_stats(move=move))
        moves = sorted(moves, key=lambda d: d["played"], reverse=True)
        return dict(position=position_stats, moves=moves)

    def get_move_stats(self, move: Move):
        next_position: Position = move.next_position
        return dict(
            played=move.played,
            frequency=move.popularity_weight,
            white_wins=round(next_position.white_wins / next_position.total_games, 2),
            black_wins=round(next_position.black_wins / next_position.total_games, 2),
            draws=round(next_position.draws / next_position.total_games, 2),
            winning_rate=next_position.winning_rate,
            year=next_position.average_year,
            average_elo=next_position.average_elo,
            performance=next_position.performance,
            fen=next_position.fen,
            move=move.move_san,
            eco_code=next_position.eco_code.eco_code
            if next_position.eco_code
            else None,
            name=next_position.eco_code.name if next_position.eco_code else None,
            link=move.description,
        )

    def get_position_stats(self, position: Position) -> dict:
        return dict(
            total_games=position.total_games,
            white_wins=position.white_wins,
            black_wins=position.black_wins,
            draws=position.draws,
            winning_rate=position.winning_rate,
            year=position.average_year,
            average_elo=position.average_elo,
            performance=position.performance,
            fen=position.fen,
            eco_code=position.eco_code.eco_code if position.eco_code else None,
            turn=position.turn,
        )

    def get_position_svg(self, position: Position, move: str, color: bool = True) -> str:
        fen = position.fen
        board = chess.Board(fen=fen)
        if move:
            try:
                last_move = board.push_san(move)
                position_svg = str(
                    svg.board(
                        board=board,
                        lastmove=last_move,
                        orientation=chess.WHITE if color else chess.BLACK,
                    )
                )

            except ValueError:
                return None
        else:
            position_svg = str(
                svg.board(
                    board=board, orientation=chess.WHITE if color else chess.BLACK
                )
            )
        return position_svg
