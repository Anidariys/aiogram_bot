from aiogram import Router
from aiogram.filters import StateFilter, Text
from lexicon.lexicon import SET_LEXICON, MAIN_LEXICON, INVALID_LEXICON
from filters.filters import ValidName, ValidCity, ValidPhone
from keyboards.kb import bild_reply_kb
from FSM.FSM import FSMBussForm
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from database.database import create_user, get_user


router: Router = Router()


@router.callback_query(Text(text='buss'), StateFilter(default_state))
async def create_buss_client(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMBussForm.buss_name)
    await state.update_data(group="Автобус")
    await callback.message.delete()
    await callback.message.answer(
        text=f'{SET_LEXICON["set_name"]}', reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(FSMBussForm.buss_name), ValidName())
async def create_buss_name(message: Message, state: FSMContext):
    data = " ".join(elem.title() for elem in message.text.split())
    database = await state.get_data()
    user = get_user(data, database["group"])
    kb = bild_reply_kb(MAIN_LEXICON)
    if user:
        await message.answer(text="Такий клієнт вже існує ❌", reply_markup=kb)
        await state.clear()
    else:
        await state.update_data(name=data)
        await state.set_state(FSMBussForm.buss_city)
        database = await state.get_data()
        await message.answer(
            text='\n'.join(database.values()) + "\n\n" + SET_LEXICON['set_city'])


@router.message(StateFilter(FSMBussForm.buss_name))
async def incorect_buss_name(message: Message):
    text = message.text
    await message.reply(text=f"{INVALID_LEXICON['invalid_name']}<b>{text}</b>")


@router.message(StateFilter(FSMBussForm.buss_city), ValidCity())
async def create_buss_city(message: Message, state: FSMContext):
    data = " ".join(elem.title() for elem in message.text.split())
    await state.update_data(city=data)
    database = await state.get_data()
    await state.set_state(FSMBussForm.buss_phone)
    await message.answer(
        text='\n'.join(database.values()) + "\n\n" + SET_LEXICON['set_phone'])


@router.message(StateFilter(FSMBussForm.buss_city))
async def incorect_buss_city(message: Message):
    text = message.text
    await message.reply(text=f"{INVALID_LEXICON['invalid_city']}<b>{text}</b>")


@router.message(StateFilter(FSMBussForm.buss_phone), ValidPhone())
async def create_buss_phone(message: Message, state: FSMContext):
    mess = str(message.text)
    phone = f"({mess[:3]}) {mess[3:5]} {mess[5:7]} {mess[7:]}"
    await state.update_data(phone=phone)
    database = await state.get_data()
    kb = bild_reply_kb(MAIN_LEXICON)
    user = create_user(database)
    await state.clear()
    await message.answer(
        text='✅  Створено  ✅',
        reply_markup=kb)


@router.message(StateFilter(FSMBussForm.buss_phone))
async def incorect_buss_phone(message: Message):
    text = message.text
    await message.reply(
        text=f"{INVALID_LEXICON['invalid_phone']}<b>{text}</b>")
