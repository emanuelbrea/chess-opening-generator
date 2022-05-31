from flask import Blueprint, jsonify

from opening_generator.services.eco_code_service import eco_service

eco = Blueprint('eco_code', __name__, url_prefix='/eco')


@eco.route('/', methods=["POST"])
def load_eco_codes():
    eco_codes = eco_service.load_eco_codes()
    return jsonify(message=f"Loaded eco codes correctly.", data=dict(total=len(eco_codes)), success=True), 200


@eco.route('/svg', methods=["POST"])
def save_svg():
    boards = eco_service.get_eco_codes_boards()
    eco_service.save_board_as_svg(boards=boards)
    return jsonify(message=f"Save svg eco positions correctly.", data=dict(total=len(boards)), success=True), 200
