from aiogram import Router, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import StateFilter, Text
from lexicon.lexicon import (
    SET_LEXICON, MAIN_LEXICON,
    INVALID_LEXICON, DELEVERY_CHOICE)
from keyboards.kb import bild_reply_kb
from filters.filters import ValidName, ValidAddress, ValidPhone
from keyboards.inline_kb import inline_keyboard
from FSM.FSM import FSMDeliveryForm
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from database.database import create_user, get_user


router: Router = Router()


@router.callback_query(Text(text='delivery'), StateFilter(default_state))
async def create_delivery_client(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMDeliveryForm.delivery_name)
    await state.update_data(group="Доставка")
    await callback.message.delete()
    await callback.message.answer(
        text=f'{SET_LEXICON["set_name"]}', reply_markup=ReplyKeyboardRemove())


@router.message(StateFilter(FSMDeliveryForm.delivery_name), ValidName())
async def create_delivery_name(message: Message, state: FSMContext):
    data = " ".join(elem.title() for elem in message.text.split())
    database = await state.get_data()
    user = get_user(data, database["group"])
    kb = bild_reply_kb(MAIN_LEXICON)
    if user:
        await message.answer(text="Такий клієнт вже існує ❌", 
            reply_markup=kb)
        await state.clear()
    else:
        await state.update_data(name=data)
        await state.set_state(FSMDeliveryForm.delivery_address)
        await message.answer(
            text=f"{SET_LEXICON['set_address']}")


@router.message(StateFilter(FSMDeliveryForm.delivery_name))
async def incorrect_delivery_name(message: Message):
    text = message.text
    await message.reply(text=f"{INVALID_LEXICON['invalid_name']}<b>{text}</b>")


@router.message(StateFilter(FSMDeliveryForm.delivery_address), ValidAddress())
async def create_delivery_address(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(FSMDeliveryForm.delivery_other)
    kb = inline_keyboard(DELEVERY_CHOICE)
    await message.answer(
        text=f"{SET_LEXICON['set_delivery_end_choice']}", reply_markup=kb)


@router.message(StateFilter(FSMDeliveryForm.delivery_address))
async def incorrect_delivery_address(message: Message):
    text = message.text
    await message.reply(
        text=f"{INVALID_LEXICON['invalid_address']}\n<b>{text}</b>")


@router.message(Text(text="Відміна"), 
    StateFilter(FSMDeliveryForm))
async def cancel_delivery_location(message: Message, state: FSMContext):
    await state.set_state(FSMDeliveryForm.delivery_other)
    kb = inline_keyboard(DELEVERY_CHOICE)
    await message.answer(
        text="Відмінено, продовжуємо :    ",
        reply_markup=kb)


@router.callback_query(
    Text(text='add_comment'),
    StateFilter(FSMDeliveryForm.delivery_other))
async def inline_add_comment(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMDeliveryForm.delivery_comment)
    button = [[KeyboardButton(text="Відміна")]]
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=button,
        resize_keyboard=True,
        one_time_keyboard=True)
    await callback.message.answer(
        text=f"{SET_LEXICON['set_delivery_comment']}", 
        reply_markup=kb)


@router.message(
    StateFilter(FSMDeliveryForm.delivery_comment),
    lambda x: len(x.text) > 5)
async def create_delivery_comment(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    await state.set_state(FSMDeliveryForm.delivery_other)
    kb = inline_keyboard(DELEVERY_CHOICE)
    data = await state.get_data()
    comment = data["comment"]
    await message.answer(
        text="✅ Коментар додано ✅\n\n" +
        f"{SET_LEXICON['set_delivery_end_choice']}",
        reply_markup=kb)


@router.message(StateFilter(FSMDeliveryForm.delivery_comment))
async def incorrect_delivery_comment(message: Message, state: FSMContext):
    database = await state.get_data()
    client = database["name"]
    await message.reply(
        text=f"Введіть коментар для клієнта\n<b>{client}</b>\
            \nВін має містити більше 5 символів.")


@router.callback_query(Text(text='add_photo'),
                       StateFilter(FSMDeliveryForm.delivery_other))
async def inline_add_photo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMDeliveryForm.delivery_photo)
    button = [[KeyboardButton(text="Відміна")]]
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=button,
        resize_keyboard=True,
        one_time_keyboard=True)
    await callback.message.answer(
        text=f"{SET_LEXICON['set_photo']}",
        reply_markup=kb)


