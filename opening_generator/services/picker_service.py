import random
from typing import List, Dict

import chess
import pandas as pd

from opening_generator.models import User
from opening_generator.models.line import Line
from opening_generator.services.line_service import line_service


class PickerService:

    def pick_variations(self, board: chess.Board, current_position: Line, color: bool, user: User):
        if board.turn == color:
            my_move: Dict[str, str] = self.pick_moves(board=board, current_position=current_position, count=1,
                                                      popularity=user.style.popularity,
                                                      fashion=user.style.fashion,
                                                      risk=user.style.risk)
            board.push_uci(list(my_move.values())[0])
            current_position: Line = line_service.get_line_by_id(line_id=list(my_move.keys())[0])
        results = self.pick_variation(board=board, current_position=current_position, user=user,
                                      depth=self.get_depth(user))
        results = self.format_results(results, board)
        return results

    def pick_moves(self, board: chess.Board, current_position: Line, count: int = 1, popularity: float = 0,
                   risk: float = 0,
                   fashion: float = 0):

        position_stats: pd.DataFrame = line_service.get_next_positions_as_df(current_position)

        if len(position_stats) == 0:
            return None

        position_stats = position_stats.nlargest(5, 'total_games')

        lines_id = {line.next_line_id: line.move for line in current_position.next_moves}

        position_stats = self.calculate_popularity(position_stats, popularity)

        position_stats = self.calculate_fashion(position_stats, fashion)

        position_stats = self.calculate_rating(position_stats)

        position_stats = self.calculate_winning_rate(position_stats, risk, board.turn)

        position_stats = self.calculate_total_weight(position_stats)

        choices = random.choices(position_stats['line_id'].tolist(), position_stats['weight'].tolist(), k=count)

        results = {move: lines_id[move] for move in set(choices)}

        return results

    def pick_variation(self, board: chess.Board, current_position: Line, user: User, depth: int):
        results = []
        if not current_position.eco_code and board.fullmove_number > depth:
            return board.move_stack
        rival_moves: Dict[str, str] = self.pick_moves(board=board, current_position=current_position, count=5,
                                                      popularity=user.style.popularity,
                                                      fashion=user.style.fashion,
                                                      risk=user.style.risk)
        if rival_moves is None:
            return board.move_stack
        for line_id, move in rival_moves.items():

            new_board = board.copy()
            new_board.push_uci(move)
            current_position: Line = line_service.get_line_by_id(line_id=line_id)

            if current_position is None:
                return new_board.move_stack
            my_move: Dict[str, str] = self.pick_moves(board=new_board, current_position=current_position, count=1,
                                                      popularity=user.style.popularity,
                                                      fashion=user.style.fashion,
                                                      risk=user.style.risk)
            if my_move is None:
                return new_board.move_stack

            new_board.push_uci(list(my_move.values())[0])
            current_position: Line = line_service.get_line_by_id(line_id=list(my_move.keys())[0])
            if current_position is None:
                return new_board.move_stack

            results.append(self.pick_variation(new_board, current_position, user, depth))
        return results

    def format_results(self, lines: List, board: chess.Board):
        if board.move_stack:
            board.pop()
        for line in lines:
            if not any(isinstance(el, list) for el in line):
                line[:] = [board.variation_san(line)]
                print(line)
            else:
                self.format_results(line, board)
        return lines

    def calculate_popularity(self, position_stats, popularity):
        """
        :param position_stats:
        :param popularity: -1 if side line, 0 neutral, 1 popular moves
        :return:
        """
        position_stats['popularity_weight'] = (0.5 * popularity + 1.5) * \
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
            return 5
        if rating < 1700:
            return 6
        if rating < 1900:
            return 7
        if rating < 2100:
            return 8
        return 9


picker_service = PickerService()
