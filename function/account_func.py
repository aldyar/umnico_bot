from database.models import async_session
from database.models import Account
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime, timedelta

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner

class AccountFunc():

    @connection
    async def get_one(session,id):
        result = await session.scalar(select(Account).where(Account.id ==id))
        return result
    

    @connection
    async def get_all(session):
        result = await session.scalars(select(Account))
        return result.all()


    @connection
    async def update_one(session, id: str, **kwargs):
        await session.execute(update(Account).where(Account.id == str(id)).values(**kwargs))
        await session.commit()

    
    @connection
    async def add_one(session, id,type,login):
        new_acc = Account(
            id=id,
            type=type,
            login=login)
        session.add(new_acc)
        await session.commit()