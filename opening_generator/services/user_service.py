import logging
from typing import List

from sqlalchemy.exc import IntegrityError, NoResultFound

from opening_generator.db.user_dao import user_dao
from opening_generator.exceptions import UserException, InvalidRequestException
from opening_generator.models import Style, User, Move, Position
from opening_generator.services.auth_service import auth_service


class UserService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_user(self, first_name: str, last_name: str, email: str):
        try:
            user_dao.create_user(
                first_name=first_name, last_name=last_name, email=email
            )
        except IntegrityError as err:
            raise UserException(
                f"User {first_name} {last_name} with email {email} already exists."
            ) from err

    def update_user_style(
        self, user: User, popularity: float, fashion: float, risk: float, rating: int
    ):
        style: Style = user.style
        style.rating = rating
        style.risk = risk
        style.fashion = fashion
        style.popularity = popularity
        try:
            user_dao.add_style_to_user(user=user, style=style)
        except IntegrityError as err:
            raise UserException(f"Invalid style.") from err

    def update_user(
        self, user: User, first_name: str, last_name: str, age: int, playing_since: int
    ):
        try:
            user_dao.update_user(
                user=user,
                first_name=first_name,
                last_name=last_name,
                age=age,
                playing_since=playing_since,
            )
        except IntegrityError as err:
            raise UserException(
                f"Invalid values for user profile. Name: {first_name}. Last name: {last_name}"
            ) from err

    def get_user(self):
        user_claims = auth_service.get_user_claims()
        email = user_claims.get("email")
        try:
            user = user_dao.get_user(email=email)
        except NoResultFound:
            self.logger.info(
                "User with email %s does not exist. Will create it.", email
            )
            first_name = user_claims.get("given_name", "")
            last_name = user_claims.get("family_name", "")
            user = user_dao.create_user(
                first_name=first_name, last_name=last_name, email=email
            )
        return user

    def add_favorite_move(self, user: User, position: Position, move_san: str):
        user_favorite_moves: List[Move] = [
            fav_move.move for fav_move in user.favorites_moves
        ]

        move: Move = next(
            (move for move in position.next_moves if move.move_san == move_san),
            None,
        )

        if not move:
            raise InvalidRequestException(description="Invalid favorite move")

        if move in user_favorite_moves:
            user_dao.remove_favorite_move(user=user, move=move)
        else:
            user_dao.add_favorite_move(user=user, move=move)
        return move


user_service = UserService()
