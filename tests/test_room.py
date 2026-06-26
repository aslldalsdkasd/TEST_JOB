import pytest
from httpx import AsyncClient


async def test_create_room_success(async_client: AsyncClient, auth_token: str):
    """Тест на создание комнат с токеном"""
    resp = await async_client.post(
        '/add/room',
        json={
            'reservation': True,
            'booked_from': '14:13:00',
            'booked_to': '14:13:10',
        },
        headers={"Authorization": f"Bearer {auth_token}"},

    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['room']['reservation'] == True
    assert data['room']['booked_from'] == '14:13:00'
    assert data['room']['booked_to'] == '14:13:10'
    assert data['status'] == 'created'
    assert data['message'] == 'Room created'

async def test_create_room_without_auth(async_client: AsyncClient):
    """Тест на создание комнат без токена"""
    resp = await async_client.post(
        '/add/room',
        json={
            'reservation': True,
            'booked_from': '14:13:00',
            'booked_to': '14:13:10',
        }
    )
    assert resp.status_code == 401
    data = resp.json()
    assert data['detail'] == "Not authenticated"

async def test_get_rooms_success(async_client: AsyncClient, auth_token: str):
    """Тест на получение комнат с токеном"""
    resp = await async_client.get(
        '/room/booking',
        headers={"Authorization": f"Bearer {auth_token}"},
        params={'booked_from': '15:14:13', 'booked_to': '15:14:13'},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['count'] == 3
    assert data['status'] == 'success'
    assert data['data'][0]['id'] == 1
    assert data['data'][0]['reservation'] == False
    assert data['data'][0]['booked_from'] == '15:14:13'
    assert data['data'][0]['booked_to'] == '15:14:13'

async def test_add_booking_with_token(async_client: AsyncClient, auth_token: str):
    """Тест на добавление брони с токеном"""
    resp = await async_client.post(
        '/room/booking',
        params={'room_data': 2},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['Booking_room']['id'] == 4
    assert data['Booking_room']['user_id'] == 1
    assert data['Booking_room']['room_id'] == 2
    assert data['status'] == 'booking'
    assert data['message'] == 'Booking created'

async def test_delete_booking(async_client: AsyncClient, auth_token: str):
    """Тест на удаление брони"""
    resp = await async_client.delete(
        '/room/booking',
        params={'booking_id': 2},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['message'] == 'Бронь отменена'
    assert data['status'] == 'success'

async def test_admin_delete_booking(async_client: AsyncClient, auth_token: str):
    """Тест на удаление админом чужой юрони"""
    resp = await async_client.delete(
        '/admin/room/booking',
        params={'booking_id': 3},
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data['message'] == 'Бронь отменена'
    assert data['status'] == 'success'




