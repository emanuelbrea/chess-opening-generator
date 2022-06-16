from flask import jsonify, Blueprint

from opening_generator.models import User, Style
from opening_generator.tree.loader import TreeLoader

move_bp = Blueprint('move', __name__, url_prefix='/move')

user = User(user_id=1, first_name='Emanuel', email='a', rating=1800)
style = Style(user_id=1, popularity=0, fashion=0, risk=0)
user.style = style


@move_bp.route('/games', methods=["POST"])
def load_games():
    tree_loader = TreeLoader()
    tree_loader.load_games()
    return jsonify(message=f"Loaded positions correctly.", success=True), 200
