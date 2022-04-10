from typing import List

import chess


class Position:

    def __init__(self, white_wins, black_wins, draws, elo, year, total_games=1):
        self.total_games: int = total_games
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

    def final_elo(self):
        return self._elo // self._total_ranked_games if self._elo > 0 else 0

    def add_move(self, new_move: chess.Move):
        if new_move not in self.next_moves:
            self.next_moves.append(new_move)

