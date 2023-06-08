from lexicon.lexicon import LEXICON, MAIN_LEXICON, CHOICE_LEXICON
from keyboards.kb import bild_reply_kb
from keyboards.inline_kb import inline_keyboard
from FSM.FSM import FSMUpdateForm, FSMGetClientData, FSMDeletClient
from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart, StateFilter, Text


router: Router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message, state: FSMContext):
    kb = bild_reply_kb(MAIN_LEXICON)
    await state.clear()
    await message.answer(
        text="Давайте розпочнемо =)", 
        reply_markup=kb)


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON["/help"])


@router.message(Command(commands='cancel'),
                StateFilter(default_state))
async def command_calcel(message: Message):
    await message.reply(text="У вас немає незавершених дій ")


@router.message(Command(commands='cancel'),
                ~StateFilter(default_state))
async def in_state_command_calcel(message: Message, state: FSMContext):
    kb = bild_reply_kb(MAIN_LEXICON)
    await message.reply(text="Відмінив ", reply_markup=kb)
    await state.clear()


@router.message(Text(text="Створити клієнта"),
                StateFilter(default_state))
async def crate_client(message: Message):
    kb = inline_keyboard(CHOICE_LEXICON, 2)

    await message.answer(
        text="Виберіть де ви хочете його створити :", reply_markup=kb)


@router.message(Text(text="Створити клієнта"),
                ~StateFilter(default_state))
async def in_state_create_client(message: Message):
    await message.answer(
        text="Ви ще не завершили минулу дію\n/cancel - щоб закінчити")


@router.message(Text(text="Редагувати дані клієнта"),
                StateFilter(default_state))
async def update_client(message: Message, state: FSMContext):
    kb = inline_keyboard(CHOICE_LEXICON, 2)
    await state.set_state(FSMUpdateForm.set_group)
    await message.answer(
        text="Виберіть де ви хочете його змінити :", reply_markup=kb)


@router.message(Text(text="Редагувати дані клієнта"),
                ~StateFilter(default_state))
async def in_state_update_client(message: Message):
    await message.answer(
        text="Ви ще не завершили минулу дію\n/cancel - щоб закінчити")


@router.message(Text(text="Переглянути дані клієнта"),
                StateFilter(default_state))
async def get_client_datat(message: Message, state: FSMContext):
    await state.set_state(FSMGetClientData.get_group)
    kb = inline_keyboard(CHOICE_LEXICON, 2)
    await message.answer(
        text="Виберіть де ми його шукаємо :", reply_markup=kb)


@router.message(Text(text="Переглянути дані клієнта"),
                ~StateFilter(default_state))
async def in_state_get_client(message: Message):
    await message.answer(
        text="Ви ще не завершили минулу дію\n/cancel - щоб закінчити")


@router.message(Text(text="Видалити клієнта"), StateFilter(default_state))
async def delete_clent_handler(message: Message, state: FSMContext):
    await state.set_state(FSMDeletClient.get_group)
    kb = inline_keyboard(CHOICE_LEXICON, 2)
    await message.answer(
        text="Виберіть звідки ми \nбудемо його видаляти :", reply_markup=kb)


@router.message(Text(text="Видалити клієнта"), ~StateFilter(default_state))
async def in_state_delete_client(message: Message):
    await message.answer(
        text="Ви ще не завершили минулу дію\n/cancel - щоб закінчити")
