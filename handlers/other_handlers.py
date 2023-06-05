from aiogram import Router
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state


router: Router = Router()


@router.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.answer(
        f'{message.from_user.first_name}\nБот не знає як реагувати на 🤷‍♂️ :\n<b>{message.text}</b>')
