import logging

import chess
import pandas as pd
from chess.polyglot import zobrist_hash

from opening_generator.db.line_dao import line_dao
from opening_generator.models.line import Line


class LineService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.lines = self._get_lines()

    def get_next_moves_as_san(self, line: Line, board: chess.Board):
        moves = [next_move.move for next_move in line.next_moves]
        moves = [board.parse_uci(move) for move in moves]
        moves = [board.san(move) for move in moves]
        return moves

    def get_line(self, board: chess.Board):
        line_id = str(zobrist_hash(board=board))
        return self.get_line_by_id(line_id=line_id)

    def get_line_by_id(self, line_id: str):
        line: Line = self.lines.get(line_id)
        return line

    def save_lines(self, games: {}):
        return line_dao.save_lines(games)

    def _get_lines(self):
        lines_db = line_dao.get_lines()
        lines = {}
        for line in lines_db:
            lines[line.line_id] = line
        return lines

    def get_lines_as_df(self, line: Line):
        lines = []
        for move in line.next_moves:
            next_line = self.lines.get(move.next_line_id)
            lines.append((next_line.line_id, move.move, next_line.total_games, next_line.white_wins, next_line.draws,
                          next_line.black_wins,
                          next_line.average_year, next_line.average_elo))
        return pd.DataFrame.from_records(lines,
                                         columns=['line_id', 'move', 'total_games', 'white_wins', 'draws', 'black_wins',
                                                  'average_year', 'average_elo'])


line_service = LineService()
