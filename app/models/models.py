from sqlalchemy import Column, String

from app.models.base import AbsId, AbsCreated


class User(AbsId, AbsCreated):
    __tablename__ = 'users'

    login = Column(String(100), nullable=False, index=True, unique=True)
    hashed_password = Column(String(100), nullable=False, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    second_name = Column(String(50), nullable=False)
