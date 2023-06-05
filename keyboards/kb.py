from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def bild_reply_kb(arr: list[str]):
    buttons = [[KeyboardButton(text=data)] for data in arr]
    main_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
        keyboard=[*buttons],
        resize_keyboard=True)
    return main_kb
