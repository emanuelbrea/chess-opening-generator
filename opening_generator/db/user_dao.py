import logging

from opening_generator.db import db_session
from opening_generator.models import Style
from opening_generator.models.user import User


class UserDao:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def create_user(self, first_name, email):
        style = Style()
        user = User(first_name=first_name, email=email, style=style)
        db_session.add(user)
        db_session.commit()
        self.logger.info("Created new user with name %s and email %s", first_name, email)

    def add_style_to_user(self, user: User, style: Style):
        user.style = style
        db_session.commit()
        self.logger.info("Updated style for user %s. Popularity: %f , Fashion: %f ,"
                         " Risk %f, Rating %d", user.email, style.popularity, style.fashion, style.risk, style.rating)


user_dao = UserDao()
