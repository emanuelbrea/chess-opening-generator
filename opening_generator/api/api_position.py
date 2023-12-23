from typing import List

import chess
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from opening_generator.db import get_db
from opening_generator.models import Position
from opening_generator.models.schemas import SuccessfulDataResponse
from opening_generator.services.position_service import PositionService

position_router = APIRouter(prefix="/position", tags=["position"])


def get_board_by_fen(fen: str) -> chess.Board:
    try:
        board: chess.Board = chess.Board(fen)
        return board
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FEN provided")


def get_color(color: str = "WHITE") -> bool:
    color = color.upper()
    if color not in ("WHITE", "BLACK"):
        raise HTTPException(status_code=400, detail="Invalid color provided")
    return color == "WHITE"


@position_router.get("/stats", response_model=SuccessfulDataResponse, status_code=200)
def get_stats(fen: str, session: Session = Depends(get_db)):
    position_service = PositionService(session=session)
    board: chess.Board = get_board_by_fen(fen=fen)

    position: Position = position_service.get_position_by_board(board)

    stats = position_service.get_position_stats(position=position)
    return SuccessfulDataResponse(message="Stats retrieved correctly.",
                                  data=stats, success=True)


@position_router.get("/moves", response_model=SuccessfulDataResponse, status_code=200)
def get_moves(fen: str, session: Session = Depends(get_db)):
    position_service = PositionService(session=session)
    board: chess.Board = get_board_by_fen(fen=fen)

    position: Position = position_service.get_position_by_board(board)

    next_moves: List[str] = position_service.get_next_moves(position=position)

    return SuccessfulDataResponse(message="Next moves retrieved correctly.",
                                  data=next_moves, success=True)


@position_router.get("/moves/stats", response_model=SuccessfulDataResponse, status_code=200)
def get_next_moves_stats(fen: str, session: Session = Depends(get_db)):
    position_service = PositionService(session=session)
    board: chess.Board = get_board_by_fen(fen=fen)

    position: Position = position_service.get_position_by_board(board)

    moves_stats = position_service.get_next_moves_stats(position=position)

    return SuccessfulDataResponse(message="Next moves stats retrieved correctly.",
                                  data=moves_stats, success=True)


@position_router.get("/svg", status_code=200)
def get_position_svg(move: str, color: str, fen: str, session: Session = Depends(get_db)):
    position_service = PositionService(session=session)
    board: chess.Board = get_board_by_fen(fen=fen)

    position: Position = position_service.get_position_by_board(board)

    color = get_color(color=color)

    position_svg = position_service.get_position_svg(
        position=position, move=move, color=color
    )

    if not position_svg:
        raise HTTPException(status_code=400, detail=f"Move {move} is not valid in this position.")

    return StreamingResponse(
        content=position_svg,
        media_type="image/svg+xml",
    )
