from sqlalchemy import Column
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/postgres" # URL подключения к PostgreSQL

engine = create_async_engine(DATABASE_URL, echo=True) # Создаем асинхронный движок для работы с PostgreSQL

Async_Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False) # Создаем фабрику для сессий

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)