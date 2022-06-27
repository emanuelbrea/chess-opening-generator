import logging
import os
import time

import chess.pgn
from chess.polyglot import zobrist_hash

from opening_generator.models import Position, Move


class PositionLoaderService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.folder = "/../../data/pgn/"
        self.max_moves = 30
        self.total_games = 0
        self.positions = {}
        self.final_positions = {}
        self.visited = {}
        self.next_moves = {}
        self.initial_pos = self.set_initial_position()

    def set_initial_position(self):
        board: chess.Board = chess.Board()
        initial_pos_id: str = str(zobrist_hash(board=board))
        initial_position = dict(
            pos_id=initial_pos_id,
            total_games=0,
            white_wins=0,
            draws=0,
            black_wins=0,
            average_elo=0,
            average_year=0,
            performance=0,
            turn=True,
            fen=board.fen()
        )
        self.positions[initial_pos_id] = initial_position
        self.next_moves[initial_pos_id] = []
        return initial_position

    def load_games(self):
        for filename in os.listdir(os.path.dirname(__file__) + self.folder):
            if os.path.splitext(filename)[1] == '.pgn':
                file = os.path.dirname(__file__) + os.path.join(self.folder, filename)
                self.load_file(file)
        self.set_final_positions()
        return self.final_positions

    def load_file(self, filename: str):
        self.logger.info("About to read %s", filename)
        board: chess.Board = chess.Board()
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

                prev_position = self.initial_pos['pos_id']

                self.update_initial_position(white_wins, draws, black_wins, elo_white, elo_black, year)

                for move in game.mainline_moves():
                    if board.ply() > self.max_moves:
                        break

                    move_san = board.san(move)
                    board.push(move)
                    turn = board.turn

                    next_moves = self.next_moves[prev_position]
                    move = next((move_dict for move_dict in next_moves if move_dict['move'] == move_san), None)

                    if move is None:
                        move = dict(move=move_san, pos_id=None, played=1)
                        next_moves.append(move)

                    else:
                        move['played'] += 1

                    if move.get('pos_id') is not None:  # move has next position
                        next_position = self.positions[move['pos_id']]
                        next_position['total_games'] += 1
                        next_position['white_wins'] += white_wins
                        next_position['draws'] += draws
                        next_position['black_wins'] += black_wins
                        if not turn:
                            next_position['average_elo'] += elo_white
                            next_position['performance'] += elo_black
                        else:
                            next_position['average_elo'] += elo_black
                            next_position['performance'] += elo_white
                        next_position['average_year'] += year
                        prev_position = next_position['pos_id']

                    else:  # move does not have next position yet
                        pos_id: str = str(zobrist_hash(board=board))

                        if pos_id not in self.positions:
                            position = dict(
                                pos_id=pos_id,
                                total_games=1,
                                white_wins=white_wins,
                                draws=draws,
                                black_wins=black_wins,
                                average_elo=elo_white if not turn else elo_black,
                                performance=elo_white if turn else elo_black,
                                average_year=year,
                                turn=turn,
                                fen=board.fen()
                            )
                            self.positions[pos_id] = position
                            self.next_moves[pos_id] = []

                        move['pos_id'] = pos_id
                        prev_position = pos_id

                board.reset()
                self.total_games += 1
                if self.total_games % 10000 == 0:
                    self.logger.info("Games: %d ", self.total_games)
                    self.logger.info("Positions: %d ", len(self.positions))
        self.logger.info("Loaded %s in %f seconds.", filename, time.time() - start)

    def update_initial_position(self, white_wins, draws, black_wins, elo_white, elo_black, year):
        self.initial_pos['total_games'] += 1
        self.initial_pos['white_wins'] += white_wins
        self.initial_pos['draws'] += draws
        self.initial_pos['black_wins'] += black_wins
        self.initial_pos['average_elo'] += elo_white
        self.initial_pos['performance'] += elo_black
        self.initial_pos['average_year'] += year

    def set_final_positions(self):
        self.remove_least_played_moves(self.initial_pos)

        self.visited = {}

        self.set_final_position_values(self.initial_pos['pos_id'])

        self.visited = {}

        self.positions = {}

        self.next_moves = {}

    def convert_position(self, position):
        return Position(
            pos_id=position['pos_id'],
            total_games=position['total_games'],
            white_wins=position['white_wins'],
            draws=position['draws'],
            black_wins=position['black_wins'],
            average_elo=position['average_elo'],
            average_year=position['average_year'],
            performance=position['performance'],
            turn=position['turn'],
            fen=position['fen']
        )

    def set_final_position_values(self, pos_id):
        if pos_id in self.visited:
            return
        self.visited[pos_id] = True
        position = self.convert_position(self.positions[pos_id])
        self.final_positions[pos_id] = position
        self.positions[pos_id] = {}
        next_moves = [Move(next_pos_id=move['pos_id'], move_san=move['move'], played=move['played']) for move in
                      self.next_moves[position.pos_id]]
        position.next_moves = next_moves
        position.set_final_values()
        for move in next_moves:
            self.set_final_position_values(move.next_pos_id)

    def remove_least_played_moves(self, position):
        if position['pos_id'] in self.visited:
            return
        self.visited[position['pos_id']] = True
        next_moves = self.next_moves[position['pos_id']]
        moves = [move for move in next_moves if
                 move['played'] > 10 and self.positions[move['pos_id']]['total_games'] > 10]
        self.next_moves[position['pos_id']] = moves
        for move in moves:
            self.remove_least_played_moves(self.positions[move['pos_id']])
