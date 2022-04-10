import csv
import os
import time
from typing import Optional, List

import chess.pgn
from chess.polyglot import zobrist_hash

from position import Position

FOLDER = "data/pgn/"
VALID_RESULTS = ["1-0", "0-1", "1/2-1/2"]
SAVE_FILE = "book.csv"
MAX_MOVES = 10


class Pgn:
    __instance = None

    def __init__(self, max_moves: Optional[int] = MAX_MOVES, folder: Optional[str] = FOLDER,
                 save_file: Optional[str] = SAVE_FILE):

        if Pgn.__instance is not None:
            raise Exception("Can't create another PGN.")

        self.max_moves = max_moves
        self.book = {}
        self.folder = folder
        self.save_file = save_file
        self.total_games: int = 0
        self.load_games()
        self.save_book_to_file()
        self.load_book_from_file()
        Pgn.__instance = self

    def load_games(self):
        for filename in os.listdir(self.folder):
            file = os.path.join(self.folder, filename)
            self.load_file(file)

    def load_file(self, filename: str):
        pgn = open(filename)
        start = time.time()
        while True:
            game: chess.pgn.Game = chess.pgn.read_game(pgn)

            if game is None:
                break
            self.total_games += 1
            board: chess.Board = game.board()
            result: str = game.headers.get("Result")
            elo_white: int = int(game.headers.get("WhiteElo", 0))
            elo_black: int = int(game.headers.get("BlackElo", 0))
            date: str = game.headers.get("Date")

            try:
                year: int = int(date.split(".")[0]) if date is not None else None
            except ValueError:
                year = None

            if result is None or result not in VALID_RESULTS:
                continue
            previous_key = None

            for move in game.mainline_moves():
                if board.fullmove_number > self.max_moves:
                    break
                turn = board.turn
                board.push(move)
                fen_key: int = zobrist_hash(board=board)
                if fen_key in self.book:
                    entry: Position = self.book[fen_key]
                    if result == "1-0":
                        entry.white_wins += 1
                    elif result == "0-1":
                        entry.black_wins += 1
                    elif result == "1/2-1/2":
                        entry.draws += 1
                    entry.total_games += 1
                    if year is not None and year > entry.year:
                        entry.year = year
                    if turn:
                        entry.elo = elo_white
                    else:
                        entry.elo = elo_black
                else:
                    entry: Position = Position(white_wins=1 if result == "1-0" else 0,
                                               black_wins=1 if result == "0-1" else 0,
                                               draws=1 if result == "1/2-1/2" else 0,
                                               elo=elo_white if turn else elo_black,
                                               year=year
                                               )
                    self.book[fen_key] = entry

                if previous_key is not None:
                    previous_entry: Position = self.book[previous_key]
                    previous_entry.add_move(move)
                previous_key = fen_key
        print(
            f"Loaded {filename} in {time.time() - start} seconds with {len(self.book)} positions for"
            f" {self.total_games} games.")

    def save_book_to_file(self):
        with open(self.save_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for key, entry in self.book.items():
                # if entry.total_games < len(self.book) * 0.001:
                #     continue
                writer.writerow(
                    [key,
                     entry.total_games,
                     entry.white_wins,
                     entry.draws,
                     entry.black_wins,
                     entry.year,
                     entry.final_elo(),
                     " ".join(move.uci() for move in entry.next_moves)
                     ])

    def load_book_from_file(self):
        start = time.time()
        with open(self.save_file) as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                key = int(row[0])
                moves: List[chess.Move] = [] if not row[7] or row[7].isspace() else [chess.Move.from_uci(uci) for uci in
                                                                                     row[7].split(" ")]
                entry: Position = Position(
                    total_games=int(row[1]),
                    white_wins=int(row[2]),
                    black_wins=int(row[3]),
                    draws=int(row[4]),
                    year=int(row[5]),
                    elo=int(row[6])
                )
                entry.next_moves = moves
                self.book[key] = entry
        print(f"Loaded {len(self.book)} entries in {time.time() - start} seconds.")

    def load_position_from_book(self, board: chess.Board):
        key = zobrist_hash(board=board)
        try:
            entry = self.book[key]
        except KeyError:
            print("Position not found in book")
            return None

        return entry

    @staticmethod
    def get_instance():
        if Pgn.__instance is None:
            Pgn()
        return Pgn.__instance
