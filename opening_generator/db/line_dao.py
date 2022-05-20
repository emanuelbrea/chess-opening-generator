from opening_generator.db import db_session


def save_lines(book: {}):
    for line in book.values():
        line.set_final_elo()

    db_session.add_all(book.values())
    db_session.commit()
    db_session.close()
