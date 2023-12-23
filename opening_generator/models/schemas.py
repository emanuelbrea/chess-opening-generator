from typing import Optional

from pydantic import BaseModel


class ColorRequest(BaseModel):
    color: str


class InputRequest(BaseModel):
    move: str
    fen: str


class MessageInput(BaseModel):
    message: str
    email: str
    name: str
    rating: int


class SuccessfulResponse(BaseModel):
    message: str
    success: bool


class SuccessfulDataResponse(SuccessfulResponse):
    data: dict


class UserInput(BaseModel):
    first_name: str
    email: str
    last_name: str


class UserData(UserInput):
    age: int
    playing_since: int
    last_name: str


class UserStyle(BaseModel):
    popularity: Optional[float]
    fashion: Optional[float]
    risk: Optional[float]
    rating: Optional[int]

