import logging
from typing import List, Dict

from opening_generator.db.repertoire_dao import repertoire_dao
from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import Move, Position, User, Repertoire
from opening_generator.services.picker_service import picker_service
from opening_generator.services.position_service import position_service


class RepertoireService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_user_repertoire(self, user: User, color: bool) -> Repertoire | InvalidRequestException:
        repertoire = next((repertoire for repertoire in user.repertoire if repertoire.color == color), None)
        if repertoire is None:
            color = "white" if color else "black"
            raise InvalidRequestException(description=f"User {user.email} does not have a {color} repertoire")
        return repertoire

    def get_repertoire_moves(self, position: Position, user: User, color: bool,
                             depth: int) -> Dict | InvalidRequestException:
        repertoire = self.get_user_repertoire(user=user, color=color)
        repertoire_moves = repertoire.moves

        if position.turn == color:
            next_moves = position.next_moves
            my_move: Move = self.get_my_move(repertoire_moves, next_moves)
            if not my_move:
                raise InvalidRequestException(description=f"Position with FEN {position.fen} is not in user "
                                                          f"{user.email} repertoire.")

            my_move_stats: Dict = position_service.get_move_stats(move=my_move)
            moves = []
            floor: float = picker_service.calculate_floor(current_depth=depth, depth=picker_service.get_depth(user))
            for move in next_moves:
                if move.popularity_weight >= floor:
                    moves.append(position_service.get_move_stats(move=move))
            my_moves_stats = sorted(moves, key=lambda d: d['played'], reverse=True)
            next_position: Position = my_move.next_position
        else:
            next_position: Position = position
            my_move_stats = {}
            my_moves_stats = {}

        position_stats: Dict = position_service.get_position_stats(position=position)

        rival_moves: List[Move] = self.get_rival_moves(repertoire_moves, next_position.next_moves)
        rival_moves_stats = []
        for move in rival_moves:
            rival_moves_stats.append(position_service.get_move_stats(move=move))
        rival_moves_stats = sorted(rival_moves_stats, key=lambda d: d['played'], reverse=True)

        return dict(position=position_stats, my_move=my_move_stats, my_moves=my_moves_stats,
                    rival_moves=rival_moves_stats, depth=depth)

    def get_my_move(self, repertoire_moves: List[Move], next_moves: List[Move]) -> Move | None:
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

    def create_user_repertoire(self, position: Position, user: User):
        self.logger.info("About to create both repertoires for user %s", user.email)
        moves: List[Move] = picker_service.pick_variations(position=position, user=user, color=True)
        repertoire_dao.create_repertoire(user=user, color=True, moves=moves)
        moves: List[Move] = picker_service.pick_variations(position=position, user=user, color=False)
        repertoire_dao.create_repertoire(user=user, color=False, moves=moves)
        self.logger.info("Created both repertoires for user %s", user.email)

    def update_user_repertoire(self, position: Position, user: User, color: bool, new_move: str):
        repertoire = self.get_user_repertoire(user=user, color=color)
        repertoire_moves = repertoire.moves
        next_moves = position.next_moves
        move_to_remove = self.get_my_move(repertoire_moves=repertoire_moves, next_moves=next_moves)
        if not move_to_remove:
            raise InvalidRequestException(description=f"Position with FEN {position.fen} is not in user {user.email} "
                                                      f"repertoire.")

        if not new_move:
            tries = 0
            depth = picker_service.get_depth(user)
            new_move = picker_service.pick_move(position=position, user=user, color=color, depth=depth)
            while new_move is move_to_remove:
                new_move = picker_service.pick_move(position=position, user=user, color=color, depth=depth)
                tries += 1
                if tries == 10:
                    raise InvalidRequestException(
                        description=f"Not able to find a good move to replace {move_to_remove.move_san}."
                                    f" Consider passing it manually.")
        else:
            new_move = next((move for move in next_moves if move.move_san == new_move), None)
            if not new_move:
                raise InvalidRequestException(description=f"Suggested move is not available in this position. Choose"
                                                          f" a different one.")
        next_position = new_move.next_position
        moves = picker_service.pick_variations(position=next_position, user=user, color=color, current_depth=1)
        moves.append(new_move)

        moves_to_remove = self.get_moves_after_position(repertoire=repertoire, move=move_to_remove)
        repertoire_dao.insert_new_moves(repertoire=repertoire, user=user, color=color,
                                        moves=moves, old_moves=moves_to_remove)
        return moves

    def get_moves_after_position(self, repertoire: Repertoire, move: Move) -> List[Move]:
        moves = [move]
        next_position: Position = move.next_position
        next_moves = next_position.next_moves
        if next_position.turn == repertoire.color:
            my_move = self.get_my_move(repertoire_moves=repertoire.moves, next_moves=next_moves)
            if my_move:
                moves += self.get_moves_after_position(repertoire, my_move)
        else:
            rival_moves = self.get_rival_moves(repertoire_moves=repertoire.moves, next_moves=next_moves)
            for move in rival_moves:
                moves += self.get_moves_after_position(repertoire, move)
        return moves

    def add_rival_move_to_repertoire(self, position: Position, user: User, color: bool, move_san: str):
        repertoire = self.get_user_repertoire(user=user, color=color)
        rival_moves = position.next_moves
        new_move = next((move for move in rival_moves if move.move_san == move_san), None)
        if not new_move:
            raise InvalidRequestException(description=f"Suggested move is not available in this position. Choose"
                                                      f" a different one.")
        if new_move in self.get_rival_moves(repertoire_moves=repertoire.moves, next_moves=rival_moves):
            raise InvalidRequestException(description=f"Suggested move is already in repertoire.")
        next_position = new_move.next_position
        moves = picker_service.pick_variations(position=next_position, user=user, color=color, current_depth=1)
        moves.append(new_move)
        repertoire_dao.insert_new_moves(repertoire=repertoire, user=user, color=color,
                                        moves=moves, old_moves=[])
        return moves

    def remove_rival_move_from_repertoire(self, position: Position, user: User, color: bool, move_san: str):
        repertoire = self.get_user_repertoire(user=user, color=color)
        repertoire_moves = repertoire.moves
        rival_moves: List[Move] = self.get_rival_moves(repertoire_moves, position.next_moves)
        move_to_remove = next((move for move in rival_moves if move.move_san == move_san), None)
        if not move_to_remove:
            raise InvalidRequestException(description=f"Suggested move is not available in this position. Choose"
                                                      f" a different one.")
        moves_to_remove = set(self.get_moves_after_position(repertoire=repertoire, move=move_to_remove))
        repertoire_dao.insert_new_moves(repertoire=repertoire, user=user, color=color,
                                        moves=[], old_moves=moves_to_remove)
        return moves_to_remove

    def add_variant_to_repertoire(self, position: Position, user: User, color: bool):
        if position.turn != color:
            raise InvalidRequestException(description=f"Invalid position for repertoire.")
        repertoire = self.get_user_repertoire(user=user, color=color)
        previous_move = next((move for move in repertoire.moves if move.next_pos_id == position.pos_id), None)
        if not previous_move:
            raise InvalidRequestException(description=f"Position not available in user {user.email} repertoire.")

        move = self.get_my_move(repertoire_moves=repertoire.moves, next_moves=position.next_moves)
        if move:
            raise InvalidRequestException(
                description=f"Position with FEN {position.fen} is already in user {user.email} "
                            f"repertoire.")

        moves = picker_service.pick_variations(position=position, user=user, color=color, current_depth=1)
        repertoire_dao.insert_new_moves(repertoire=repertoire, user=user, color=color,
                                        moves=moves, old_moves=[])
        return moves


repertoire_service = RepertoireService()
