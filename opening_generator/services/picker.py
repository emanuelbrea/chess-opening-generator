import math
import random
from typing import List, Dict

import chess
from opening_generator.db.pgn import Pgn
from opening_generator.services.position import Position


class Picker:

    def __init__(self, pgn: Pgn):
        self.pgn = pgn
        self.popularity = 1
        self.risk = 1

    def pick_variations(self, board: chess.Board, current_position: Position, color: bool, depth: int = 3):
        if board.turn == color:
            my_move: chess.Move = self.pick_moves(board, current_position)
            if not my_move:  # all moves lose
                return []
            board.push(my_move)
            current_position: Position = self.pgn.load_position_from_book(board=board)
        results = self.pick_variation(board, current_position, depth=depth)
        self.print_lines(results, board)
        return results

    def pick_moves(self, board: chess.Board, current_position: Position, count: int = 1):
        moves: List[chess.Move] = current_position.next_moves
        candidates: Dict[chess.Move, Position] = {}
        move_weights = []
        ratings = []

        for move in moves:
            board.push(move)
            position: Position = self.pgn.load_position_from_book(board=board)
            candidates[move] = position
            board.pop()
            if position.elo > 0:
                ratings.append(position.elo)

        rating_mean = sum(ratings) / len(ratings) if ratings else 0

        for move, position in candidates.items():
            winning_percentage_weight = position.white_percentage_win if board.turn \
                else 1 - position.white_percentage_win
            popularity_weight = (1 / math.sqrt(self.popularity)) * (position.total_games / current_position.total_games)
            winning_percentage_weight = winning_percentage_weight * (1 / math.sqrt(self.risk))
            rating_weight = position.elo / rating_mean if position.elo != 0 else 1
            weight = popularity_weight * winning_percentage_weight * rating_weight
            if weight == 0:  # lost all games
                moves.remove(move)
            else:
                move_weights.append(weight)

        if len(moves) == 0:
            return None

        choices = random.choices(moves, move_weights, k=count)

        return list(set(choices)) if count > 1 else choices[0]

    def pick_variation(self, board: chess.Board, current_position: Position, depth: int = 3):
        results = []
        if len(board.move_stack) >= depth * 2:
            return board.move_stack
        rival_moves: List[chess.Move] = self.pick_moves(board, current_position, 5)
        if rival_moves is None:
            return board.move_stack
        for move in rival_moves:
            new_board = board.copy()
            new_board.push(move)
            current_position: Position = self.pgn.load_position_from_book(board=new_board)
            if current_position is None:
                return new_board.move_stack

            my_move: chess.Move = self.pick_moves(new_board, current_position)
            if my_move is None:
                return new_board.move_stack

            new_board.push(my_move)
            current_position: Position = self.pgn.load_position_from_book(board=new_board)
            if current_position is None:
                return new_board.move_stack

            results.append(self.pick_variation(new_board, current_position, depth))
        return results

    def print_lines(self, lines: List, board: chess.Board):
        if board.move_stack:
            board.pop()
        for line in lines:
            if not any(isinstance(el, list) for el in line):
                line[:] = [board.variation_san(line)]
                print(line)
            else:
                self.print_lines(line, board)
