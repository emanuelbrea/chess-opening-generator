import logging
from typing import List, Dict

from opening_generator import Position, User, picker_service
from opening_generator.db.repertoire_dao import repertoire_dao
from opening_generator.models import Move


class RepertoireService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_repertoire_moves(self, position: Position, user: User, color: bool) -> Dict:
        next_moves = position.next_moves
        repertoire = next(repertoire for repertoire in user.repertoire if repertoire.color == color)
        repertoire_moves = repertoire.moves
        my_move = self.get_my_move(repertoire_moves, next_moves)
        if not my_move:
            return []

        next_position: Position = my_move.next_position
        my_move_stats = dict(move=my_move.move_san,
                             played=my_move.played,
                             total_games=next_position.total_games,
                             white_wins=next_position.white_wins,
                             draws=next_position.draws,
                             black_wins=next_position.black_wins,
                             average_rating=next_position.average_elo,
                             average_year=next_position.average_year,
                             fen=position.fen
                             )
        rival_moves = self.get_rival_moves(repertoire_moves, next_position.next_moves)
        rival_moves_stats = {}
        for move in rival_moves:
            next_position = move.next_position
            rival_moves_stats[move.move_san] = dict(move=move.move_san,
                                                    played=move.played,
                                                    total_games=next_position.total_games,
                                                    white_wins=next_position.white_wins,
                                                    draws=next_position.draws,
                                                    black_wins=next_position.black_wins,
                                                    average_rating=next_position.average_elo,
                                                    average_year=next_position.average_year,
                                                    fen=next_position.fen
                                                    )

        return dict(my_move=my_move_stats, rival_moves=rival_moves_stats)

    def get_my_move(self, repertoire_moves, next_moves) -> Move | None:
        for move in next_moves:
            if move in repertoire_moves:
                return move
        return None

    def get_rival_moves(self, repertoire_moves, next_moves) -> List[Move]:
        rival_moves = []
        for move in next_moves:
            if move in repertoire_moves:
                rival_moves.append(move)
        return rival_moves

    def create_user_repertoire(self, position, user):
        moves = picker_service.pick_variations(position, user, True)
        repertoire_dao.create_repertoire(user=user, color=True, moves=moves)
        moves = picker_service.pick_variations(position, user, False)
        repertoire_dao.create_repertoire(user=user, color=False, moves=moves)

    def update_user_repertoire(self, position, user, color, new_move, old_move):
        next_moves = position.next_moves
        old_move = next((move for move in next_moves if move.move_san == old_move), None)
        if not old_move:
            return []
        if not new_move:
            tries = 0
            new_move = picker_service.pick_move(position, user, color)
            while new_move is old_move:
                new_move = picker_service.pick_move(position, user, color)
                tries += 1
                if tries == 10:
                    return []
        else:
            new_move = next((move for move in next_moves if move.move_san == new_move), None)
            if not new_move:
                return []
        next_position = new_move.next_position
        moves = picker_service.pick_variations(next_position, user, color)
        moves.append(new_move)

        repertoire = next(repertoire for repertoire in user.repertoire if repertoire.color == color)
        repertoire_moves = repertoire.moves
        moves_to_remove = self.get_moves_after_position(repertoire_moves, old_move)
        repertoire_dao.delete_moves_from_repertoire(repertoire=repertoire, user=user, color=color,
                                                    moves=moves_to_remove)
        repertoire_dao.insert_new_moves(repertoire=repertoire, user=user, color=color,
                                        moves=moves)
        return moves

    def get_moves_after_position(self, repertoire_moves, move) -> List[Move]:
        moves = [move]
        next_position = move.next_position
        next_moves = next_position.next_moves
        rival_moves = self.get_rival_moves(repertoire_moves=repertoire_moves, next_moves=next_moves)
        moves += rival_moves
        for move in rival_moves:
            next_position = move.next_position
            next_moves = next_position.next_moves
            my_move = self.get_my_move(repertoire_moves=repertoire_moves, next_moves=next_moves)
            if my_move:
                moves += self.get_moves_after_position(repertoire_moves, my_move)

        return moves


repertoire_service = RepertoireService()
