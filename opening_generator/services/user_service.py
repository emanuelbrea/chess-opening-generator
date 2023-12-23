import logging
from typing import List

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from opening_generator.db.user_dao import UserDao
from opening_generator.models import Style, User, Move, Position


class UserService:
    def __init__(self, session: Session):
        self.logger = logging.getLogger(__name__)
        self.user_dao = UserDao(session)

    def create_user(self, first_name: str, last_name: str, email: str):
        try:
            self.user_dao.create_user(
                first_name=first_name, last_name=last_name, email=email
            )
        except IntegrityError as err:
            raise HTTPException(status_code=400,
                                detail=f"User {first_name} {last_name} with email {email} already exists.") from err

    def update_user_style(
            self, user: User, popularity: float, fashion: float, risk: float, rating: int
    ):
        style: Style = user.style
        style.rating = rating
        style.risk = risk
        style.fashion = fashion
        style.popularity = popularity
        try:
            self.user_dao.add_style_to_user(user=user, style=style)
        except IntegrityError as err:
            raise HTTPException(status_code=400,
                                detail=f"Invalid style.") from err

    def update_user(
            self, user: User, first_name: str, last_name: str, age: int, playing_since: int
    ):
        try:
            self.user_dao.update_user(
                user=user,
                first_name=first_name,
                last_name=last_name,
                age=age,
                playing_since=playing_since,
            )
        except IntegrityError as err:
            raise HTTPException(status_code=400,
                                detail=f"Invalid values for user profile. "
                                       f"Name: {first_name}. Last name: {last_name}") from err

    def add_favorite_move(self, user: User, position: Position, move_san: str):
        user_favorite_moves: List[Move] = [
            fav_move.move for fav_move in user.favorites_moves
        ]

        move: Move = next(
            (move for move in position.next_moves if move.move_san == move_san),
            None,
        )

        if not move:
            raise HTTPException(status_code=400, detail="Invalid favorite move")

        if move in user_favorite_moves:
            self.user_dao.remove_favorite_move(user=user, move=move)
        else:
            self.user_dao.add_favorite_move(user=user, move=move)
        return move

    def save_user_message(self, message: str, email: str, name: str, rating: int):
        self.user_dao.save_user_message(
            message=message, email=email, name=name, rating=rating
        )
        self.logger.info("Saved new message from %s", email)
