import logging

from opening_generator.models.line import Line


class LineService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_next_moves(self, line: Line):
        moves = [next_move.move for next_move in line.next_moves]
        return moves


line_service = LineService()
