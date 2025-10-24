from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AbsId(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"


class AbsCreated(Base):
    __abstract__ = True

    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, index=True)