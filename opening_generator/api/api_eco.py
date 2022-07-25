import chess
from flask import Blueprint, jsonify, request

from opening_generator.api.api_position import get_board_by_fen, get_position_by_board
from opening_generator.models import Position, EcoCode
from opening_generator.services.eco_code_service import eco_service

eco_bp = Blueprint('eco_code', __name__, url_prefix='/api/eco')


@eco_bp.route('/', methods=["GET"])
def get_eco_code():
    args = request.args

    board: chess.Board = get_board_by_fen(args)

    position: Position = get_position_by_board(board)

    eco_code: EcoCode = eco_service.get_eco_code(position=position)

    if not eco_code:
        return jsonify(message="Eco code not found for position.", data={}, success=True), 200

    eco_code_desc = dict(eco_code=eco_code.eco_code,
                         main_line=eco_code.main_line,
                         name=eco_code.name)
    return jsonify(message="Eco code found for position.", data=eco_code_desc, success=True), 200
