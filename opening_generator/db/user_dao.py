from opening_generator.db import db_session
from opening_generator.models.repertoire import Repertoire
from opening_generator.models.user import User


def create_user():
    user = User(first_name='emanuel', email='ema_brea')
    db_session.add(user)
    repertoire = Repertoire(user=user, line_id='asd', color='WHITE')
    db_session.add(repertoire)
    db_session.commit()
    db_session.close()
