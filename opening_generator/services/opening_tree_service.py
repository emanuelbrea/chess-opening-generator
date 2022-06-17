from typing import List

import pandas as pd
from sqlalchemy.exc import NoResultFound

from opening_generator.db.move_dao import move_dao
from opening_generator.models import Move
from opening_generator.services.tree_loader_service import TreeLoaderService


class OpeningTreeService:

    def __init__(self):
        self.root: Move = self.retrieve_initial_position()

    def get_variation(self, moves: List[str]) -> Move:
        return self.root.get_variation(moves)

    def retrieve_initial_position(self) -> Move:
        try:
            initial_position = move_dao.get_initial_position()
        except NoResultFound:
            tree_loader = TreeLoaderService()
            tree_loader.load_games()
            initial_position = move_dao.get_initial_position()
        return initial_position

    def get_stats_as_df(self, move: Move):
        next_moves = []
        for next_move in move.next_moves:
            next_moves.append([next_move.move, next_move.total_games, next_move.white_wins, next_move.draws,
                               next_move.black_wins, next_move.average_year, next_move.average_elo])
        df = pd.DataFrame(next_moves, columns=['move', 'total_games', 'white_wins', 'draws', 'black_wins',
                                               'average_year', 'average_elo'])
        return df

    def get_next_moves(self, current_position: Move, moves: List[str]) -> List[Move]:

        result = []
        for move in moves:
            next_move = current_position.get_next_move(move)
            if next_move is not None:
                result.append(next_move)

        return result


opening_tree_service = OpeningTreeService()