@router.message(StateFilter(FSMDeliveryForm.delivery_photo), F.photo)
async def create_delivery_photo(message: Message, state: FSMContext):
    photo = message.photo[0].file_id
    await state.update_data(photo=photo)
    await state.set_state(FSMDeliveryForm.delivery_other)
    kb = inline_keyboard(DELEVERY_CHOICE)
    await message.answer(
        text="✅ Фото додано ✅ \n\n" +
        f"{SET_LEXICON['set_delivery_end_choice']}",
        reply_markup=kb)


@router.message(StateFilter(FSMDeliveryForm.delivery_photo))
async def incorrect_delivery_photo(message: Message, state: FSMContext):
    database = await state.get_data()
    client = database["name"]
    await message.reply(
        text=f"Я досі чекаю на фото для клієнта\n<b>{client}</b>")


@router.callback_query(
    Text(text='add_location'),
    StateFilter(FSMDeliveryForm.delivery_other))
async def inline_add_location(callback: CallbackQuery, state: FSMContext):
    await state.set_state(FSMDeliveryForm.delivery_location)
    button = [[KeyboardButton(
        text="Відправити геолокацію", request_location=True)], 
        [KeyboardButton(text="Відміна")]]
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=button,
        resize_keyboard=True,
        one_time_keyboard=True)
    await callback.message.answer(
        text="Натисніть на кнопку,\nщоб відправити локацію ⬇️", 
        reply_markup=kb)


@router.message(
    StateFilter(FSMDeliveryForm.delivery_location),
    F.content_type == 'location')
async def create_delivery_location(message: Message, state: FSMContext):
    location = message.location.dict()
    loc = {
    "longitude": location["longitude"],
    "latitude": location["latitude"]
    }
    await state.update_data(location=loc)
    await state.set_state(FSMDeliveryForm.delivery_other)
    kb = inline_keyboard(DELEVERY_CHOICE)
    await message.answer(
        text="✅ Локацію додано ✅ \n\n" +
        f"{SET_LEXICON['set_delivery_end_choice']}",
        reply_markup=kb)


@router.message(StateFilter(FSMDeliveryForm.delivery_location))
async def incorrect_delivery_location(message: Message, state: FSMContext):
    button = [KeyboardButton(
        text="Відправити геолокацію", request_location=True)]
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[button],
        resize_keyboard=True,
        one_time_keyboard=True)
    await message.reply(
        text="Натисніть на кнопку знизу,\nщоб відправити локацію ⬇️", 
        reply_markup=kb)


@router.callback_query(
    Text(text='add_phone'),
    StateFilter(FSMDeliveryForm.delivery_other))
async def inline_add_comment(callback: CallbackQuery, state: FSMContext):
    button = [[KeyboardButton(text="Відміна")]]
    kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=button,
        resize_keyboard=True,
        one_time_keyboard=True)
    await state.set_state(FSMDeliveryForm.delivery_phone)
    await callback.message.answer(
        text=f"{SET_LEXICON['set_phone']}", 
        reply_markup=kb)


@router.message(
    StateFilter(FSMDeliveryForm.delivery_phone),
    ValidPhone())
async def create_delivery_comment(message: Message, state: FSMContext):
    mess = str(message.text)
    phone = f"({mess[:3]}) {mess[3:5]} {mess[5:7]} {mess[7:]}"
    await state.update_data(phone=phone)
    await state.set_state(FSMDeliveryForm.delivery_other)
    kb = inline_keyboard(DELEVERY_CHOICE)
    await message.answer(
        text="✅ Телефон додано ✅\n\n" +
        f"{SET_LEXICON['set_delivery_end_choice']}",
        reply_markup=kb)


@router.message(StateFilter(FSMDeliveryForm.delivery_phone))
async def incorrect_delivery_comment(message: Message, state: FSMContext):
    database = await state.get_data()
    client = database["name"]
    await message.reply(
        text=f"Введіть номер телефону для :\n<b>{client}</b>\
            \nВін має складатися з 10 цифр")


@router.callback_query(
    Text(text='finish'),
    StateFilter(FSMDeliveryForm.delivery_other))
async def inline_finish(callback: CallbackQuery, state: FSMContext):
    database = await state.get_data()
    kb = bild_reply_kb(MAIN_LEXICON)
    user = create_user(database)
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(text='✅  Створено  ✅ ', 
        reply_markup=kb)
