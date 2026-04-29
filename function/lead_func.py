from database.models import async_session
from database.models import Leads
from sqlalchemy import select, update, delete, desc
from decimal import Decimal
from datetime import datetime, timedelta

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner

class LeadsFunc():

    @connection
    async def get_one(session,lead_id):
        result = await session.scalar(select(Leads).where(Leads.lead_id ==lead_id))
        return result
    
    
    @connection
    async def update_one(session, lead_id: str, **kwargs):
        await session.execute(update(Leads).where(Leads.lead_id == str(lead_id)).values(**kwargs))
        await session.commit()

    
    @connection
    async def add_one(session, lead_id,client_name):
        new_lead = Leads(
            lead_id=str(lead_id),
            client_name=client_name)
        session.add(new_lead)
        await session.commit()