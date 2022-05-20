import logging
import os
import time
from typing import Optional, List
import chess.pgn
from chess.polyglot import zobrist_hash

from opening_generator.db.line_dao import save_lines
from opening_generator.models.game_pgn import GamePgn
from opening_generator.models.line import Line

FOLDER = "/../../data/pgn/"
VALID_RESULTS = ["1-0", "0-1", "1/2-1/2"]
MAX_MOVES = 30


class Pgn:
    __instance = None

    def __init__(self, max_moves: Optional[int] = MAX_MOVES, folder: Optional[str] = FOLDER):

        if Pgn.__instance is not None:
            self.logger.error("Can't create another PGN.")
            raise AssertionError("Can't create another PGN.")

        self.logger = logging.getLogger(__name__)
        self.max_moves = max_moves
        self.book = {}
        self.folder = folder
        self.current_move = 0
        self.games: List[GamePgn] = []
        self.load_games()
        self.load_positions()
        self.save_book_to_database()
        Pgn.__instance = self

    def load_games(self):
        for filename in os.listdir(os.path.dirname(__file__) + self.folder):
            if os.path.splitext(filename)[1] == '.pgn':
                file = os.path.dirname(__file__) + os.path.join(self.folder, filename)
                self.load_file(file)

    def load_file(self, filename: str):
        start = time.time()
        with open(filename) as pgn:
            while True:
                game: chess.pgn.Game = chess.pgn.read_game(pgn)

                if not game:
                    break

                board: chess.Board = game.board()
                if board.fen() != chess.STARTING_FEN:
                    self.logger.warning(
                        f"Invalid initial position for game {game.headers.get('White')} vs {game.headers.get('Black')} "
                        f"on {game.headers.get('Date')} ")
                    continue

                result: str = game.headers.get("Result")
                elo_white: int = int(game.headers.get("WhiteElo", 0))
                elo_black: int = int(game.headers.get("BlackElo", 0))
                date: str = game.headers.get("Date")

                try:
                    year: int = int(date.split(".")[0]) if date is not None else None
                except ValueError:
                    year = 0

                self.games.append(GamePgn(line=game.mainline_moves(), result=result, elo_black=elo_black,
                                          elo_white=elo_white, year=year))

        self.logger.warning(
            f"Loaded {filename} in {time.time() - start} seconds.")

    def load_positions(self):
        while self.current_move < self.max_moves:
            for game in list(self.games):
                previous_entry: Line = None
                board: chess.Board = chess.Board()
                for move in game.line:
                    if board.ply() > self.current_move:
                        break

                    if board.ply() < self.current_move:
                        board.push(move)
                        if board.ply() == self.current_move:
                            previous_key: int = zobrist_hash(board=board)
                            previous_entry = self.book[previous_key]
                        continue

                    if board.ply() > 0:
                        fen_key: int = zobrist_hash(board=board)
                        if self.book[fen_key].total_games < 10:
                            self.games.remove(game)
                            break

                    turn = board.turn
                    board.push(move)
                    fen_key: int = zobrist_hash(board=board)
                    if fen_key in self.book:
                        entry: Line = self.book[fen_key]
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
                                           fen=board.fen(),
                                           line_id=str(fen_key)
                                           )
                        self.book[fen_key] = entry
                    if previous_entry:
                        previous_entry.add_next_line(entry)

            self.current_move += 1
            self.logger.warning(f"Next move number: {self.current_move}")
            self.logger.warning(f"Games in memory: {len(self.games)}")
        self.games = []


    def save_book_to_database(self):
        save_lines(self.book)
        self.book = {}

    @staticmethod
    def get_instance():
        if Pgn.__instance is None:
            Pgn()
        return Pgn.__instance
