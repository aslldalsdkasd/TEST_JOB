# КАК ЗАПУСТИТЬ
****
1. создать env файл создать параметры из [env.template](env.template)
2. запутить [docker-compose.yml](docker-compose.yml) командой docker compose up --build
3. для запуска тестов docker-compose --profile test up
****
## ПРИМЕРЫ РАБОТЫ ##
****
/auth/register

Принимает json с данными {"login": str, "password"" str}
Возвращает  

return {"message": "Пользователь успешно зарегистрирован"} при успешном запросе 

При 400 ошибке возвращает

raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином существует"
        )
****
/auth/login 

Принимает  json {"login": str, "password"" str}

Возвращает 

return TokenResponse(access_token=token) 

при ошибке 401 
raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

****
/add/room
принимает токен авторизации 
room_data: RoomCreate схему с полями 
    reservation: bool
    booked_from: time
    booked_to: time

возвращает return JSONResponse({
        'room': {
            'id': new_room.id,
            'reservation': new_room.reservation,
            'booked_from': str(new_room.booked_from),
            'booked_to': str(new_room.booked_to)
        },
        'status': 'created',
        'message': 'Room created'})

При ошибке 401

raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Нет прав доступа")

если нет данных для создания комнаты

raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не корректные данные переговорной")

****
/room/booking(POST)

Принимает ID комнаты, токен авторизации
возвращает  

return JSONResponse({
        "Booking_room": {
            "id": new_booking_room.id,
            'user_id': new_booking_room.user_id,
            'room_id': new_booking_room.room_id
        },
        "status": "booking",
        "message": "Booking created",
    })

так же обрабатывает ошибку на отсутствия токена или отсутствия прав и отсутсвия ID комнаты

****
/room/booking(GET)

Принимает параметры время бронирования и токен

Возвращает return {
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

так же обрабатывает ошибку на отсутствия токена или прав и отсутсвия времени бронирования

****
/room/booking(DELETE)
Принимает токен и ID брони

Возвращает 

return JSONResponse({
    'message': 'Бронь отменена',
    'status': 'success',
    })

Делает проверку на наличи прав и проверку на существование брони

****
/admin/room/booking

Принимает ID брони и токен

Возвращает 

return JSONResponse({
        'message': 'Бронь отменена',
        'status': 'success',
    })

Делает проверку на наличие брони и наличие прав администратора
Роут для удаления любых броней для админов


