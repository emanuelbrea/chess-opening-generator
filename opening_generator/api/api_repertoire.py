import chess
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from opening_generator.api.api_position import (
    get_board_by_fen,
    get_color,
)
from opening_generator.db import get_db
from opening_generator.models import Position, User
from opening_generator.models.schemas import SuccessfulDataResponse, Color
from opening_generator.services.auth import get_user
from opening_generator.services.position_service import PositionService
from opening_generator.services.repertoire_service import RepertoireService

repertoire_router = APIRouter(prefix="/repertoire", tags=["repertoire"])


@repertoire_router.get("", response_model=SuccessfulDataResponse, status_code=200)
def get_user_repertoire(color: Color, fen: str, session: Session = Depends(get_db), user: User = Depends(get_user)):
    repertoire_service = RepertoireService(session=session)
    color: bool = get_color(color)
    board: chess.Board = get_board_by_fen(fen)
    position_service = PositionService(session=session)
    position: Position = position_service.get_position_by_board(board)
    depth = board.fullmove_number

    moves = repertoire_service.get_repertoire_moves(
        position=position, user=user, color=color, depth=depth
    )
    return SuccessfulDataResponse(message="Repertoire retrieved correctly.", data=moves, success=True)


@repertoire_router.get("/info", response_model=SuccessfulDataResponse, status_code=200)
def get_user_repertoire_info(session: Session = Depends(get_db), user: User = Depends(get_user)):
    repertoire_service = RepertoireService(session=session)

    info = repertoire_service.get_user_repertoire_info(user=user)
    return SuccessfulDataResponse(message="Repertoire info retrieved correctly.", data=info, success=True)


@repertoire_router.post("", response_model=SuccessfulDataResponse, status_code=201)
def create_user_repertoire(color: Color, session: Session = Depends(get_db),
                           user: User = Depends(get_user)):
    color = get_color(color)
    repertoire_service = RepertoireService(session=session)
    position_service = PositionService(session=session)

    initial_position = position_service.retrieve_initial_position()
    repertoire_service.create_user_repertoire(
        position=initial_position, user=user, color=color
    )
    return SuccessfulDataResponse(message="Repertoire created correctly.", data={}, success=True)


@repertoire_router.put("", response_model=SuccessfulDataResponse, status_code=200)
def edit_user_repertoire(color: Color, fen: str, move: str, session: Session = Depends(get_db),
                         user: User = Depends(get_user)):
    color: bool = get_color(color)
    board: chess.Board = get_board_by_fen(fen)
    position_service = PositionService(session=session)
    position: Position = position_service.get_position_by_board(board)
    depth = board.fullmove_number
    repertoire_service = RepertoireService(session=session)

    moves = repertoire_service.update_user_repertoire(
        position=position, user=user, color=color, new_move=move
    )
    if len(moves) == 0:
        raise HTTPException(status_code=400, detail="Repertoire could not be updated. Try with another move.")

    moves = repertoire_service.get_repertoire_moves(
        position=position, user=user, color=color, depth=depth
    )
    return SuccessfulDataResponse(message=f"Repertoire updated correctly after {position}.",
                                  data=moves, success=True)


@repertoire_router.delete("", response_model=SuccessfulDataResponse, status_code=200)
def delete_user_repertoire(color: Color, session: Session = Depends(get_db),
                           user: User = Depends(get_user)):
    color = get_color(color)
    repertoire_service = RepertoireService(session=session)

    repertoire_service.delete_user_repertoire(user=user, color=color)
    return SuccessfulDataResponse(message=f"{color} repertoire deleted correctly.",
                                  data={}, success=True)


@repertoire_router.put("/rival", response_model=SuccessfulDataResponse, status_code=201)
def add_rival_move(color: Color, fen: str, move: str, session: Session = Depends(get_db),
                   user: User = Depends(get_user)):
    color: bool = get_color(color)
    board: chess.Board = get_board_by_fen(fen)
    position_service = PositionService(session=session)
    position: Position = position_service.get_position_by_board(board)
    repertoire_service = RepertoireService(session=session)

    moves = repertoire_service.add_rival_move_to_repertoire(
        position=position, user=user, color=color, move_san=move
    )
    return SuccessfulDataResponse(message=f"Repertoire updated correctly after {position.fen}.",
                                  data=moves, success=True)


@repertoire_router.delete("/rival", response_model=SuccessfulDataResponse, status_code=200)
def remove_rival_move(color: Color, fen: str, move: str, session: Session = Depends(get_db),
                      user: User = Depends(get_user)):
    color: bool = get_color(color)
    board: chess.Board = get_board_by_fen(fen)
    position_service = PositionService(session=session)
    position: Position = position_service.get_position_by_board(board)
    repertoire_service = RepertoireService(session=session)

    moves = repertoire_service.remove_rival_move_from_repertoire(
        position=position, user=user, color=color, move_san=move
    )
    return SuccessfulDataResponse(message=f"Move {move} deleted correctly from user repertoire.",
                                  data=moves, success=True)


@repertoire_router.patch("", response_model=SuccessfulDataResponse, status_code=200)
def add_variant_to_repertoire(color: Color, fen: str, session: Session = Depends(get_db),
                              user: User = Depends(get_user)):
    color: bool = get_color(color)
    board: chess.Board = get_board_by_fen(fen)
    position_service = PositionService(session=session)
    position: Position = position_service.get_position_by_board(board)
    depth = board.fullmove_number
    repertoire_service = RepertoireService(session=session)

    repertoire_service.add_variant_to_repertoire(position=position, user=user, color=color)
    moves = repertoire_service.get_repertoire_moves(
        position=position, user=user, color=color, depth=depth
    )
    return SuccessfulDataResponse(message=f"Variant added correctly after {position.fen}.",
                                  data=moves, success=True)
