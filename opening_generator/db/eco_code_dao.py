import csv
import io
import os

import chess.pgn
from chess.polyglot import zobrist_hash

from opening_generator import db_session
from opening_generator.models.eco_code import EcoCode
from opening_generator.models.line import Line


def add_eco_codes():
    ecos = []
    for filename in os.listdir(os.path.dirname(__file__) + "/../../data/eco/"):
        if os.path.splitext(filename)[1] == '.csv':
            filename = os.path.dirname(__file__) + os.path.join("/../../data/eco/", filename)

            with open(filename) as file:
                csvreader = csv.reader(file)
                next(csvreader)
                for row in csvreader:
                    eco_code = row[1]
                    name = row[2]
                    line = row[3]
                    pgn = io.StringIO(line)
                    game = chess.pgn.read_game(pgn)
                    board = game.board()
                    for move in game.mainline_moves():
                        board.push(move)
                    fen_key: int = zobrist_hash(board=board)

                    line_db = db_session.query(Line).filter(Line.line_id == str(fen_key)).first()

                    if line_db:
                        eco = EcoCode(eco_code=eco_code, line_id=str(fen_key), main_line=line, name=name)
                        ecos.append(eco)
    db_session.add_all(ecos)
    db_session.commit()
    db_session.close()
