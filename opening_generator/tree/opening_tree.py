from typing import Dict, List

from opening_generator.models.game_pgn import GamePgn
from opening_generator.tree.move import Move


class OpeningTree:

    def __init__(self):
        self.nodes: Dict[str, Move] = {}

    def get_node(self, move_str):
        return self.nodes.get(move_str)

    def has_node(self, move_str):
        return self.nodes.get(move_str) is not None

    def add_node(self, move_str):
        if not self.has_node(move_str):
            move = Move(move_str, True)
            self.nodes[move_str] = move
            return Move
        return None

    def get_variation(self, moves: List[str]):
        node = self.get_node(moves.pop(0))
        if node:
            node.get_variation(moves)
        return None

    def add_variant(self, line: GamePgn):
        moves = line.line
        self.add_node(moves[0])
        node = self.get_node(moves.pop(0))
        return node.add_variant(line)
