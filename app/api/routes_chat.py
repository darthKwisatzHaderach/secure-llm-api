"""Эндпоинты /chat/* — защищены JWT; бизнес-логика в usecase."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_chat_usecase, get_current_user_id
from app.schemas.chat import ChatMessagePublic, ChatRequest, ChatResponse
from app.usecases.chat import ChatUsecase

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user_id: Annotated[int, Depends(get_current_user_id)],
    usecase: Annotated[ChatUsecase, Depends(get_chat_usecase)],
) -> ChatResponse:
    answer = await usecase.ask(
        user_id,
        prompt=body.prompt,
        system=body.system,
        max_history=body.max_history,
        temperature=body.temperature,
    )
    return ChatResponse(answer=answer)


@router.get("/history", response_model=list[ChatMessagePublic])
async def history(
    user_id: Annotated[int, Depends(get_current_user_id)],
    usecase: Annotated[ChatUsecase, Depends(get_chat_usecase)],
) -> list[ChatMessagePublic]:
    rows = await usecase.get_history(user_id)
    return [ChatMessagePublic.model_validate(m) for m in rows]


@router.delete("/history", status_code=204)
async def clear_history(
    user_id: Annotated[int, Depends(get_current_user_id)],
    usecase: Annotated[ChatUsecase, Depends(get_chat_usecase)],
) -> None:
    await usecase.clear_history(user_id)
