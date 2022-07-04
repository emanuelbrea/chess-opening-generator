import logging

from sqlalchemy.exc import IntegrityError

from opening_generator.db.user_dao import user_dao
from opening_generator.exceptions import UserException
from opening_generator.models import Style, User


class UserService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_user(self, first_name, email):
        try:
            user_dao.create_user(first_name=first_name, email=email)
        except IntegrityError as err:
            raise UserException(f"User with email {email} already exists.") from err

    def create_user_style(self, user: User, popularity: float, fashion: float, risk: float, rating: int):
        style = Style(popularity=popularity, fashion=fashion, risk=risk, rating=rating)
        try:
            user_dao.add_style_to_user(user=user, style=style)
        except IntegrityError as err:
            raise UserException(f"Invalid style.") from err


user_service = UserService()
