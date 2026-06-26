from datetime import time
from typing import List

from pydantic import BaseModel

class RoomCreate(BaseModel):
    """Схема создания комнаты"""
    reservation: bool
    booked_from: time
    booked_to: time
