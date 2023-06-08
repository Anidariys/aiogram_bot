from lexicon.lexicon import (SET_LEXICON, MAIN_LEXICON, INVALID_LEXICON, 
    CHOICE_LEXICON, UPDATE_USER_LEXICON, DB_ROWS)
from filters.filters import ValidName, ValidCity, ValidPhone, ValidAddress
from keyboards.kb import bild_reply_kb
from keyboards.inline_kb import inline_keyboard
from FSM.FSM import FSMUpdateForm
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram import Router, F
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from database.database import get_user, update_user


router: Router = Router()


@router.callback_query(Text(text=["NP", "delivery", "buss"]), StateFilter(FSMUpdateForm.set_group))
async def choice_update_group(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMUpdateForm.set_name)
    await state.update_data(group=CHOICE_LEXICON[callback.data])
    await callback.message.delete()
    await callback.message.answer(
        text="Вкажіть прізвище та ім'я клієнта 🧑‍⚕️", reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(FSMUpdateForm.set_name), ValidName())
async def get_client_name(message: Message, state: FSMContext):
    data = " ".join(elem.title() for elem in message.text.split())
    database = await state.get_data()
    user = get_user(data, database["group"])
    if user is None:
        await message.answer(
            text=f"{INVALID_LEXICON['user_not_found']}")

    else:
        choice = {
        "Нова пошта": UPDATE_USER_LEXICON["np_choice"],
        "Автобус": UPDATE_USER_LEXICON["buss_choice"],
        "Доставка": UPDATE_USER_LEXICON["delivery_choice"]
        }

        kb = inline_keyboard(choice[database["group"]])
        await state.update_data(name=data)
        await state.set_state(FSMUpdateForm.set_kay)
        await message.answer(
            text="Виберіть що саме будемо міняти :", reply_markup=kb)


@router.message(StateFilter(FSMUpdateForm.set_name))
async def incorect_user_name(message: Message):
    text = message.text
    await message.reply(text=f"{INVALID_LEXICON['invalid_name']}<b>{text}</b>")


@router.callback_query(Text(text="phone"), StateFilter(FSMUpdateForm.set_kay))
async def choice_user_phone(callback: CallbackQuery, state: FSMContext):
    await state.update_data(key=callback.data)
    await state.set_state(FSMUpdateForm.set_phone)
    await callback.message.delete()
    await callback.message.answer(
        text="На що міняємо ❓❓")


@router.message(StateFilter(FSMUpdateForm.set_phone), ValidPhone())
async def update_user_phone(message: Message, state: FSMContext):
    mess = str(message.text)
    phone = f"({mess[:3]}) {mess[3:5]} {mess[5:7]} {mess[7:]}"
    print("* "*10, phone)
    await state.update_data(value=phone)
    data = await state.get_data()
    update_user(data)
    kb = bild_reply_kb(MAIN_LEXICON)
    await message.answer(text="✅ Змінено ✅", reply_markup=kb)
    await state.clear()


@router.message(StateFilter(FSMUpdateForm.set_phone))
async def incorect_phone(message: Message):
    await message.answer(text=f"{INVALID_LEXICON['invalid_phone']}")    


@router.callback_query(Text(text=DB_ROWS), StateFilter(FSMUpdateForm.set_kay))
async def choice_user_category(callback: CallbackQuery, state: FSMContext):
    await state.update_data(key=callback.data)
    await state.set_state(FSMUpdateForm.set_value)
    await callback.message.delete()
    await callback.message.answer(
        text="На що міняємо ❓❓")


@router.message(StateFilter(FSMUpdateForm.set_value))
async def update_user_data(message: Message, state: FSMContext):
    await state.update_data(value=message.text)
    data = await state.get_data()
    update_user(data)
    kb = bild_reply_kb(MAIN_LEXICON)
    await message.answer(text="✅ Змінено ✅", reply_markup=kb)
    await state.clear()


@router.message(StateFilter(FSMUpdateForm.set_value))
async def incorect_messsage(message: Message):
    await message.answer(text="короткувато...попробуйте більше символів.")    


@router.callback_query(Text(text="photo"), StateFilter(FSMUpdateForm.set_kay))
async def update_delivery_photo(callback: CallbackQuery, state: FSMContext):
    await state.update_data(key=callback.data)
    await state.set_state(FSMUpdateForm.set_photo)
    await callback.message.delete()
    await callback.message.answer(
        text="Пришліть фото")


@router.message(StateFilter(FSMUpdateForm.set_photo), F.photo)
async def update_photo(message: Message, state: FSMContext):
    photo = message.photo[0].file_id
    await state.update_data(value=photo)
    data = await state.get_data()
    update_user(data)
    kb = bild_reply_kb(MAIN_LEXICON)
    await message.answer(text="✅ Фото змінено ✅", reply_markup=kb)
    await state.clear()


@router.message(StateFilter(FSMUpdateForm.set_photo))
async def incorect_user_photo(message: Message, state: FSMContext):
    await message.answer(text="Це не схоже на фото...")


@router.callback_query(
    Text(text="location"),
    StateFilter(FSMUpdateForm.set_kay))
async def inline_get_location(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMUpdateForm.set_location)
    await state.update_data(key=callback.data)
    button = [[KeyboardButton(
        text="Відправити геолокацію", request_location=True)], 
        [KeyboardButton(text="Відміна")]]
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=button,
        resize_keyboard=True,
        one_time_keyboard=True)
    await callback.message.delete()
    await callback.message.answer(
        text="Натисніть на кнопку,\nщоб відправити локацію ⬇️", 
        reply_markup=kb)


@router.message(
    StateFilter(FSMUpdateForm.set_location),
                F.content_type == 'location')
async def cancel_user_location(message: Message, state: FSMContext):
    location = message.location
    kb = bild_reply_kb(MAIN_LEXICON)
    await state.update_data(value=location.json())
    await message.answer(text="✅ Локацію змінено ✅", reply_markup=kb)
    await state.clear()


@router.message(
    StateFilter(FSMUpdateForm.set_location),
                F.content_type == 'location')
async def update_user_location(message: Message, state: FSMContext):
    location = message.location
    kb = bild_reply_kb(MAIN_LEXICON)
    await state.update_data(value=location.json())
    await message.answer(text="✅ Локацію змінено ✅", reply_markup=kb)
    await state.clear()


@router.message(StateFilter(FSMUpdateForm.set_location))
async def update_user_location(message: Message):
    button = [KeyboardButton(
        text="Відправити геолокацію", request_location=True)]
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[button],
        resize_keyboard=True,
        one_time_keyboard=True)
    await callback.message.answer(
        text="Натисніть на кнопку,\nщоб відправити локацію ⬇️", 
        reply_markup=kb)



