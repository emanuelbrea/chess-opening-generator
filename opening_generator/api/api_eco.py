import chess
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from opening_generator.api.api_position import get_board_by_fen
from opening_generator.db import get_db
from opening_generator.models import Position, EcoCode
from opening_generator.models.schemas import SuccessfulDataResponse
from opening_generator.services.eco_code_service import EcoCodeService
from opening_generator.services.position_service import PositionService

eco_router = APIRouter(prefix="/eco", tags=["eco"])


@eco_router.get("/", response_model=SuccessfulDataResponse, status_code=200)
def get_eco_code(fen: str, session: Session = Depends(get_db)):
    eco_service = EcoCodeService(session=session)
    board: chess.Board = get_board_by_fen(fen)
    position_service = PositionService(session=session)

    position: Position = position_service.get_position_by_board(board)

    eco_code: EcoCode = eco_service.get_eco_code(position=position)

    if not eco_code:
        raise HTTPException(status_code=400, detail="Eco code not found for position.")

    eco_code_desc = dict(
        eco_code=eco_code.eco_code, main_line=eco_code.main_line, name=eco_code.name
    )
    return SuccessfulDataResponse(message="Eco code found for position.",
                                  data=eco_code_desc, success=True)
