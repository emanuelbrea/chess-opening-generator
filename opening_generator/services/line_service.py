import logging
from typing import List

import chess
from chess.polyglot import zobrist_hash

from opening_generator.db.line_dao import line_dao
from opening_generator.models.line import Line


class LineService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_next_moves(self, line: Line):
        moves = [next_move.move for next_move in line.next_moves]
        return moves

    def get_next_moves_as_san(self, line: Line, board: chess.Board):
        moves = self.get_next_moves(line=line)
        moves = [board.parse_uci(move) for move in moves]
        moves = [board.san(move) for move in moves]
        return moves

    def get_line(self, board: chess.Board):
        line_id = str(zobrist_hash(board=board))
        line: Line = line_dao.get_line_by_position(line_id)
        return line

    def get_line_by_id(self, line_id: str):
        line: Line = line_dao.get_line_by_position(line_id)
        return line

    def save_lines(self, games: {}):
        return line_dao.save_lines(games)

    def get_next_positions_as_df(self, line: Line):
        lines: List[str] = [nl.next_line_id for nl in line.next_moves]
        positions = line_dao.get_next_positions_as_df(lines)
        return positions


line_service = LineService()
