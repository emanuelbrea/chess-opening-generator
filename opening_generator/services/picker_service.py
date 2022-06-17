import logging
import random
from typing import List

import pandas as pd

from opening_generator.models import User, Move
from opening_generator.services.opening_tree_service import opening_tree_service


class PickerService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def pick_move(self, turn: bool, current_position: Move, popularity: float = 0,
                  risk: float = 0,
                  fashion: float = 0) -> Move:

        position_stats: pd.DataFrame = opening_tree_service.get_stats_as_df(current_position)

        if len(position_stats) == 0:
            return None

        position_stats = self.calculate_popularity(position_stats, 0)

        position_stats = position_stats.loc[position_stats['popularity_weight'] > 0.2, :]

        position_stats = position_stats.nlargest(5, 'total_games')

        position_stats = self.calculate_popularity(position_stats, popularity)

        position_stats = self.calculate_fashion(position_stats, fashion)

        position_stats = self.calculate_rating(position_stats)

        position_stats = self.calculate_winning_rate(position_stats, risk, turn)

        position_stats = self.calculate_total_weight(position_stats)

        choices = random.choices(position_stats['move'].tolist(), position_stats['weight'].tolist(), k=1)

        move = choices[0]

        variation: Move = current_position.get_next_move(move)

        return variation

    def calculate_floor(self, current_depth, user: User):

        depth = self.get_depth(user)
        floor = current_depth // 2 + 1 * 0.05 - depth / 100

        return floor if 0 < floor < 0.2 else 0.2

    def pick_oponent_moves(self, current_position: Move, current_depth, user: User):

        position_stats: pd.DataFrame = opening_tree_service.get_stats_as_df(current_position)

        if len(position_stats) == 0:
            return []

        floor: float = self.calculate_floor(current_depth, user)

        position_stats = self.calculate_popularity(position_stats, 0)

        position_stats = position_stats.loc[position_stats['popularity_weight'] > floor, :]

        moves = opening_tree_service.get_next_moves(current_position, position_stats['move'].tolist())

        return moves

    def pick_variation(self, current_position: Move, color: bool, user: User, depth: int, current_depth: int = 0):
        moves = []
        if current_depth > depth:
            if current_position.color == color:
                return []
            return [current_position]
        if current_position.color == color:
            rival_moves: List[Move] = self.pick_oponent_moves(current_position=current_position, user=user,
                                                              current_depth=current_depth)
            for move in rival_moves:
                moves.append(move)
                moves += self.pick_variation(move, color, user, depth, current_depth)
        else:
            current_depth += 1
            my_move = self.pick_move(color, current_position, user.style.popularity, user.style.risk,
                                     user.style.fashion)
            if my_move is not None:
                moves.append(my_move)
                moves += self.pick_variation(my_move, color, user, depth, current_depth)
        return moves

    def format_results(self, lines: List):
        for line in lines:
            if not any(isinstance(el, list) for el in line):
                line[:] = [line]
                print(line)
            else:
                self.format_results(line)
        return lines

    def calculate_popularity(self, position_stats, popularity):
        """
        :param position_stats:
        :param popularity: -1 if side line, 0 neutral, 1 popular moves
        :return:
        """
        position_stats['popularity_weight'] = (0.5 * popularity + 1) * \
                                              position_stats['total_games'] / position_stats['total_games'].sum()
        return position_stats

    def calculate_fashion(self, position_stats, fashion):
        min_year = 1970
        position_stats['average_year'] = position_stats['average_year'] - min_year
        position_stats['fashion_weight'] = (0.5 * fashion + 1) * \
                                           position_stats['average_year'] / position_stats['average_year'].sum()
        return position_stats

    def calculate_rating(self, position_stats):
        min_rating = 2300
        position_stats['average_elo'] = position_stats['average_elo'] - min_rating
        position_stats['rating_weight'] = position_stats['average_elo'] / position_stats['average_elo'].sum()
        return position_stats

    def calculate_winning_rate(self, position_stats, risk, turn):
        """
        :param position_stats:
        :param risk: -1 if aggressive, 0 neutral, 1 solid
        :param turn: true if white to move, false if black to move
        :return:
        """
        color = 'white_wins' if turn else 'black_wins'
        position_stats['winning_rate'] = (position_stats[color] + (0.5 * position_stats['draws'] * (0.5 * risk + 1))) \
                                         / position_stats['total_games']
        position_stats['winning_weight'] = position_stats['winning_rate'] / position_stats['winning_rate'].sum()
        return position_stats

    def calculate_total_weight(self, position_stats):
        position_stats['weight'] = position_stats['popularity_weight'] * 1.5 * position_stats['fashion_weight'] * \
                                   position_stats['rating_weight'] * position_stats['winning_weight']

        position_stats['weight'] = position_stats['weight'] / position_stats['weight'].sum()
        return position_stats

    def get_depth(self, user):
        rating = user.rating
        if not rating or rating < 1500:
            return 4
        if rating < 1700:
            return 5
        if rating < 1900:
            return 6
        if rating < 2100:
            return 7
        return 8


picker_service = PickerService()
