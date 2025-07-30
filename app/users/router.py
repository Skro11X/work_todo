from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.users.repository import UserRepository
from app.users.shemas import CreatUser, LoginUser
from app.users.utils.password import check_password
from app.users.utils.token import create_tokens

router = APIRouter()


# todo сделать нормальное логирование событий для отслеживания работы
@router.post("/register", response_model=CreatUser, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: CreatUser, session: AsyncSession = Depends(get_session)):
    """Регистрация пользователя"""
    user_repo = UserRepository(session)
    try:
        user_instance = await user_repo.create(user_in.model_dump())
        if not user_instance:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось создать задачу",
            )
        return user_instance  # todo сделать возвращение понятного тела как в случае с возникновением ошибок
    except ValueError as e:
        logger.error(f"Validation error creating user: {str(e)}")
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


@router.post("/login", response_model=LoginUser, status_code=status.HTTP_200_OK)
async def login(
    response: Response,
    user_data: LoginUser,
    session: AsyncSession = Depends(get_session),
):
    user_rep = UserRepository(session)
    user = await user_rep.get(user_data.username)
    if not (
        user
        and check_password(password=user_data.password, hashed_password=user.password)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Неверная почта или пароль"
        )
    access_token, refresh_token = create_tokens()
    response.set_cookie(
        key="user_access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    response.set_cookie(
        key="user_refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return {
        "ok": True,
        "message": "Авторизация успешна!",
    }  # todo знаю что говно переделаю я хотел хоть что-то доделать


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("user_access_token")
    response.delete_cookie("user_refresh_token")
    return {"message": "Пользователь успешно вышел из системы"}
