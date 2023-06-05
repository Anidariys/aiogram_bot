from lexicon.lexicon import (INVALID_LEXICON, 
    CHOICE_LEXICON, DB_ROWS, MAIN_LEXICON)
from filters.filters import ValidName
from FSM.FSM import FSMDeletClient
from aiogram import Router
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from database.database import get_user, delete_client
from keyboards.kb import bild_reply_kb


router: Router = Router()


@router.callback_query(Text(
    text=["NP", "delivery", "buss"]), StateFilter(FSMDeletClient.get_group))
async def choice_delete_clent_group(
    callback: CallbackQuery, 
    state: FSMContext):
    await state.set_state(FSMDeletClient.get_name)
    await state.update_data(group=CHOICE_LEXICON[callback.data])
    await callback.message.delete()
    await callback.message.answer(
        text="Вкажіть прізвище та імя клієнта 🧑‍⚕️", reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(FSMDeletClient.get_name), ValidName())
async def get_client_name(message: Message, state: FSMContext):
    data = " ".join(elem.title() for elem in message.text.split())
    database = await state.get_data()
    user = get_user(data, database["group"])
    kb = bild_reply_kb(MAIN_LEXICON)
    if user is None:
        await message.answer(
            text=f"{INVALID_LEXICON['user_not_found']}")
    else:
        delete_client(data, database["group"])
        await message.answer(
            text=f"Клієнтa -> <b>{data}</b>\nВидалено 🗑️", reply_markup=kb)
        await state.clear()


@router.message(StateFilter(FSMDeletClient.get_name))
async def incorect_user_name(message: Message):
    text = message.text
    await message.reply(text=f"{INVALID_LEXICON['invalid_name']}<b>{text}</b>")
