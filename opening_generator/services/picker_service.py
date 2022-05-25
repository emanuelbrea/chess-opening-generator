import random
from typing import List, Dict

import chess

from opening_generator.db.line_dao import line_dao
from opening_generator.models.line import Line
from opening_generator.services.line_service import line_service


class PickerService:

    def pick_variations(self, board: chess.Board, current_position: Line, color: bool, popularity: int = 1):
        if board.turn == color:
            my_move: chess.Move = self.pick_moves(board, current_position, popularity)
            if not my_move:  # all moves lose
                return []
            board.push_uci(my_move)
            current_position: Line = line_dao.get_line_by_position(fen=board.fen())
        results = self.pick_variation(board, current_position)
        results = self.format_results(results, board)
        return results

    def pick_moves(self, board: chess.Board, current_position: Line, count: int = 1, popularity: float = 1):
        moves: List[str] = line_service.get_next_moves(line=current_position)
        candidates: Dict[str, Line] = {}
        move_weights = []
        max_rating = 0

        for move in list(moves):
            board.push_uci(move)
            position: Line = line_dao.get_line_by_position(fen=board.fen())
            board.pop()
            if not position:
                moves.remove(move)

            candidates[move] = position
            if position.average_elo > max_rating:
                max_rating = position.average_elo

        for move, position in candidates.items():
            if board.turn:
                winning_percentage_weight = (position.white_wins + 0.5 * position.draws) / position.total_games
            else:
                winning_percentage_weight = (position.black_wins + 0.5 * position.draws) / position.total_games

            popularity_weight = (position.total_games / current_position.total_games) * (0.5 * popularity + 1)

            # style_weight = (position.total_games / current_position.total_games) * (0.5 * popularity + 1)

            rating_weight = position.average_elo / max_rating

            weight = popularity_weight * winning_percentage_weight * rating_weight

            if weight == 0:  # lost all games
                moves.remove(move)
            else:
                move_weights.append(weight)

        if len(moves) == 0:
            return None

        choices = random.choices(moves, move_weights, k=count)

        return list(set(choices)) if count > 1 else choices[0]

    def pick_variation(self, board: chess.Board, current_position: Line, popularity: float = 1):
        results = []
        if not current_position.eco_code and board.fullmove_number > 6:
            return board.move_stack
        rival_moves: List[str] = self.pick_moves(board, current_position, 5, popularity)
        if rival_moves is None:
            return board.move_stack
        for move in rival_moves:
            new_board = board.copy()
            new_board.push_uci(move)
            current_position: Line = line_dao.get_line_by_position(fen=new_board.fen())
            if current_position is None:
                return new_board.move_stack

            my_move: str = self.pick_moves(new_board, current_position, popularity=popularity)
            if my_move is None:
                return new_board.move_stack

            new_board.push_uci(my_move)
            current_position: Line = line_dao.get_line_by_position(fen=new_board.fen())
            if current_position is None:
                return new_board.move_stack

            results.append(self.pick_variation(new_board, current_position))
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


picker_service = PickerService()
