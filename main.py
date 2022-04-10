import chess

from position import Position
from pgn import Pgn
from picker import Picker
import time

pgn = Pgn()

# Get position from user
start = time.time()
fen = "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"
board = chess.Board(fen)
entry: Position = pgn.load_position_from_book(board=board)
picker = Picker(pgn)
play_as = False  # as black pieces
picker.pick_variations(board, entry, play_as, depth=5)
print(time.time() - start)
