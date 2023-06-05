from aiogram.filters import BaseFilter
from aiogram.types import Message
from config_data.config import load_config
from admin.admin_db import get_white_list_users, get_ids_from_decision_list


class IsAdmin(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        admin_id: str = load_config().tg_bot.admin
        return str(message.from_user.id) == admin_id


class IsInWiteList(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        wite_users: list[str] = [
        data.get("user_id") for data in get_white_list_users()
        ]
        return message.from_user.id in wite_users


class ValidName(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        if not len(message.text.split()) in (2, 3):
            return False
        return all([elem.isalpha() and len(elem) >= 2 for elem in
                    message.text.split()])


class IsNotInDecisionList(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        users: list[int] = get_ids_from_decision_list()
        return message.from_user.id in users



class ValidCity(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        return all([x.isalpha() and len(x) > 2 for x in message.text.split()])


class ValidAddress(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        return len(message.text) > 3


class ValidPhone(BaseFilter):

    async def __call__(self, message: Message) -> bool:
        data = message.text.replace(" ", "")
        return data.isdigit() and len(data) == 10
