import csv
import io
import logging
import os

import chess
from chess import pgn
from sqlalchemy.orm import Session

from opening_generator.db.eco_code_dao import EcoCodeDao
from opening_generator.models import Position
from opening_generator.models.eco_code import EcoCode
from opening_generator.services.position_service import PositionService


class EcoCodeService:

    def __init__(self, session: Session):
        self.logger = logging.getLogger(__name__)
        self.eco_code_dao = EcoCodeDao(session=session)
        self.position_service = PositionService(session=session)
        self.link = "https://en.wikibooks.org/wiki/Chess_Opening_Theory"
        self.load_eco_codes()
        self.positions_loaded = {}

    def load_eco_codes(self):
        eco_codes = self.get_eco_codes()
        self.logger.info(f"Got {len(eco_codes)} eco codes")

        if len(eco_codes) == 0:
            current_dir = os.path.dirname(__file__)
            parent_dir = os.path.dirname(current_dir)
            data_dir = os.path.join(parent_dir, 'data', 'eco')

            self.logger.info(f"Loading Eco Codes from {data_dir}")
            for filename in os.listdir(data_dir):
                if os.path.splitext(filename)[1] == ".csv":
                    filename = os.path.join(
                        data_dir, filename
                    )
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
                                    link = (
                                            link
                                            + "/"
                                            + str(board.fullmove_number)
                                            + "._"
                                            + board.san(move)
                                    )
                                else:
                                    link = (
                                            link
                                            + "/"
                                            + str(board.fullmove_number)
                                            + "..."
                                            + board.san(move)
                                    )
                                board.push(move)
                            position = self.position_service.get_position(board=board)
                            if position:
                                eco = EcoCode(
                                    eco_code=eco_code,
                                    name=name,
                                    main_line=line,
                                    position=position,
                                    description=link,
                                )
                                eco_codes.append(eco)

            self.eco_code_dao.add_eco_codes(ecos=eco_codes)
        return eco_codes

    def add_move_description(self, move, depth, color, description):
        if not move.description:
            if color:
                move.description = description + "/" + str(depth) + "._" + move.move_san
            else:
                move.description = (
                        description + "/" + str(depth) + "..." + move.move_san
                )
        next_position: Position = move.next_position
        if next_position.pos_id not in self.positions_loaded:
            self.positions_loaded[next_position.pos_id] = True
            for next_move in next_position.next_moves:
                self.add_move_description(
                    next_move,
                    depth + 1 if not color else depth,
                    not color,
                    move.description,
                )

    def get_eco_codes(self):
        return self.eco_code_dao.get_eco_codes()

    def get_eco_code(self, position: Position):
        return self.eco_code_dao.get_eco_code(position)
