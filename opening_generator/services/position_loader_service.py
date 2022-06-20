import logging
import os
import time

import chess.pgn
from chess.polyglot import zobrist_hash

from opening_generator.models import Position


class PositionLoaderService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.folder = "/../../data/pgn/"
        self.max_moves = 30
        self.total_games = 0
        self.positions = {}
        self.initial_pos = self.set_initial_position()
        self.visited = {}

    def set_initial_position(self):
        board: chess.Board = chess.Board()
        initial_pos_id: str = str(zobrist_hash(board=board))
        initial_position = Position(
            pos_id=initial_pos_id,
            total_games=0,
            white_wins=0,
            draws=0,
            black_wins=0,
            average_elo=0,
            average_year=0,
            turn=True,
            fen=board.fen()
        )
        self.positions[initial_pos_id] = initial_position
        return initial_position

    def load_games(self):
        for filename in os.listdir(os.path.dirname(__file__) + self.folder):
            if os.path.splitext(filename)[1] == '.pgn':
                file = os.path.dirname(__file__) + os.path.join(self.folder, filename)
                self.load_file(file)
        self.set_final_positions()
        return self.initial_pos

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

                board: chess.Board = chess.Board()

                prev_position = self.initial_pos

                self.update_initial_position(white_wins, draws, black_wins, elo_white, year)

                for move in game.mainline_moves():
                    if board.ply() > self.max_moves:
                        break

                    move_san = board.san(move)
                    board.push(move)
                    turn = board.turn

                    move = prev_position.add_move(move_san)

                    pos_id: str = str(zobrist_hash(board=board))

                    position = self.set_position(pos_id, white_wins, draws, black_wins, elo_white, elo_black, year,
                                                 turn, board)

                    move.next_position = position

                    prev_position = position

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
            return position
        else:
            position = Position(
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
            self.positions[pos_id] = position
            return position

    def update_initial_position(self, white_wins, draws, black_wins, elo_white, year):
        self.initial_pos.total_games += 1
        self.initial_pos.white_wins += white_wins
        self.initial_pos.draws += draws
        self.initial_pos.black_wins += black_wins
        self.initial_pos.average_elo += elo_white
        self.initial_pos.average_year += year

    def set_final_positions(self):
        self.remove_least_played_moves(self.initial_pos)

        self.visited = {}

        self.set_final_position_values(self.initial_pos)

    def set_final_position_values(self, position):
        if position.pos_id in self.visited:
            return
        self.visited[position.pos_id] = position.pos_id
        position.set_final_values()
        for move in position.next_moves:
            self.set_final_position_values(move.next_position)

    def remove_least_played_moves(self, position):
        if position.pos_id in self.visited:
            return
        self.visited[position.pos_id] = position.pos_id
        moves = [move for move in position.next_moves if move.played > 10 and move.next_position.total_games > 10]
        position.next_moves = moves
        for move in moves:
            self.remove_least_played_moves(move.next_position)
