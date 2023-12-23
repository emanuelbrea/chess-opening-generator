import logging

from sqlalchemy.orm import Session

from opening_generator.models import Style, Move, Contact
from opening_generator.models.move import FavoriteMoves
from opening_generator.models.user import User


class UserDao:
    def __init__(self, session: Session):
        self.logger = logging.getLogger(__name__)
        self.session = session

    def create_user(self, first_name, last_name, email):
        style = Style()
        user = User(
            first_name=first_name, last_name=last_name, email=email, style=style
        )
        self.session.add(user)
        self.session.commit()
        self.logger.info(
            "Created new user with name %s and email %s", first_name, email
        )
        return user

    def add_style_to_user(self, user: User, style: Style):
        user.style = style
        self.session.commit()
        self.logger.info(
            "Updated style for user %s. Popularity: %f , Fashion: %f ,"
            " Risk %f, Rating %d",
            user.email,
            style.popularity,
            style.fashion,
            style.risk,
            style.rating,
        )

    def get_user(self, email: str):
        user = self.session.query(User).filter(User.email == email).one()
        return user

    def get_default_user(self):
        user = self.session.query(User).first()
        return user

    def update_user(
            self, user: User, first_name: str, last_name: str, age: int, playing_since: int
    ):
        user.first_name = first_name
        user.last_name = last_name
        user.age = age
        user.playing_since = playing_since
        self.session.commit()
        self.logger.info(
            "Updated user profile: %s %s for user %s", first_name, last_name, user.email
        )

    def add_favorite_move(self, user: User, move: Move):
        favorite_move = FavoriteMoves(user=user, move=move)
        user.favorites_moves.append(favorite_move)
        self.session.commit()

    def remove_favorite_move(self, user: User, move: Move):
        fav_move = next(
            (fav_move for fav_move in user.favorites_moves if fav_move.move == move),
            None,
        )
        if fav_move:
            self.session.delete(fav_move)
            self.session.commit()

    def save_user_message(self, message: str, email: str, name: str, rating: int):
        contact = Contact(message=message, email=email, name=name, rating=rating)
        self.session.add(contact)
        self.session.commit()
