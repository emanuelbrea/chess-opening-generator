import logging
from typing import List

import pandas as pd

from opening_generator.db import db_session
from opening_generator.models.line import Line


class LineDao:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_line_by_position(self, line_id: str):
        return db_session.query(Line).filter(Line.line_id == line_id).first()

    def save_lines(self, book: {}):
        self.logger.info("About to insert %i lines.", len(book))

        db_session.add_all(book.values())
        db_session.commit()
        db_session.close()

        self.logger.info("Finished inserting lines.")
        return book

    def get_next_positions_as_df(self, lines: List[str]):
        query = db_session.query(Line).filter(Line.line_id.in_(lines))
        return pd.read_sql(query.statement, db_session.engine)


line_dao = LineDao()
