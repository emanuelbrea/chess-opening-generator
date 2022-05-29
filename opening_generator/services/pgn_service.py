import logging
import os
import time
from typing import Optional, List

import chess.pgn
from chess.polyglot import zobrist_hash

from opening_generator.models.game_pgn import GamePgn
from opening_generator.models.line import Line

FOLDER = "/../../data/pgn/"
VALID_RESULTS = ["1-0", "0-1", "1/2-1/2"]
MAX_MOVES = 30


class PgnService:

    def __init__(self, max_moves: Optional[int] = MAX_MOVES, folder: Optional[str] = FOLDER):
        self.logger = logging.getLogger(__name__)
        self.max_moves = max_moves
        self.folder = folder
        self.current_move = 0
        self.games: List[GamePgn] = []

    def load_games(self):
        for filename in os.listdir(os.path.dirname(__file__) + self.folder):
            if os.path.splitext(filename)[1] == '.pgn':
                file = os.path.dirname(__file__) + os.path.join(self.folder, filename)
                self.load_file(file)
        book = self.load_positions()
        return book

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

                try:
                    year: int = int(date.split(".")[0]) if date is not None else None
                except ValueError:
                    year = 0

                line: List[str] = []
                moves = game.mainline_moves()
                board: chess.Board = chess.Board()
                for move in moves:
                    if board.ply() > self.max_moves:
                        break
                    move_uci = board.uci(move)
                    line.append(move_uci)
                    board.push(move)

                self.games.append(GamePgn(line=line, result=result, elo_black=elo_black,
                                          elo_white=elo_white, year=year))

        self.logger.info(
            f"Loaded {filename} in {time.time() - start} seconds.")

    def load_positions(self):
        book = {}
        while self.current_move < self.max_moves:
            for game in list(self.games):
                previous_entry: Line = None
                board: chess.Board = chess.Board()
                for move in game.line:
                    if board.ply() > self.current_move:
                        break

                    if board.ply() < self.current_move:
                        board.push_uci(move)
                        if board.ply() == self.current_move:
                            previous_key: int = zobrist_hash(board=board)
                            previous_entry = book[previous_key]
                        continue

                    if board.ply() > 0:
                        fen_key: int = zobrist_hash(board=board)
                        if book[fen_key].total_games < 10:
                            self.games.remove(game)
                            break

                    turn = board.turn
                    board.push_uci(move)
                    fen_key: int = zobrist_hash(board=board)
                    if fen_key in book:
                        entry: Line = book[fen_key]
                        entry.total_games += 1
                        if game.result == "1-0":
                            entry.white_wins += 1
                        elif game.result == "0-1":
                            entry.black_wins += 1
                        else:
                            entry.draws += 1
                        if game.year > entry.last_year:
                            entry.last_year = game.year
                        if turn:
                            entry.add_elo(game.elo_white)
                        else:
                            entry.add_elo(game.elo_black)
                    else:
                        entry: Line = Line(white_wins=1 if game.result == "1-0" else 0,
                                           black_wins=1 if game.result == "0-1" else 0,
                                           draws=1 if game.result == "1/2-1/2" else 0,
                                           total_games=1,
                                           average_elo=game.elo_white if turn else game.elo_black,
                                           last_year=game.year,
                                           line_id=str(fen_key)
                                           )
                        book[fen_key] = entry
                    if previous_entry:
                        previous_entry.add_next_move(move)

            self.current_move += 1
            self.logger.info(f"Next move number: {self.current_move}")
            self.logger.info(f"Games in memory: {len(self.games)}")
        del self.games
        self.games = []
        return book


pgn_service = PgnService()
