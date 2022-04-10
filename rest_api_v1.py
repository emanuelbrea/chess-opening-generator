import chess
from flask import Flask, request, abort, jsonify

from pgn import Pgn
from picker import Picker
from position import Position

app = Flask(__name__)

main_pgn = Pgn()


@app.route('/position', methods=["GET"])
def get_variations():
    args = request.args

    fen = args.get("fen")
    if not fen:
        abort(404, description="Fen not provided")

    depth = int(args.get("depth", 3))
    color = args.get("color", "WHITE").upper() == "WHITE"

    board = chess.Board(fen)
    pgn = Pgn.get_instance()
    position: Position = pgn.load_position_from_book(board=board)

    if not position:
        abort(404, description="Position not found in database")

    picker = Picker(pgn)
    variations = picker.pick_variations(board=board, current_position=position, color=color, depth=depth)
    return jsonify(status=200, message="Variations calculated correctly.", data=variations, success=True)
