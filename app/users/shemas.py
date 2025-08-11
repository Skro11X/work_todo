from pydantic import BaseModel, ConfigDict, Field, model_validator
from fastapi import HTTPException, status

from app.users.utils.password import hash_password


class UserBase(BaseModel):
    username: str = Field(
        min_length=3, max_length=32, description="Имя провфиля пользователя"
    )

    model_config = ConfigDict(from_attributes=True)


class CreatUser(UserBase):
    password: str = Field(min_length=8, max_length=16, description="Пароль")
    password_confirm: str = Field(
        min_length=8, max_length=16, description="Подтверждение пароля"
    )

    @model_validator(mode="after")
    def check_pass(self):
        if self.password_confirm != self.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ошибка не совпадают пароли",
            )
        self.password: bytes = hash_password(self.password)
        return self


class AuthUserResponse(BaseModel):
    is_auth: bool = True


class LoginUser(UserBase):
    password: str = Field(min_length=8, max_length=16, description="Пароль")


class UserUpdate(UserBase):
    pass
