import logging

from opening_generator import Position, User
from opening_generator.models import Move


class RepertoireService:

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_repertoire_moves(self, position: Position, user: User, color: bool):
        next_moves = position.next_moves
        repertoire = [repertoire for repertoire in user.repertoire if repertoire.color == color][0]
        repertoire_moves = repertoire.moves
        my_move = self.get_my_move(repertoire_moves, next_moves)
        if not my_move:
            return []

        next_position: Position = my_move.next_position
        my_move_stats = dict(move=my_move.move_san,
                             played=my_move.played,
                             total_games=next_position.total_games,
                             white_wins=next_position.white_wins,
                             draws=next_position.draws,
                             black_wins=next_position.black_wins,
                             average_rating=next_position.average_elo,
                             average_year=next_position.average_year,
                             fen=position.fen
                             )
        rival_moves = self.get_rival_moves(repertoire_moves, next_position.next_moves)
        rival_moves_stats = {}
        for move in rival_moves:
            next_position = move.next_position
            rival_moves_stats[move.move_san] = dict(move=move.move_san,
                                                    played=move.played,
                                                    total_games=next_position.total_games,
                                                    white_wins=next_position.white_wins,
                                                    draws=next_position.draws,
                                                    black_wins=next_position.black_wins,
                                                    average_rating=next_position.average_elo,
                                                    average_year=next_position.average_year,
                                                    fen=next_position.fen
                                                    )

        return dict(my_move=my_move_stats, rival_moves=rival_moves_stats)

    def get_my_move(self, repertoire_moves, next_moves) -> Move:
        for move in repertoire_moves:
            if move in next_moves:
                return move
        return None

    def get_rival_moves(self, repertoire_moves, next_moves) -> Move:
        rival_moves = []
        for move in repertoire_moves:
            if move in next_moves:
                rival_moves.append(move)
        return rival_moves


repertoire_service = RepertoireService()
