import logging

from sqlalchemy.exc import IntegrityError

from opening_generator.db.user_dao import user_dao
from opening_generator.exceptions import UserException


class UserService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_user(self, first_name, email):
        try:
            user_dao.create_user(first_name=first_name, email=email)
        except IntegrityError as err:
            raise UserException(f"User with email {email} already exists.") from err


user_service = UserService()
