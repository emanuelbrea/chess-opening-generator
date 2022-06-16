from typing import List

from sqlalchemy.exc import NoResultFound

from opening_generator.db.move_dao import move_dao
from opening_generator.models import Move
from opening_generator.services.tree_loader_service import TreeLoaderService


class OpeningTreeService:

    def __init__(self):
        self.root: Move = self.retrieve_initial_position()

    def get_variation(self, moves: List[str]):
        return self.root.get_variation(moves)

    def retrieve_initial_position(self):
        try:
            initial_position = move_dao.get_initial_position()
        except NoResultFound:
            tree_loader = TreeLoaderService()
            tree_loader.load_games()
            initial_position = move_dao.get_initial_position()
        return initial_position


opening_tree_service = OpeningTreeService()
