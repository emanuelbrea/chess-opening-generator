import logging

import chess

from opening_generator.models.line import Line


class LineService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_next_moves(self, line: Line):
        moves = [next_move.move for next_move in line.next_moves]
        return moves

    def get_next_moves_as_san(self, line: Line):
        moves = self.get_next_moves(line=line)
        board = chess.Board(fen=line.fen)
        moves = [board.parse_uci(move) for move in moves]
        moves = [board.san(move) for move in moves]
        return moves


line_service = LineService()
