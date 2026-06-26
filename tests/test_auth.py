import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_success(async_client: AsyncClient):
    """Тест на успешную регистрацию"""
    resp = await async_client.post(
        "/auth/register",
        json= {"login": "user", "password": "pipa"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "Пользователь успешно зарегистрирован"

async def test_register_duplicate_login(async_client: AsyncClient):
    """Тест на регистрацию с сущесвующим логином"""
    resp = await async_client.post(
        "/auth/register",
        json= {"login": "admin", "password": "admin"}
    )
    assert resp.status_code == 400
    data = resp.json()
    assert "существует" in data.get("detail")

async def test_login_success(async_client: AsyncClient):
    """Тест успешной авторизации"""
    resp = await async_client.post(
        '/auth/login',
        json= {"login": 'admin', 'password' : 'admin'}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'

async def test_protected_route_without_token(async_client: AsyncClient):
    """Тест на работу роута без токена авторизации"""
    resp = await async_client.get('/room/booking')
    assert resp.status_code == 401
    data = resp.json()
    assert data['detail'] == "Not authenticated"

async def test_protected_route_with_token(async_client: AsyncClient, auth_token: str):
    """Тест работы роута с токеном авторизации"""
    resp = await async_client.get(
        '/room/booking',
        params={"booked_to": "14:15:13",
                'booked_from': "14:15:13"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['detail'] == 'Ничего не найденно'


