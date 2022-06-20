from opening_generator.db import db_session
from opening_generator.models.user import User


def create_user():
    user = User(first_name='emanuel', email='ema_brea')
    db_session.add(user)
    db_session.commit()
