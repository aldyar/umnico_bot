from sqlalchemy import String, Integer, Boolean,Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from sqlalchemy.ext.asyncio import AsyncAttrs,async_sessionmaker,create_async_engine,AsyncSession

#URL_DB = "mysql+aiomysql://root:1234@localhost:3306/umnico_bot"
URL_DB = "mysql+aiomysql://root:1234@localhost:3306/umnico"
engine = create_async_engine(url=URL_DB,echo=False,pool_size=20,max_overflow=10,pool_timeout=60)

async_session = async_sessionmaker(engine,class_=AsyncSession)

class Base(AsyncAttrs,DeclarativeBase):
    pass

class Messages(Base):
    __tablename__ = 'messages'

    id:Mapped[int] = mapped_column(Integer,autoincrement=True,primary_key=True)
    lead_id: Mapped[str] = mapped_column(String(255), nullable=True)
    msg_id:Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[str] = mapped_column(String(100), nullable=True)


class Leads(Base):
    __tablename__='leads'


    id:Mapped[int] = mapped_column(Integer,autoincrement=True,primary_key=True)
    lead_id:Mapped[str] = mapped_column(String(255), nullable=True)
    is_active:Mapped[bool] = mapped_column(Boolean,default=True)
    lead_status:Mapped[str] = mapped_column(String(255), nullable=True)
    client_name:Mapped[str] = mapped_column(String(255), nullable=True)


class Account(Base):
    __tablename__='account'

    id:Mapped[str] = mapped_column(String(255),primary_key=True)
    type:Mapped[str] = mapped_column(String(255), nullable=True)
    login:Mapped[str] = mapped_column(String(255), nullable=True)
    prompt:Mapped[str] = mapped_column(Text(255), nullable=True)
    ai_is_active:Mapped[bool] = mapped_column(Boolean,default=True)

    
async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)