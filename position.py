from typing import List

import chess


class BookPosition:

    def __init__(self, white_wins: int, black_wins: int, draws: int, elo: int, year: int):
        self.white_wins: int = white_wins
        self.black_wins: int = black_wins
        self.draws: int = draws
        self._elo: int = elo
        self.year: int = year
        self._total_ranked_games: int = 1 if elo > 0 else 0
        self.next_moves: List[chess.Move] = []

    @property
    def elo(self):
        return self._elo

    @elo.setter
    def elo(self, new_elo: int):
        if new_elo > 0:
            self._elo += new_elo
            self._total_ranked_games += 1

    @property
    def white_percentage_win(self):
        return round((self.white_wins + 0.5 * self.draws) / self.total_games, 3)

    @property
    def total_games(self):
        return self.white_wins + self.draws + self.black_wins

    @property
    def final_elo(self):
        return self._elo // self._total_ranked_games if self._total_ranked_games > 0 else 0

    def add_move(self, new_move: chess.Move):
        if new_move not in self.next_moves:
            self.next_moves.append(new_move)


class Position:

    def __init__(self, total_games: int, white_percentage_win: float, elo: int, year: int,
                 next_moves: List[chess.Move]):
        self.total_games = total_games
        self.white_percentage_win = white_percentage_win
        self.elo = elo
        self.year = year
        self.next_moves = next_moves

    @classmethod
    def from_book(cls, book_position: BookPosition):
        return cls(total_games=book_position.total_games,
                   white_percentage_win=book_position.white_percentage_win,
                   elo=book_position.final_elo,
                   year=book_position.year,
                   next_moves=book_position.next_moves)

    @property
    def next_moves_str(self):
        return " ".join(move.uci() for move in self.next_moves)
