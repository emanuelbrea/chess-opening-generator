import logging
import random
from typing import Dict

from opening_generator.models import Move, Position

MIN_YEAR = 1970
MIN_RATING = 2300


class PickerService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def pick_variations(self, position, user, color):
        depth = self.get_depth(user)
        moves = self.pick_variation(position, user, color, depth, 0)
        moves = list(set(moves))
        return moves

    def pick_variation(self, position, user, color, depth, current_depth):
        if current_depth == depth:
            return []
        moves = []
        if position.turn == color:
            current_depth += 1
            my_move: Move = self.pick_move(position, user, color, depth, current_depth)
            if my_move is not None:
                moves.append(my_move)
                moves += self.pick_variation(my_move.next_position, user, color, depth, current_depth)
        else:
            rival_moves = self.pick_rival_moves(position, depth, current_depth)
            for move in rival_moves:
                moves.append(move)
                moves += self.pick_variation(move.next_position, user, color, depth, current_depth)
        return moves

    def pick_move(self, position: Position, user, color, depth, current_depth=5):
        popularity = user.style.popularity
        fashion = user.style.fashion
        risk = user.style.risk

        year_sum = 0
        rating_sum = 0
        winning_rate_sum = 0

        next_moves = position.next_moves

        candidates = {}

        floor = self.calculate_floor(depth, current_depth)

        floor = (0.5 * popularity + 1) * floor

        for move in next_moves:
            if move.popularity_weight < floor:
                continue
            next_position: Position = move.next_position

            if color:
                winning_rate = next_position.white_wins + (0.5 * next_position.draws * (0.5 * risk + 1)) \
                               / next_position.total_games
            else:
                winning_rate = next_position.black_wins + (0.5 * next_position.draws * (0.5 * risk + 1)) \
                               / next_position.total_games
            if winning_rate == 0:
                continue
            rating_sum += next_position.average_elo - MIN_RATING
            year_sum += next_position.average_year - MIN_YEAR
            winning_rate_sum += winning_rate
            candidates[move] = winning_rate

        if len(candidates) == 0:
            return None

        move_weights: Dict[Move, (float, float)] = {}

        for move, winning_rate in candidates.items():
            next_position: Position = move.next_position
            fashion_weight = (0.5 * fashion + 1) * (next_position.average_year - MIN_YEAR) / year_sum
            rating_weight = (next_position.average_elo - MIN_RATING) / rating_sum
            winning_rate_weight = winning_rate / winning_rate_sum

            move_weights[move] = move.popularity_weight * fashion_weight * rating_weight * winning_rate_weight

        choices = random.choices(list(move_weights.keys()), move_weights.values(), k=1)

        move = choices[0]

        return move

    def pick_rival_moves(self, position: Position, depth: int, current_depth: int):
        floor = self.calculate_floor(depth, current_depth)
        next_moves = position.next_moves

        moves = []
        for move in next_moves:
            if move.popularity_weight >= floor:
                moves.append(move)
        return moves

    def calculate_floor(self, depth: int, current_depth: int):
        floor = current_depth * 0.05 - depth / 100
        if floor < 0.05:
            return 0.05
        if floor > 0.2:
            return 0.2
        return floor

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
