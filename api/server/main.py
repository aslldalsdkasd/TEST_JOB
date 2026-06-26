from fastapi import FastAPI
from contextlib import asynccontextmanager
import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.connection import engine
from api.database.models import Base, Role
from api.server.routes.routes_room import router
from api.server.routes.auth_routes import auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    for i in range(3):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print(' Таблицы созданы')

    async with AsyncSession(engine) as db:
        default_roles = [
            Role(name='admin', descriptions='Админимтратор'),
            Role(name='manages',descriptions='Менеджер')
        ]
        for role in default_roles:
            res = await db.execute(
                select(Role).where(Role.name == role.name)
            )
            existing_role = res.scalar_one_or_none()
            if not existing_role:
                db.add(role)
        await db.commit()
        print("Роли созданы")
    yield

    # Закрываем соединение
    print(' Завершение приложения...')
    await engine.dispose()
    print(' Соединение закрыто')

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)
app.include_router(router)

