import logging
import random
from typing import Dict

from opening_generator.models import Move, Position, User

MIN_YEAR = 1970
MAX_YEAR = 2022
MIN_RATING = 2300
DIFF_YEAR = MAX_YEAR - MIN_YEAR


class PickerService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.visited = {}

    def pick_variations(self, position, user, color, current_depth: int = 0):
        depth = self.get_depth(user)
        moves = self.pick_variation(position, user, color, depth, current_depth)
        moves = list(set(moves))
        self.visited = {}
        return moves

    def pick_variation(self, position, user, color, depth, current_depth):
        if position.pos_id in self.visited:
            return []
        self.visited[position.pos_id] = True
        moves = []
        if position.turn == color:
            if current_depth == depth:
                return []
            current_depth += 1
            my_move: Move = self.pick_move(position, user, color, depth, current_depth)
            if my_move is not None:
                moves.append(my_move)
                moves += self.pick_variation(
                    my_move.next_position, user, color, depth, current_depth
                )
        else:
            rival_moves = self.pick_rival_moves(position, depth, current_depth)
            for move in rival_moves:
                moves.append(move)
                moves += self.pick_variation(
                    move.next_position, user, color, depth, current_depth
                )
        return moves

    def pick_move(
        self,
        position: Position,
        user: User,
        color: bool,
        depth: int,
        current_depth: int = 5,
    ):
        popularity = user.style.popularity
        fashion = user.style.fashion
        risk = user.style.risk

        year_sum = 0
        popularity_sum = 0
        rating_sum = 0
        winning_rate_sum = 0

        next_moves = position.next_moves

        candidates = []

        floor = self.calculate_floor(depth, current_depth)

        floor = (0.5 * popularity + 1) * floor

        ref_year = MIN_YEAR if fashion <= 0 else MAX_YEAR

        for move in next_moves:
            if move.popularity_weight < floor:
                continue
            next_position: Position = move.next_position

            draws = next_position.draws * 100 / next_position.total_games

            if color:
                wins = next_position.white_wins * 100 / next_position.total_games
                loses = next_position.black_wins * 100 / next_position.total_games
            else:
                wins = next_position.black_wins * 100 / next_position.total_games
                loses = next_position.white_wins * 100 / next_position.total_games

            winning_rate = (wins + 0.5 * draws) ** 2
            if risk < 0:  # aggressive, minimize draws
                winning_rate *= (1 - draws / 100) ** (1 - risk)
            if risk > 0:  # solid, minimize loses
                winning_rate *= (1 - loses / 100) ** (1 + risk)
            winning_rate *= winning_rate
            if winning_rate == 0:
                continue

            winning_rate_sum += winning_rate

            year_weight = (
                (next_position.average_year - ref_year) / DIFF_YEAR * fashion + 1
            ) ** 2
            year_sum += year_weight

            rating_weight = ((next_position.average_elo - MIN_RATING) ** 2) + (
                next_position.performance - MIN_RATING
            ) ** 2
            rating_sum += rating_weight

            popularity_weight = move.popularity_weight ** (0.5 * popularity + 1)
            popularity_sum += popularity_weight

            candidate = (
                move,
                winning_rate,
                year_weight,
                popularity_weight,
                rating_weight,
            )
            candidates.append(candidate)

        if len(candidates) == 0:
            return None

        move_weights: Dict[Move, (float, float)] = {}

        for candidate in candidates:
            move = candidate[0]
            winning_rate = candidate[1]
            year_weight = candidate[2]
            popularity_weight = candidate[3]
            rating_weight = candidate[4]

            fashion_weight = year_weight / year_sum
            rating_weight = rating_weight / rating_sum
            winning_rate_weight = winning_rate / winning_rate_sum
            popularity_weight = popularity_weight / popularity_sum

            move_weights[move] = (
                popularity_weight * fashion_weight * rating_weight * winning_rate_weight
            )

        choices = random.choices(
            list(move_weights.keys()), list(move_weights.values()), k=1
        )

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
        rating = user.style.rating
        if rating < 1500:
            return 4
        if rating < 1700:
            return 5
        if rating < 1900:
            return 6
        if rating < 2100:
            return 7
        return 8


picker_service = PickerService()
