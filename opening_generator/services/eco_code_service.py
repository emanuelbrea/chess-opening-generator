import csv
import io
import logging
import os
from typing import List

import chess
from chess import pgn

from opening_generator.db import db_session
from opening_generator.db.eco_code_dao import eco_code_dao
from opening_generator.models import Position, Move
from opening_generator.models.eco_code import EcoCode
from opening_generator.services.position_service import position_service


class EcoCodeService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.folder = "/../../data/eco/"
        self.link = "https://en.wikibooks.org/wiki/Chess_Opening_Theory"
        self.load_eco_codes()
        self.positions_loaded = {}

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
                            link = self.link
                            game_pgn = io.StringIO(line)
                            game = pgn.read_game(game_pgn)
                            board: chess.Board = game.board()
                            for move in game.mainline_moves():
                                if board.turn:
                                    link = link + '/' + str(board.fullmove_number) + '._' + board.san(move)
                                else:
                                    link = link + '/' + str(board.fullmove_number) + '...' + board.san(move)
                                board.push(move)
                            position = position_service.get_position(board=board)
                            if position:
                                eco = EcoCode(eco_code=eco_code, name=name, main_line=line, position=position,
                                              description=link)
                                eco_codes.append(eco)

            eco_code_dao.add_eco_codes(ecos=eco_codes)
        return eco_codes

    def add_moves_description(self):
        initial_position: Position = position_service.retrieve_initial_position()
        next_moves: List[Move] = initial_position.next_moves
        for move in next_moves:
            self.add_move_description(move=move, depth=1, color=True, description=self.link)
        self.positions_loaded.clear()
        db_session.commit()
        db_session.close()
        self.logger.info("Added moves descriptions")

    def add_move_description(self, move, depth, color, description):
        if not move.description:
            if color:
                move.description = description + '/' + str(depth) + '._' + move.move_san
            else:
                move.description = description + '/' + str(depth) + '...' + move.move_san
        next_position: Position = move.next_position
        if next_position.pos_id not in self.positions_loaded:
            self.positions_loaded[next_position.pos_id] = True
            for next_move in next_position.next_moves:
                self.add_move_description(next_move, depth + 1 if not color else depth, not color, move.description)

    def get_eco_codes(self):
        return eco_code_dao.get_eco_codes()

    def get_eco_code(self, position: Position):
        return eco_code_dao.get_eco_code(position)


eco_service = EcoCodeService()
