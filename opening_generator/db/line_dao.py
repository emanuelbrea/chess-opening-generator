import logging

from opening_generator.db import db_session
from opening_generator.models.line import Line


class LineDao:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_line_by_position(self, fen: str):
        return db_session.query(Line).filter(Line.fen == fen).first()

    def save_lines(self, book: {}):
        self.logger.info("About to insert %d lines.", len(book))
        for line in book.values():
            line.set_final_elo()

        db_session.add_all(book.values())
        db_session.commit()
        db_session.close()

        self.logger.info("Finished inserting lines.")


line_dao = LineDao()
