from typing import List

from opening_generator.db import db_session
from opening_generator.models import Move, NextMove
from opening_generator.models.game_pgn import GamePgn


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
            if self.move is None:  # root
                move = OpeningMove(move_str, True)
            else:
                move = OpeningMove(move_str, not self.color)
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

        if self.color is None:
            self.average_elo += line.elo_white
            self.average_elo += line.elo_black

        elif self.color:
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
        next_moves = [NextMove(move_id=move_db.move_id, next_move_id=next_id) for next_id in next_moves_ids]
        move_db.next_moves = next_moves
        db_session.commit()

        return move_db.move_id

    def set_move(self, move: Move):
        self.total_games = move.total_games
        self.white_wins = move.white_wins
        self.black_wins = move.black_wins
        self.draws = move.draws
        self.average_year = move.average_year
        self.average_elo = move.average_elo
        next_moves = move.next_moves
        for next_move in next_moves:
            opening_move = OpeningMove(next_move.move, next_move.color)
            self.next_moves.append(opening_move.set_move(next_move))
        return self