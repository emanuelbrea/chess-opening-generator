from typing import List

from opening_generator.db import db_session
from opening_generator.models import Move
from opening_generator.models.game_pgn import GamePgn
from opening_generator.tree.opening_move import OpeningMove


class OpeningTree:

    def __init__(self):
        self.root = OpeningMove(None, None)

    def get_variation(self, moves: List[str]):
        return self.root.get_variation(moves)

    def add_variant(self, line: GamePgn):
        return self.root.add_variant(line)

    def save_moves(self):
        return self.root.save_moves()

    def retrieve_initial_position(self):
        initial_position = db_session.query(Move).filter(Move.move == None).one()
        self.root.set_move(initial_position)

