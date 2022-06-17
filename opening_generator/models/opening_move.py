from typing import List

from opening_generator.db import db_session
from opening_generator.models import Move


class OpeningMove:

    def __init__(self, move, color):
        self.move = move
        self.color = color
        self.total_games = 0
        self.white_wins = 0
        self.draws = 0
        self.black_wins = 0
        self.average_elo = 0
        self.average_year = 0
        self.next_moves: List[OpeningMove] = []

    def has_next_move(self, move_str):
        for move in self.next_moves:
            if move.move == move_str:
                return True
        return False

    def add_next_move(self, move_str):
        if not self.has_next_move(move_str):
            if self.move:
                move = OpeningMove(move_str, not self.color)
            else:  # root
                move = OpeningMove(move_str, True)
            self.next_moves.append(move)

    def get_next_move(self, move_str):
        for move in self.next_moves:
            if move.move == move_str:
                return move
        return None

    def add_variant(self, line, result, elo_black, elo_white, year):
        self.total_games += 1
        if result == "1-0":
            self.white_wins += 1
        elif result == "0-1":
            self.black_wins += 1
        else:
            self.draws += 1

        if self.color:
            self.average_elo += elo_white
        else:
            self.average_elo += elo_black
        self.average_year += year

        if len(line) == 0:
            return
        self.add_next_move(line[0])
        next_move = self.get_next_move(line.pop(0))
        next_move.add_variant(line, result, elo_black, elo_white, year)

    def set_final_elo(self):
        self.average_elo = self.average_elo // self.total_games

    def set_final_year(self):
        self.average_year = self.average_year // self.total_games

    def save_moves(self):
        if self.total_games < 10:
            return None
        next_moves_ids = []
        for move in self.next_moves:
            next_move_id = move.save_moves()
            if next_move_id:
                next_moves_ids.append(next_move_id)

        self.set_final_year()
        self.set_final_elo()
        move_db = Move(move=self.move,
                       color=self.color,
                       total_games=self.total_games,
                       white_wins=self.white_wins,
                       draws=self.draws,
                       black_wins=self.black_wins,
                       average_elo=self.average_elo,
                       average_year=self.average_year)
        db_session.add(move_db)
        move_db.next_moves = next_moves_ids
        db_session.commit()

        return move_db
