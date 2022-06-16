import logging
import os
import time
from typing import List

import chess.pgn

from opening_generator.models.game_pgn import GamePgn
from opening_generator.tree.opening_tree import OpeningTree


class TreeLoader:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.folder = "/../../data/pgn/"
        self.opening_tree = OpeningTree()
        self.max_moves = 30

    def load_games(self):
        for filename in os.listdir(os.path.dirname(__file__) + self.folder):
            if os.path.splitext(filename)[1] == '.pgn':
                file = os.path.dirname(__file__) + os.path.join(self.folder, filename)
                self.load_file(file)
        self.opening_tree.save_moves()
        return self.opening_tree

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

                line: List[str] = []
                moves = game.mainline_moves()
                board: chess.Board = chess.Board()
                for move in moves:
                    if board.ply() > self.max_moves:
                        break
                    move_uci = board.uci(move)
                    line.append(move_uci)
                    board.push(move)

                self.opening_tree.add_variant(GamePgn(line=line, result=result, elo_black=elo_black,
                                                      elo_white=elo_white, year=year))
        self.logger.info("Loaded %s in %f seconds.", filename, time.time() - start)
