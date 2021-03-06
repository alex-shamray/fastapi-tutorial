from fastapi import Depends, HTTPException, Security, status
from fastapi.security import SecurityScopes, HTTPBasicCredentials
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from .basic_auth import auth_scheme
from .db import get_db
from .oauth2 import oauth2_password_scheme, oauth2_authorization_code_scheme


def get_current_user(
    security_scopes: SecurityScopes,
    db: Session = Depends(get_db),
    password_token: str = Depends(oauth2_password_scheme),
    auth_code_token: str = Depends(oauth2_authorization_code_scheme),
    credentials: HTTPBasicCredentials = Depends(auth_scheme),
) -> models.User:
    token = password_token or auth_code_token
    if token:
        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        else:
            authenticate_value = f"Bearer"
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
            token_scopes = payload.get("scopes", [])
            token_data = schemas.TokenPayload(scopes=token_scopes, user_id=user_id)
        except (jwt.JWTError, ValidationError):
            raise credentials_exception
        user = crud.user.get(db, id=token_data.user_id)
        if not user:
            raise credentials_exception
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        return user
    elif credentials:
        user = crud.user.authenticate(
            db, email=credentials.username, password=credentials.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return user


def get_current_active_user(
    current_user: models.User = Security(get_current_user, scopes=["me"]),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user
