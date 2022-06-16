import csv
import io
import logging
import os
from typing import List

import chess
import chess.svg

from opening_generator.db.eco_code_dao import eco_code_dao
from opening_generator.models.eco_code import EcoCode


class EcoCodeService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.folder = "/../../data/eco/"

    def load_eco_codes(self):
        ecos = []
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
                        pgn = io.StringIO(line)
                        game = chess.pgn.read_game(pgn)
                        eco = EcoCode(eco_code=eco_code, main_line=line, name=name)
                        ecos.append(eco)

        eco_code_dao.add_eco_codes(ecos=ecos)
        return ecos

    def get_eco_codes(self):
        return eco_code_dao.get_eco_codes()

    def get_eco_codes_boards(self):
        ecos: List[EcoCode] = self.get_eco_codes()
        boards = {}
        for eco in ecos:
            pgn = io.StringIO(eco.main_line)
            game = chess.pgn.read_game(pgn)
            boards[eco.eco_code] = game.end().board()
        return boards

    def save_board_as_svg(self, boards):
        for eco_code, board in boards.items():
            svg = chess.svg.board(board)
            with open(f'data/svg/{eco_code}.svg', 'w') as fd:
                fd.write(svg)


eco_service = EcoCodeService()