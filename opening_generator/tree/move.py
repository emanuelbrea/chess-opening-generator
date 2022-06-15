from typing import List

from opening_generator.models.game_pgn import GamePgn


class Move:

    def __init__(self, move, color):
        self.move = move
        self.color = color
        self.total_games = 0
        self.white_wins = 0
        self.draws = 0
        self.black_wins = 0
        self.average_elo = 0
        self.average_year = 0
        self.next_moves: List[Move] = []

    def has_next_move(self, move_str):
        for move in self.next_moves:
            if move.move == move_str:
                return True
        return False

    def add_next_move(self, move_str):
        if not self.has_next_move(move_str):
            move = Move(move_str, not self.color)
            self.next_moves.append(move)

    def get_next_move(self, move_str):
        for move in self.next_moves:
            if move.move == move_str:
                return move
        return None

    def get_variation(self, moves: List[str]):
        if len(moves) == 0:
            return self
        next_move = self.get_next_move(moves.pop(0))
        return next_move.get_variation(moves)

    def add_variant(self, line: GamePgn):
        self.total_games += 1
        if line.result == "1-0":
            self.white_wins += 1
        elif line.result == "0-1":
            self.black_wins += 1
        else:
            self.draws += 1
        if self.color:
            self.average_elo += line.elo_white
        else:
            self.average_elo += line.elo_black
        self.average_year += line.year

        moves = line.line
        if len(moves) == 0:
            return
        self.add_next_move(moves[0])
        next_move = self.get_next_move(moves.pop(0))
        next_move.add_variant(line)

    def set_final_elo(self):
        self.average_elo = self.average_elo // self.total_games

    def set_final_year(self):
        self.average_year = self.average_year // self.total_games
