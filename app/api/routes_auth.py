"""Эндпоинты /auth/* — только вызов usecase, ошибки → глобальные exception handlers."""

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_usecase, get_current_user_id
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUsecase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
async def register(
    body: RegisterRequest,
    usecase: Annotated[AuthUsecase, Depends(get_auth_usecase)],
) -> UserPublic:
    user = await usecase.register(email=str(body.email), password=body.password)
    return UserPublic.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    usecase: Annotated[AuthUsecase, Depends(get_auth_usecase)],
) -> TokenResponse:
    # username в OAuth2 — наш email
    token = await usecase.login(email=form.username, password=form.password)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserPublic)
async def me(
    user_id: Annotated[int, Depends(get_current_user_id)],
    usecase: Annotated[AuthUsecase, Depends(get_auth_usecase)],
) -> UserPublic:
    user = await usecase.get_profile(user_id)
    return UserPublic.model_validate(user)
