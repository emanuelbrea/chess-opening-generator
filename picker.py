import random
from typing import List, Dict

import chess

from pgn import Pgn
from position import Position
import math


class Picker:

    def __init__(self, pgn: Pgn):
        self.pgn = pgn
        self.popularity = 1
        self.risk = 1

    def pick_variations(self, board: chess.Board, current_position: Position, color: bool, depth: int = 3):
        if board.turn == color:
            my_move: chess.Move = self.pick_moves(board, current_position)
            board.push(my_move)
            current_position: Position = self.pgn.load_position_from_book(board=board)
        results = self.pick_variation(board, current_position, depth=depth)
        self.print_lines(results, board)
        return results

    def pick_moves(self, board: chess.Board, current_position: Position, count: int = 1):
        moves: List[chess.Move] = current_position.next_moves
        candidates: Dict[chess.Move, Position] = {}
        move_weights = []
        turn = 1 if board.turn else -1

        for move in moves:
            board.push(move)
            candidates[move] = self.pgn.load_position_from_book(board=board)
            board.pop()

        for move, position in candidates.items():
            popularity_weight = (1 / math.sqrt(self.popularity)) * (position.total_games / current_position.total_games)
            risk_win_weight = (turn * position.white_wins / position.total_games) * (1 / math.sqrt(self.risk))
            risk_lose_weight = (turn * position.black_wins / position.total_games) * (math.sqrt(self.risk))
            weight = popularity_weight * (risk_win_weight - risk_lose_weight + 1)
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
        for line in lines:
            if not any(isinstance(el, list) for el in line):
                line[:] = [board.variation_san(line)]
            else:
                self.print_lines(line, board)
