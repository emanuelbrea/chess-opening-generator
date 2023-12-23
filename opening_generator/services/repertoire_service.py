from __future__ import annotations

import logging
import time
from typing import List, Dict

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from opening_generator.db.repertoire_dao import RepertoireDao
from opening_generator.models import Move, Position, User, Repertoire
from opening_generator.services.picker_service import picker_service
from opening_generator.services.position_service import PositionService


class RepertoireService:
    def __init__(self, session: Session):
        self.logger = logging.getLogger(__name__)
        self.repertoire_dao = RepertoireDao(session=session)
        self.position_service = PositionService(session=session)

    def get_user_repertoire(
            self, user: User, color: bool
    ) -> Repertoire | HTTPException:
        repertoire = next(
            (repertoire for repertoire in user.repertoire if repertoire.color == color),
            None,
        )
        if repertoire is None:
            color = "white" if color else "black"
            raise HTTPException(status_code=400, detail=f"User {user.email} does not have a {color} repertoire")
        return repertoire

    def get_user_repertoire_info(self, user: User):
        white_repertoire = self.get_repertoire_info(user=user, color=True)
        black_repertoire = self.get_repertoire_info(user=user, color=False)
        return dict(white=white_repertoire, black=black_repertoire)

    def get_repertoire_info(self, user: User, color: bool):
        try:
            repertoire: Repertoire = self.get_user_repertoire(user=user, color=color)
            repertoire_moves: List[Move] = repertoire.moves
            last_updated = repertoire.updated_at
        except HTTPException:
            return {}
        return dict(total=len(repertoire_moves), last_updated=last_updated)

    def get_repertoire_moves(
            self, position: Position, user: User, color: bool, depth: int
    ) -> Dict | HTTPException:
        try:
            repertoire = self.get_user_repertoire(user=user, color=color)
        except HTTPException:
            self.logger.warning("User %s does not have a repertoire", user.email)
            return {}
        repertoire_moves = repertoire.moves

        if position.turn == color:
            next_moves = position.next_moves
            my_move: Move = self.get_my_move(repertoire_moves, next_moves)
            if not my_move:
                self.logger.warning(
                    "Position with FEN %s is not in user %s repertoire.",
                    position.fen,
                    user.email,
                )
                return {}

            my_move_stats: Dict = self.position_service.get_move_stats(move=my_move)
            favorite_moves: List[Move] = [
                fav_move.move for fav_move in user.favorites_moves
            ]
            my_move_stats["favorite"] = my_move in favorite_moves
            moves = []
            floor: float = picker_service.calculate_floor(
                current_depth=depth, depth=picker_service.get_depth(user)
            )
            for move in next_moves:
                if move.popularity_weight + move.played / 1000 / 100 >= floor:
                    stats = self.position_service.get_move_stats(move=move)
                    stats["favorite"] = move in favorite_moves
                    moves.append(stats)

            my_moves_stats = sorted(moves, key=lambda d: d["played"], reverse=True)
            next_position: Position = my_move.next_position
        else:
            next_position: Position = position
            my_move_stats = {}
            my_moves_stats = {}

        position_stats: Dict = self.position_service.get_position_stats(position=position)

        rival_moves: List[Move] = self.get_rival_moves(
            repertoire_moves, next_position.next_moves
        )
        rival_moves_stats = []
        for move in rival_moves:
            rival_moves_stats.append(self.position_service.get_move_stats(move=move))
        rival_moves_stats = sorted(
            rival_moves_stats, key=lambda d: d["played"], reverse=True
        )

        return dict(
            position=position_stats,
            my_move=my_move_stats,
            my_moves=my_moves_stats,
            rival_moves=rival_moves_stats,
            depth=depth,
        )

    def get_my_move(
            self, repertoire_moves: List[Move], next_moves: List[Move]
    ) -> Move | None:
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

    def create_user_repertoire(self, position: Position, user: User, color: bool):
        self.logger.info(
            "About to create %s repertoire for user %s",
            "white" if color else "black",
            user.email,
        )
        start_time = time.time()
        moves: List[Move] = picker_service.pick_variations(
            position=position, user=user, color=color
        )
        self.repertoire_dao.create_repertoire(user=user, color=color, moves=moves)
        self.logger.info("Created repertoire for user %s", user.email)
        self.repertoire_dao.save_repertoire_metric(
            user=user, moves=len(moves), start_time=start_time, end_time=time.time()
        )

    def update_user_repertoire(
            self, position: Position, user: User, color: bool, new_move: str
    ):
        start_time = time.time()
        repertoire = self.get_user_repertoire(user=user, color=color)
        repertoire_moves = repertoire.moves
        next_moves = position.next_moves
        move_to_remove = self.get_my_move(
            repertoire_moves=repertoire_moves, next_moves=next_moves
        )
        if not move_to_remove:
            raise HTTPException(status_code=400, detail=f"Position with FEN {position.fen} is not in user {user.email} "
                                                        f"repertoire.")

        if not new_move:
            tries = 0
            depth = picker_service.get_depth(user)
            new_move = picker_service.pick_move(
                position=position, user=user, color=color, depth=depth
            )
            while new_move is move_to_remove:
                new_move = picker_service.pick_move(
                    position=position, user=user, color=color, depth=depth
                )
                tries += 1
                if tries == 10:
                    raise HTTPException(status_code=400,
                                        detail=f"Not able to find a good move to replace {move_to_remove.move_san}."
                                               f" Consider passing it manually.")
        else:
            new_move = next(
                (move for move in next_moves if move.move_san == new_move), None
            )
            if not new_move:
                raise HTTPException(status_code=400, detail=f"Suggested move is not available in this position. Choose"
                                                            f" a different one.")
        next_position = new_move.next_position
        moves = picker_service.pick_variations(
            position=next_position, user=user, color=color, current_depth=1
        )
        moves.append(new_move)

        moves_to_remove = self.get_moves_after_position(
            repertoire=repertoire, move=move_to_remove, visited={}
        )
        self.repertoire_dao.insert_new_moves(
            repertoire=repertoire,
            user=user,
            color=color,
            moves=moves,
            old_moves=moves_to_remove,
        )
        self.repertoire_dao.update_repertoire_history(
            user=user, new_move=new_move, old_move=move_to_remove
        )
        self.repertoire_dao.save_repertoire_metric(
            user=user, moves=len(moves), start_time=start_time, end_time=time.time()
        )
        return moves

    def get_moves_after_position(
            self, repertoire: Repertoire, move: Move, visited: Dict
    ) -> List[Move]:
        if move in visited:
            return []
        visited[move] = True
        moves = [move]
        next_position: Position = move.next_position
        next_moves = next_position.next_moves
        if next_position.turn == repertoire.color:
            my_move = self.get_my_move(
                repertoire_moves=repertoire.moves, next_moves=next_moves
            )
            if my_move and my_move not in moves:
                moves += self.get_moves_after_position(repertoire, my_move, visited)
        else:
            rival_moves = self.get_rival_moves(
                repertoire_moves=repertoire.moves, next_moves=next_moves
            )
            for move in rival_moves:
                if move not in moves:
                    moves += self.get_moves_after_position(repertoire, move, visited)
        return moves

    def add_rival_move_to_repertoire(
            self, position: Position, user: User, color: bool, move_san: str
    ):
        repertoire = self.get_user_repertoire(user=user, color=color)
        rival_moves = position.next_moves
        new_move = next(
            (move for move in rival_moves if move.move_san == move_san), None
        )
        if not new_move:
            raise HTTPException(status_code=400, detail=f"Suggested move is not available in this position. Choose"
                                                        f" a different one.")
        if new_move in self.get_rival_moves(
                repertoire_moves=repertoire.moves, next_moves=rival_moves
        ):
            raise HTTPException(status_code=400, detail=f"Suggested move is already in repertoire.")
        next_position = new_move.next_position
        moves = picker_service.pick_variations(
            position=next_position, user=user, color=color, current_depth=1
        )
        moves.append(new_move)
        self.repertoire_dao.insert_new_moves(
            repertoire=repertoire, user=user, color=color, moves=moves, old_moves=[]
        )
        return moves

    def remove_rival_move_from_repertoire(
            self, position: Position, user: User, color: bool, move_san: str
    ):
        repertoire = self.get_user_repertoire(user=user, color=color)
        repertoire_moves = repertoire.moves
        rival_moves: List[Move] = self.get_rival_moves(
            repertoire_moves, position.next_moves
        )
        move_to_remove = next(
            (move for move in rival_moves if move.move_san == move_san), None
        )
        if not move_to_remove:
            raise HTTPException(status_code=400, detail=f"Suggested move is not available in this position. Choose"
                                                        f" a different one.")
        moves_to_remove = self.get_moves_after_position(repertoire=repertoire, move=move_to_remove, visited={})

        self.repertoire_dao.insert_new_moves(
            repertoire=repertoire,
            user=user,
            color=color,
            moves=[],
            old_moves=moves_to_remove,
        )
        return moves_to_remove

    def add_variant_to_repertoire(self, position: Position, user: User, color: bool):
        if position.turn != color:
            raise HTTPException(status_code=400, detail=f"Invalid position for repertoire.")
        start_time = time.time()
        repertoire = self.get_user_repertoire(user=user, color=color)
        previous_move = next(
            (move for move in repertoire.moves if move.next_pos_id == position.pos_id),
            None,
        )
        if not previous_move:
            raise HTTPException(status_code=400, detail=f"Position not available in user {user.email} repertoire.")

        move = self.get_my_move(
            repertoire_moves=repertoire.moves, next_moves=position.next_moves
        )
        if move:
            raise HTTPException(status_code=400,
                                detail=f"Position with FEN {position.fen} is already in user {user.email} "
                                       f"repertoire.")

        moves = picker_service.pick_variations(
            position=position, user=user, color=color, current_depth=1
        )
        self.repertoire_dao.insert_new_moves(
            repertoire=repertoire, user=user, color=color, moves=moves, old_moves=[]
        )
        self.repertoire_dao.save_repertoire_metric(
            user=user, moves=len(moves), start_time=start_time, end_time=time.time()
        )
        return moves

    def delete_user_repertoire(self, user: User, color: bool):
        try:
            self.repertoire_dao.delete_repertoire(user=user, color=color)
        except IntegrityError as err:
            message = f"There was an error deleting user {user.email} repertoire."
            self.logger.error(message)
            raise HTTPException(status_code=400, detail=message) from err
