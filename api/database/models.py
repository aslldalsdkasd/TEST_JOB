from sqlalchemy import Column, Integer, String, Boolean,  ForeignKey, Table
from sqlalchemy.orm import Mapped, DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import TIME



class Base(DeclarativeBase):
    pass

class Room(Base):
    """Таблица комнат"""
    __tablename__ = 'room'
    id: Mapped[int] = Column(Integer, primary_key=True)
    reservation: Mapped[bool] = Column(Boolean, default=False)
    booked_from = Column(TIME(precision=0), nullable=False)
    booked_to = Column(TIME(precision=0), nullable=False)

    bookings = relationship("Booking", back_populates="room")
class User(Base):
    """Таблица пользователей"""
    __tablename__ = 'user'
    id: Mapped[int] = Column(Integer, primary_key=True)
    login: Mapped[String] = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)

    roles = relationship("Role", secondary="user_role", back_populates="users")
    bookings = relationship("Booking", back_populates="user")

class Role(Base):
    """Таблица ролей"""
    __tablename__ = 'role'
    id: Mapped[int] = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    descriptions = Column(String(255), nullable=True,)
    users = relationship("User", secondary='user_role', back_populates="roles")


user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('role.id'), primary_key=True)
)


class Booking(Base):
    """Таблица бронирования"""
    __tablename__ = 'booking'
    id: Mapped[int] = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    room_id = Column(Integer, ForeignKey('room.id'), nullable=False)


    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
