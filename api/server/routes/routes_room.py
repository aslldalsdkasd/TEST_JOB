from datetime import time

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from starlette import status
from starlette.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_400_BAD_REQUEST


from api.database.models import Room, User, Booking
from sqlalchemy.ext.asyncio import AsyncSession
from api.server.JWT_func import get_current_user, get_admin_user
from api.server.schema.room_schema import RoomCreate
from api.database.connection import get_session_db


router = APIRouter(tags=['room'])
@router.post('/add/room')
async def add_room(
        room_data: RoomCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session_db),
):
    """Для создания комнат"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет прав доступа")
    if not room_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не корректные данные переговорной")

    new_room = Room(
        reservation=room_data.reservation,
        booked_from=room_data.booked_from,
        booked_to=room_data.booked_to
    )
    try:
        db.add(new_room)
        await db.commit()
        await db.refresh(new_room)
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка при создании переговорной -> {error}")
    return JSONResponse({
        'room': {
            'id': new_room.id,
            'reservation': new_room.reservation,
            'booked_from': str(new_room.booked_from),
            'booked_to': str(new_room.booked_to)
        },
        'status': 'created',
        'message': 'Room created'})

@router.post('/room/booking')
async def room_booking(
        room_data: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session_db)
):
    """Бронирование комнат"""

    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Нет прав доступа')

    if not room_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Не коректные даные комнаты')
    existing_room = select(Room).where(Room.id == room_data)
    result = await db.execute(existing_room)
    room = result.scalars().one()
    if not room:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Комната не найдена")
    if room.reservation is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Комната уже занята')
    new_booking_room = Booking(
        user_id=current_user.id,
        room_id=room_data
    )
    room.reservation = False
    try:
        db.add(new_booking_room)
        await db.commit()
        await db.refresh(new_booking_room)
    except Exception as error:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Произошла ошибка при бронировании -> {error}")

    return JSONResponse({
        "Booking_room": {
            "id": new_booking_room.id,
            'user_id': new_booking_room.user_id,
            'room_id': new_booking_room.room_id
        },
        "status": "booking",
        "message": "Booking created",
    })

@router.get('/room/booking')
async def get_rooms(
        booked_from: str = Query(..., description="Время начала "),
        booked_to: str = Query(..., description="Время окончания "),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session_db)
):
    """Получени комнат"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет прав доступа")
    try:
        from_time = time.fromisoformat(booked_from)
        to_time = time.fromisoformat(booked_to)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат времени. Используйте HH:MM:SS"
        )
    stmt = select(Room).where(
        Room.booked_from == from_time,
        Room.booked_to == to_time
    )
    result = await db.execute(stmt)
    rooms = result.scalars().all()

    if not rooms:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Ничего не найденно'
        )

    data = []
    return {
        'status': 'success',
        'count': len(rooms),
        'data': [
            {
                "id": room.id,
                'reservation': room.reservation,
                "booked_from": room.booked_from.strftime("%H:%M:%S"),
                "booked_to": room.booked_to.strftime("%H:%M:%S")
            }
            for room in rooms
        ]
    }

@router.delete('/room/booking')
async def delete_booking(
        booking_id: int = Query(..., description='Номер брони'),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_session_db)
):
    """Удаление броней с правами менеджера"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет прав доступа")

    if not booking_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Не корректные данные")


    stmt = select(Booking).where(
        Booking.user_id == current_user.id,
        Booking.id == booking_id
    ).options(selectinload(Booking.user))
    try:
        result = await db.execute(stmt)
        booking = result.scalars().one()
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Проверьте id переговорной')
    if not booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Нельзя удалить чужую бронь")
    await db.delete(booking)
    await db.commit()
    return JSONResponse({
    'message': 'Бронь отменена',
    'status': 'success',
    })

@router.delete('/admin/room/booking')
async def admin_delete_booking(
        booking_id: int = Query(..., description="Номер брони "),
        current_user: User = Depends(get_admin_user),
        db: AsyncSession = Depends(get_session_db)
):
    """Удаление брони с правами админа"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет прав доступа")

    if not booking_id:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Не корректные данные")

    stmt = select(Booking).where(
    Booking.id == booking_id)

    try:
        result = await db.execute(stmt)
        booking = result.scalars().one()
    except Exception as error:
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"В БД нет брони с ID {booking_id}")
    if not booking:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Бронь не найдена')
    await db.delete(booking)
    await db.commit()
    return JSONResponse({
        'message': 'Бронь отменена',
        'status': 'success',
    })