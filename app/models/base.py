from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

def utcnow():
    return func.timezone('UTC', func.utcnow())

class AbsId(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class AbsCreated(Base):
    __abstract__ = True