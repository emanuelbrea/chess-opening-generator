import logging

from sqlalchemy.exc import IntegrityError, NoResultFound

from opening_generator.db.user_dao import user_dao
from opening_generator.exceptions import UserException
from opening_generator.models import Style, User
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

    def update_user(self, user: User, first_name: str, last_name: str, age: int, playing_since: int):
        try:
            user_dao.update_user(user=user, first_name=first_name, last_name=last_name, age=age,
                                 playing_since=playing_since)
        except IntegrityError as err:
            raise UserException(
                f"Invalid values for user profile. Name: {first_name}. Last name: {last_name}"
            ) from err

    def get_user(self):
        user_claims = auth_service.get_user_claims()
        email = user_claims.get("email")
        try:
            user = user_dao.get_user(email=email)
        except NoResultFound as err:
            raise UserException(f"User with email {email} does not exists.") from err
        return user


user_service = UserService()
