import logging
import os
import time

import chess.pgn
from chess.polyglot import zobrist_hash

from opening_generator import Position


class PositionLoaderService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.folder = "/../../data/pgn/"
        self.max_moves = 30
        self.total_games = 0
        self.positions = {}

    def load_games(self):
        for filename in os.listdir(os.path.dirname(__file__) + self.folder):
            if os.path.splitext(filename)[1] == '.pgn':
                file = os.path.dirname(__file__) + os.path.join(self.folder, filename)
                self.load_file(file)
        return self.positions.values()

    def load_file(self, filename: str):
        self.logger.info("About to read %s", filename)
        start = time.time()
        with open(filename) as pgn:
            while True:
                game: chess.pgn.Game = chess.pgn.read_game(pgn)

                if not game:
                    break

                result: str = game.headers.get("Result")
                elo_white: int = int(game.headers.get("WhiteElo", 0))
                elo_black: int = int(game.headers.get("BlackElo", 0))
                date: str = game.headers.get("Date")
                year: int = int(date.split(".")[0])

                white_wins = 1 if result == "1-0" else 0
                draws = 1 if result == "1/2-1/2" else 0
                black_wins = 1 if result == "0-1" else 0

                moves = game.mainline_moves()
                board: chess.Board = chess.Board()

                prev_pos_id: str = str(zobrist_hash(board=board))

                self.set_position(prev_pos_id, white_wins, draws, black_wins, elo_white, elo_black, year, True, board)

                for move in moves:
                    if board.ply() > self.max_moves:
                        break

                    move_san = board.san(move)
                    board.push(move)
                    turn = board.turn

                    prev_position = self.positions[prev_pos_id]
                    move = prev_position.add_move(move_san)

                    pos_id: str = str(zobrist_hash(board=board))

                    self.set_position(pos_id, white_wins, draws, black_wins, elo_white, elo_black, year, turn, board)

                    move.next_position = self.positions[pos_id]

                    prev_pos_id = pos_id

                self.total_games += 1
                if self.total_games % 10000 == 0:
                    self.logger.info("%d ", self.total_games)
        self.logger.info("Loaded %s in %f seconds.", filename, time.time() - start)

    def set_position(self, pos_id, white_wins, draws, black_wins, elo_white, elo_black, year, turn, board):
        if pos_id in self.positions:
            position = self.positions[pos_id]
            position.total_games += 1
            position.white_wins += white_wins
            position.draws += draws
            position.black_wins += black_wins
            if turn:
                position.average_elo += elo_white
            else:
                position.average_elo += elo_black
            position.average_year += year
        else:
            self.positions[pos_id] = Position(
                pos_id=pos_id,
                total_games=1,
                white_wins=white_wins,
                draws=draws,
                black_wins=black_wins,
                average_elo=elo_white if turn else elo_black,
                average_year=year,
                turn=turn,
                fen=board.fen()
            )
