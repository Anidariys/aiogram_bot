from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def inline_keyboard(lexicon: dict, width=1) -> InlineKeyboardMarkup:

    inline_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()

    data = [InlineKeyboardButton(
        text=f'{lexicon[button]}',
        callback_data=f'{button}') for button in lexicon]

    inline_builder.row(*data, width=width)

    return inline_builder.as_markup()
