import datetime
import bot

from aiogram import Router, F
from aiogram.types import Message
from keyboards.kb import bild_reply_kb
from aiogram.fsm.context import FSMContext
from config_data.config import load_config
from aiogram.fsm.state import default_state
from lexicon.lexicon import NEW_USER_LEXICON
from FSM.FSM import FSMAdminChoice, FSMAdmindDeleteUser, FSMUserReg
from aiogram.filters import CommandStart, Text, StateFilter, Command
from filters.filters import IsAdmin, IsInWiteList, IsNotInDecisionList
from admin.admin_db import (
    add_user_in_white_list, 
    delete_user_from_white_list, 
    get_white_list_users,
    get_from_decision_list,
    add_to_decision_list,
    delete_from_decision_list
    )


router: Router = Router()

ADMIN = int(load_config().tg_bot.admin)


@router.message(Command(commands='cancel'),
                ~StateFilter(default_state), 
                IsAdmin())
async def command_calcel(message: Message, state: FSMContext):
    await state.clear()
    await message.reply(text="Закрив відкритий стан")


@router.message(Command(commands='users'),
                IsAdmin())
async def get_users_from_wl(message: Message, state: FSMContext):
    users = get_white_list_users()
    if users:
        users_data = [
        "\n".join([str(value) for value in data.values()]) for data in users
        ]
        await message.answer(text="\n\n".join(users_data))
    else:
        await message.answer(text="Немає юзерів в білому листі")


@router.message(Command(commands='delete'),
                IsAdmin())
async def delet_user(message: Message, state: FSMContext):
    await state.set_state(FSMAdmindDeleteUser.delete)
    await message.answer(
        text="Пришліть айді юзера кого будем видаляти\n"
             "/users - щоб переглянути юзурів білого списку"
            )


@router.message(StateFilter(FSMAdmindDeleteUser.delete),
                IsAdmin(), 
                lambda x: x.text.isdigit())
async def admin_submission(message: Message, state: FSMContext):
    user_id = int(message.text)
    print(user_id, type(user_id), "*"* 10)
    delete_user_from_white_list(user_id)
    await state.clear()
    await message.answer(text="Видалено")


@router.message(StateFilter(FSMAdmindDeleteUser.delete),
                IsAdmin())
async def admin_invalid_submission(message: Message, state: FSMContext):
    await message.answer(text="Чекаю на йді юзера для видалення")


@router.message(CommandStart(),
                ~IsAdmin(),
                ~IsInWiteList())
async def process_start_command(message: Message, state: FSMContext):
    await state.set_state(FSMUserReg.reg)
    kb = bild_reply_kb(["Подати заявку"])
    await message.answer(
        text=NEW_USER_LEXICON["unknown_user"],
        reply_markup=kb)


@router.message(Text(text="Подати заявку"),
                ~IsInWiteList(),
                ~IsAdmin(), 
                ~IsNotInDecisionList(),
                StateFilter(FSMUserReg.reg))
async def application_submission(message: Message, state: FSMContext):
    user_data: dict[str, str | int] = {
        "user_id": message.from_user.id,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "username": message.from_user.username,
        "language_code": message.from_user.language_code,
        "date": datetime.datetime.now()
        }
    await state.clear()
    await message.answer(text="Заявку подано 👍")
    add_to_decision_list(user_data)
    await bot.bot.send_message(
        ADMIN, text='Нова заявочка від :\n\n' 
        + '\n'.join([f"{k}: {v}" for k, v in user_data.items() if v is not None]) 
        + "\n\n/add щоб прийняти і додати, - відхилити")


@router.message(Command(commands='add'), IsAdmin())
async def add_admin_submission(message: Message, state: FSMContext):
    await state.set_state(FSMAdminChoice.choice)
    await message.answer(
        text="пришліть айді кого додаєм\n" 
        + " ' - ' (мінус) + id якщо хочете відмовити" 
        + "\nnнаприклад : -23445678")


@router.message(
    F.text.startswith("-"), 
    IsAdmin(), 
    StateFilter(FSMAdminChoice.choice))
async def refuse_add_white_list(message: Message, state: FSMContext):
    try:
        user_id = int(message.text.strip("-"))
        delete_from_decision_list(user_id)
        await message.answer(text="Відмінено")
        await bot.bot.send_message(
            user_id, 
            text=NEW_USER_LEXICON["denial_to_the_user"]) 
    except Exception as e:
        await message.answer(
            text="Помилка в відмові !!\n" 
            + str(e) 
            + "\nПопробуйде ще раз")
    finally:
        await state.clear()


@router.message(
    IsAdmin(), 
    StateFilter(FSMAdminChoice.choice), 
    lambda x: x.text.isdigit())
async def add_to_white_list(message: Message, state: FSMContext):
    try:
        user_id = int(message.text)
        data = get_from_decision_list(user_id)
        add_user_in_white_list(data)
        delete_from_decision_list(user_id)
        await message.answer(text=f"Додано: {data['first_name']}")
        await state.clear()
        await bot.bot.send_message(user_id, NEW_USER_LEXICON["accept_user"])
    except:
        await message.answer(
            text="ЩОСЬ НЕ ТАК !\nпришліть айді кого додаєм\n- щоб відмінити")


@router.message(
    IsAdmin(), 
    StateFilter(FSMAdminChoice.choice))
async def invalid_user_id_from_admin(
    message: Message, state: FSMContext):
    user_text = message.text
    await message.answer(
        text="чекаю на айді юзера якого добавляємо в білий список\n" 
        + "це має бути число без букв і символів\n"  
        + f"а ви прислали: {user_text}")


@router.message(~IsInWiteList(), ~IsAdmin(), IsNotInDecisionList())
async def wait_decision_message(message: Message):
    await message.answer(
        text="Ви уже подали заявку.\n"
        + "Тепер треба зачекати на відповідь.\n" 
        + "Це може зайняти деякий час...")


@router.message(~IsInWiteList(), ~IsAdmin(), ~IsNotInDecisionList())
async def initial_message(message: Message):
    await message.answer(
        text="Ви не заєстрований клієнт\n"
        + "Щоб подати заявку над міть /start\n" 
        + "Це може зайняти деякий час...")
