from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from opening_generator.db import get_db
from opening_generator.db.user_dao import UserDao
from opening_generator.models import User
from opening_generator.services.auth_service import AuthService

auth_service = AuthService()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user(session: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    user_claims = auth_service.get_user_claims(token=token)

    if not user_claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing user claims",
        )

    email = user_claims.get("email")
    user_dao = UserDao(session=session)
    try:

        user = user_dao.get_user(email=email)
    except NoResultFound:
        first_name = user_claims.get("given_name", "")
        last_name = user_claims.get("family_name", "")
        user = user_dao.create_user(
            first_name=first_name, last_name=last_name, email=email
        )

    return user
