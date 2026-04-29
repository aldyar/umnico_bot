from database.models import async_session
from database.models import Messages
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime, timedelta

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner

class MessagesFunc():

    @connection
    async def get_one_by_msg_id(session,msg_id):
        result = await session.scalar(select(Messages).where(Messages.msg_id==msg_id))
        return result
    
    
    @connection
    async def update_config(session, **kwargs):
        await session.execute(update(Messages).values(**kwargs))
        await session.commit()

    
    @connection
    async def add_message(session, lead_id, role, content,msg_id):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_msg = Messages(
            lead_id=str(lead_id),
            role=role,
            content=content,
            date=current_date,
            msg_id=msg_id)
        session.add(new_msg)
        await session.commit()


    @connection
    async def get_last_messages(session, lead_id):
        query = (
            select(Messages)
            .where(Messages.lead_id == str(lead_id))
            .order_by(desc(Messages.id))
            .limit(15)
        )
        
        result = await session.execute(query)
        return result.scalars().all()