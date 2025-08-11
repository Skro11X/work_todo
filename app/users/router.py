import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.users.repository import UserRepository
from app.users.shemas import CreatUser, LoginUser, AuthUserResponse, UserBase
from app.users.utils.password import check_password
from app.users.utils.token import create_tokens
from app.users.depends import get_user_by_token

router = APIRouter()


# todo сделать нормальное логирование событий для отслеживания работы
@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(user_in: CreatUser, session: AsyncSession = Depends(get_session)):
    """Регистрация пользователя"""
    user_repo = UserRepository(session)
    try:
        user_instance = await user_repo.create(
            user_in.model_dump(exclude={"password_confirm"})
        )
        if not user_instance:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать задачу",
            )
        return AuthUserResponse()
    except ValueError as e:
        logger.error(f"Validation error creating user: {str(e)}")
        print(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Ошибка валидации при регистрации пользователя: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка создания пользователя: {str(e)}",
        )


@router.post("/login", response_model=UserBase, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    user_data: LoginUser,
    session: AsyncSession = Depends(get_session),
):
    user_rep = UserRepository(session)
    user = await user_rep.get_by_username(user_data.username)
    if not (
        user
        and check_password(password=user_data.password, hashed_password=user.password)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверная почта или пароль"
        )
    tokens = create_tokens({"username": user.username})
    response.set_cookie(
        key="user_access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="lax",
    )

    response.set_cookie(
        key="user_refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return UserBase(username=user.username)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {"message": "Пользователь успешно вышел из системы"}


@router.get("/users/me", response_model=UserBase)
async def user_info(user: UserBase = Depends(get_user_by_token)):
    return user
