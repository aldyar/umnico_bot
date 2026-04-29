from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

class EditAccount(StatesGroup):
    waiting_for_prompt = State()