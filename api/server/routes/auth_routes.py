from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.database.connection import get_session_db
from api.database.models import User, Role
from api.server.JWT_func import get_password_hash, verify_password, create_access_token, get_admin_user

from api.server.schema.auth_schema import UserSchema, TokenResponse

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register")
async def register_user(
        user_data: UserSchema,
        db: AsyncSession = Depends(get_session_db)
):
    """Регистрация нового пользователя по стандарту с ролью Manager"""
    existing = await db.execute(
        select(User)
        .where(User.login == user_data.login)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином существует"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        login=user_data.login,
        hashed_password=hashed_password
    )
    role_result = await db.execute(
        select(Role).where(Role.name == "manager")
    )

    user_role = role_result.scalar_one_or_none()
    if user_role:
        new_user.roles = [user_role]

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "Пользователь успешно зарегистрирован"}

@auth_router.post("/login")
async def login_user(
        login_data: UserSchema,
        db: AsyncSession = Depends(get_session_db),
):
    """Вход пользователя"""

    existing = await db.execute(
        select(User).where(User.login == login_data.login)
    )
    user = existing.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)

@auth_router.post("/admin/create-user")
async def create_user_by_admin(
        user_data: UserSchema,
        role_name:str = "admin",
        admin: User = Depends(get_admin_user),
        db: AsyncSession = Depends(get_session_db),
):
    """Создание пользователя с указанной ролью (только для админов)"""
    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Нет прав')
    existing = await db.execute(
        select(User).where(User.login == user_data.login)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже существует"
        )

    role_result = await db.execute(
        select(Role).where(Role.name == role_name)
    )

    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Роль '{role_name}' не найдена"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        login=user_data.login,
        hashed_password=hashed_password,
        roles=[role]
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": f"Пользователь создан с ролью '{role_name}'"}



@auth_router.post('/admin/register')
async def admin_register_user(
        user_data: UserSchema,
        db: AsyncSession = Depends(get_session_db),
):
    """Регистрация администратора"""
    existing = await db.execute(
        select(User)
        .where(User.login == user_data.login)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином существует"
        )

    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        login=user_data.login,
        hashed_password=hashed_password
    )
    role_result = await db.execute(
        select(Role).where(Role.name == "admin")
    )

    user_role = role_result.scalar_one_or_none()
    if user_role:
        new_user.roles = [user_role]

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "Пользователь успешно зарегестрирован"}