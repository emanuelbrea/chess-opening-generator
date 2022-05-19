import logging
import os
import time
from typing import Optional
import chess.pgn
from chess.polyglot import zobrist_hash

from opening_generator.db.line_dao import save_lines
from opening_generator.models.line import Line

FOLDER = "/../data/pgn/"
VALID_RESULTS = ["1-0", "0-1", "1/2-1/2"]
SAVE_FILE = "/../data/book.csv"
MAX_MOVES = 15


class Pgn:
    __instance = None

    def __init__(self, max_moves: Optional[int] = MAX_MOVES, folder: Optional[str] = FOLDER,
                 save_file: Optional[str] = SAVE_FILE):

        if Pgn.__instance is not None:
            self.logger.error("Can't create another PGN.")
            raise AssertionError("Can't create another PGN.")
        self.logger = logging.getLogger(__name__)
        self.max_moves = max_moves
        self.book = {}
        self.folder = folder
        self.save_file = save_file
        self.load_games()
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

                if result is None or result not in VALID_RESULTS:
                    self.logger.warning(f"Invalid result: {result} for game {game.headers.get('White')} vs "
                                        f"{game.headers.get('Black')}")
                    continue

                try:
                    year: int = int(date.split(".")[0]) if date is not None else None
                except ValueError:
                    year = 0

                previous_key = None
                for move in game.mainline_moves():
                    if board.fullmove_number > self.max_moves:
                        break
                    turn = board.turn
                    board.push(move)
                    fen_key: int = zobrist_hash(board=board)
                    if fen_key in self.book:
                        entry: Line = self.book[fen_key]
                        entry.total_games += 1
                        if result == "1-0":
                            entry.white_wins += 1
                        elif result == "0-1":
                            entry.black_wins += 1
                        else:
                            entry.draws += 1
                        if year > entry.last_year:
                            entry.last_year = year
                        if turn:
                            entry.add_elo(elo_white)
                        else:
                            entry.add_elo(elo_black)
                    else:
                        entry: Line = Line(white_wins=1 if result == "1-0" else 0,
                                           black_wins=1 if result == "0-1" else 0,
                                           draws=1 if result == "1/2-1/2" else 0,
                                           total_games=1,
                                           average_elo=elo_white if turn else elo_black,
                                           last_year=year,
                                           fen=board.fen(),
                                           line_id=str(fen_key)
                                           )
                        self.book[fen_key] = entry

                    if previous_key is not None:
                        previous_entry: Line = self.book[previous_key]
                        previous_entry.add_next_line(entry)
                    previous_key = fen_key

            self.logger.warning(
                f"Loaded {filename} in {time.time() - start} seconds with {len(self.book)} positions")

    def save_book_to_database(self):
        save_lines(self.book)
        self.book = {}

    def load_position_from_book(self, board: chess.Board):
        key = zobrist_hash(board=board)
        try:
            entry = self.book[key]
        except KeyError:
            self.logger.warning("Position not found in book.")
            return None

        return entry

    @staticmethod
    def get_instance():
        if Pgn.__instance is None:
            Pgn()
        return Pgn.__instance
