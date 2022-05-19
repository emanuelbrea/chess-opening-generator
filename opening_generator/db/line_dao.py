from opening_generator.db import db_session


def save_lines(book: {}):
    for line in book.values():
        if line.total_games > 10:
            line.set_final_elo()
            db_session().add(line)
    db_session.commit()
    db_session.close()
