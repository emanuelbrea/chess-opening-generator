import csv
import io
import logging
import os

from chess import pgn

from opening_generator.db.eco_code_dao import eco_code_dao
from opening_generator.models import Position
from opening_generator.models.eco_code import EcoCode
from opening_generator.services.position_service import position_service


class EcoCodeService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.folder = "/../../data/eco/"
        self.load_eco_codes()

    def load_eco_codes(self):
        eco_codes = self.get_eco_codes()
        if len(eco_codes) == 0:
            for filename in os.listdir(os.path.dirname(__file__) + self.folder):
                if os.path.splitext(filename)[1] == '.csv':
                    filename = os.path.dirname(__file__) + os.path.join(self.folder, filename)
                    with open(filename) as file:
                        csvreader = csv.reader(file)
                        next(csvreader)
                        for row in csvreader:
                            eco_code = row[1]
                            name = row[2]
                            line = row[3]
                            game_pgn = io.StringIO(line)
                            game = pgn.read_game(game_pgn)
                            position = position_service.get_position(board=game.end().board())
                            if position:
                                eco = EcoCode(eco_code=eco_code, name=name, main_line=line, position=position)
                                eco_codes.append(eco)

            eco_code_dao.add_eco_codes(ecos=eco_codes)
        return eco_codes

    def get_eco_codes(self):
        return eco_code_dao.get_eco_codes()

    def get_eco_code(self, position: Position):
        return eco_code_dao.get_eco_code(position)


eco_service = EcoCodeService()
