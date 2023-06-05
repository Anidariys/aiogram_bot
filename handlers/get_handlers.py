from lexicon.lexicon import (INVALID_LEXICON, 
    CHOICE_LEXICON, DB_ROWS, MAIN_LEXICON)
from filters.filters import ValidName
from FSM.FSM import FSMGetClientData
from keyboards.kb import bild_reply_kb
from aiogram import Router
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from database.database import get_user, get_all_users


router: Router = Router()


@router.callback_query(Text(text=["NP", "delivery", "buss"]), StateFilter(FSMGetClientData.get_group))
async def choice_update_group(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMGetClientData.get_name)
    await state.update_data(group=CHOICE_LEXICON[callback.data])
    await callback.message.delete()
    await callback.message.answer(
        text="Вкажіть прізвище та імя клієнта 🧑‍⚕️", reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(FSMGetClientData.get_name))
async def get_client_names(message: Message, state: FSMContext):
    data = " ".join(elem.title() for elem in message.text.split())
    database = await state.get_data()
    users = get_all_users(data, database["group"])
    kb = bild_reply_kb(MAIN_LEXICON)

    if not users:
        await message.answer(
            text=f"{INVALID_LEXICON['user_not_found']}")
    else:
        for user in users:
            output = "\n".join([f'{DB_ROWS[k]}: {user[k]}' for k, _ in DB_ROWS.items() if k in user])
            if "photo" in user:
                await message.answer_photo(
                photo=user["photo"],
                caption=output, 
                reply_markup=kb)
            else:
                await message.answer(text=output, reply_markup=kb)
            if "location" in user:
                await message.answer_location(user["location"]["latitude"], user["location"]["longitude"])
        await state.clear()



# @router.message(StateFilter(FSMGetClientData.get_name), ValidName())
# async def get_client_name(message: Message, state: FSMContext):
#     data = " ".join(elem.title() for elem in message.text.split())
#     database = await state.get_data()
#     user = get_user(data, database["group"])
#     kb = bild_reply_kb(MAIN_LEXICON)

#     if user is None:
#         await message.answer(
#             text=f"{INVALID_LEXICON['user_not_found']}")
#     else:
#         output = "\n".join([f'{DB_ROWS[k]}: {user[k]}' for k, _ in DB_ROWS.items() if k in user])
#         if "photo" in user:
#             await message.answer_photo(
#             photo=user["photo"],
#             caption=output, 
#             reply_markup=kb)
#         else:
#             await message.answer(text=output, reply_markup=kb)
#         if "location" in user:
#             await message.answer_location(user["location"]["latitude"], user["location"]["longitude"])
#         await state.clear()


# @router.message(StateFilter(FSMGetClientData.get_name))
# async def incorect_user_name(message: Message):
#     text = message.text
#     await message.reply(text=f"{INVALID_LEXICON['invalid_name']}<b>{text}</b>")

