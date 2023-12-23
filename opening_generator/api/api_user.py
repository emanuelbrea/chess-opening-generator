from typing import Union

import chess
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from opening_generator.api.api_position import get_board_by_fen
from opening_generator.db import get_db
from opening_generator.models import User, Style, Position
from opening_generator.models.schemas import InputRequest, MessageInput, SuccessfulResponse, UserInput, \
    SuccessfulDataResponse, UserStyle, UserData
from opening_generator.services.auth import get_user
from opening_generator.services.position_service import PositionService
from opening_generator.services.user_service import UserService

user_router = APIRouter(prefix="/user", tags=["user"])


@user_router.post("", response_model=SuccessfulResponse, status_code=201)
def create_user(user: UserInput, session: Session = Depends(get_db)):
    user_service = UserService(session=session)
    user_service.create_user(first_name=user.first_name, last_name=user.last_name, email=user.email)
    return SuccessfulResponse(success=True, message="User created correctly")


@user_router.put("", response_model=SuccessfulResponse)
def update_user(user_input: Union[UserStyle, UserData], session: Session = Depends(get_db),
                user: User = Depends(get_user)):
    user_service = UserService(session=session)

    user_service.update_user(
        user=user,
        first_name=user_input.first_name,
        last_name=user_input.last_name,
        age=user_input.age,
        playing_since=user_input.playing_since,
    )

    popularity = user_input.popularity
    fashion = user_input.fashion
    risk = user_input.risk
    rating = user_input.rating

    if None not in [popularity, fashion, risk, rating]:
        user_service.update_user_style(
            user=user, popularity=popularity, fashion=fashion, risk=risk, rating=rating
        )
    return SuccessfulResponse(
        success=True,
        message="User updated correctly"
    )


@user_router.get("", response_model=SuccessfulDataResponse, status_code=200)
def get_user(session: Session = Depends(get_db), user: User = Depends(get_user)):
    style: Style = user.style
    user_data = UserData(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        age=user.age,
        playing_since=user.playing_since,
    )

    style_data = UserStyle(
        popularity=style.popularity,
        fashion=style.fashion,
        risk=style.risk,
        rating=style.rating,
    )
    data = {"user": user_data.model_dump(), "style": style_data.model_dump()}
    return SuccessfulDataResponse(message="User retrieved correctly",
                                  data=data, success=True)


@user_router.put("/favorite", response_model=SuccessfulResponse, status_code=200)
def add_favorite_move(body: InputRequest, session: Session = Depends(get_db), user: User = Depends(get_user)):
    user_service = UserService(session=session)
    move = body.move
    fen = body.fen

    board: chess.Board = get_board_by_fen(fen=fen)
    position_service = PositionService(session=session)
    position: Position = position_service.get_position_by_board(board)

    user_service.add_favorite_move(user=user, position=position, move_san=move)

    return SuccessfulResponse(message="Favorite move added correctly", success=True)


@user_router.post("/message", response_model=SuccessfulResponse, status_code=200)
def save_user_message(body: MessageInput, session: Session = Depends(get_db), user: User = Depends(get_user)):
    user_service = UserService(session=session)
    message = body.message
    email = body.email
    name = body.name
    rating = body.rating

    user_service.save_user_message(
        message=message, email=email, name=name, rating=rating
    )

    return SuccessfulResponse(message=f"User message saved correctly for {user.email}", success=True)
