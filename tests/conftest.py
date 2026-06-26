from datetime import time

import pytest
from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from api.database.connection import get_session_db
from api.server.JWT_func import get_password_hash
from api.server.main import app
from api.database.models import User, Role, Base, Booking, Room

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="session")
async def async_client(test_engine):
    async_session = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with async_session() as session:
        async with session.begin() as conn:
            admin_role = Role(name='admin', descriptions='Administrator')
            manager_role = Role(name='manager', descriptions='Manager')
            session.add_all([admin_role, manager_role])
            admin_user = User(
                id=1,
                login='admin',
                hashed_password=get_password_hash('admin'),
                is_active=True,
                roles=[admin_role]
            )
            manager_user = User(
                id=2,
                login='manager',
                hashed_password=get_password_hash('manager'),
                is_active=True,
                roles=[manager_role]
            )
            session.add_all([admin_user, manager_user])
            new_room_3 = Room(
                id=3,
                reservation=True,
                booked_from=time(15, 14, 13),
                booked_to=time(15, 14, 13),
            )
            new_room = Room(
                id=1,
                booked_from=time(15, 14, 13),
                booked_to=time(15, 14, 13))
            new_room_2 = Room(
                id=2,
                reservation=True,
                booked_from=time(15, 14, 13),
                booked_to=time(15, 14, 13))
            session.add_all([new_room, new_room_2, new_room_3])
            new_booking = Booking(id=2,user_id=admin_user.id, room_id=new_room.id)
            new_booking_2 = Booking(id=3,user_id=manager_user.id, room_id=new_room_3.id)
            session.add_all([new_booking, new_booking_2])
    async def override_get_db():
        async with async_session() as session:
            yield session
    app.dependency_overrides[get_session_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
async def auth_token(async_client: AsyncClient):
    response = await async_client.post('/auth/login', json={"login": "admin", "password": "admin"})
    data = response.json()
    return data.get("access_token")

