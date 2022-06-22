import logging
from typing import List, Dict

from opening_generator.db.repertoire_dao import repertoire_dao
from opening_generator.exceptions import InvalidRequestException
from opening_generator.models import Move, Position, User, Repertoire
from opening_generator.services.picker_service import picker_service


class RepertoireService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_user_repertoire(self, user: User, color: bool) -> Repertoire | None:
        repertoire = next((repertoire for repertoire in user.repertoire if repertoire.color == color), None)
        if repertoire is None:
            color = "white" if color else "black"
            raise InvalidRequestException(description=f"User {user.email} does not have a {color} repertoire")
        return repertoire

    def get_repertoire_moves(self, position: Position, user: User, color: bool) -> InvalidRequestException | Dict:
        repertoire = self.get_user_repertoire(user=user, color=color)
        repertoire_moves = repertoire.moves
        next_moves = position.next_moves
        my_move = self.get_my_move(repertoire_moves, next_moves)
        if not my_move:
            return InvalidRequestException(description=f"Position with FEN {position.fen} is not in user "
                                                       f"{user.email} repertoire.")

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
        self.logger.info("About to create both repertoires for user %s", user.email)
        moves = picker_service.pick_variations(position, user, True)
        repertoire_dao.create_repertoire(user=user, color=True, moves=moves)
        moves = picker_service.pick_variations(position, user, False)
        repertoire_dao.create_repertoire(user=user, color=False, moves=moves)
        self.logger.info("Created both repertoires for user %s", user.email)

    def update_user_repertoire(self, position, user, color, new_move):
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
            new_move = picker_service.pick_move(position, user, color, depth)
            while new_move is move_to_remove:
                new_move = picker_service.pick_move(position, user, color, depth)
                tries += 1
                if tries == 10:
                    raise InvalidRequestException(
                        description=f"Not able to find a good move to replace {move_to_remove.move_san}."
                                    f" Consider passing it manually.")
        else:
            new_move = next((move for move in next_moves if move.move_san == new_move), None)
            if not new_move:
                raise InvalidRequestException(description=f"Suggested moved is not available in this position. Choose"
                                                          f" a different one.")
        next_position = new_move.next_position
        moves = picker_service.pick_variations(next_position, user, color)
        moves.append(new_move)

        moves_to_remove = self.get_moves_after_position(repertoire_moves, move_to_remove)
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
