import logging

from config_data.config import Config, load_config
from handlers import (other_handlers, user_handlers,
                      buss_handlers, NP_handlers,
                      delivery_handlers, update_user_handler,
                      get_handlers, delete_user_handlers)
from keyboards.main_menu import set_main_menu
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, Redis
from admin import admin_handlers

logger = logging.getLogger(__name__)


logging.basicConfig(
    level=logging.INFO,
    format='%(filename)s:%(lineno)d #%(levelname)-8s '
           '[%(asctime)s] - %(name)s - %(message)s')

logger.info('Starting bot')

redis: Redis = Redis(host='localhost')
storage: RedisStorage = RedisStorage(redis=redis)

config: Config = load_config()

bot: Bot = Bot(token=config.tg_bot.token,
               parse_mode='HTML')
dp: Dispatcher = Dispatcher(storage=storage)


dp.include_router(admin_handlers.router)
dp.include_router(user_handlers.router)
dp.include_router(get_handlers.router)
dp.include_router(update_user_handler.router)
dp.include_router(delete_user_handlers.router)
dp.include_router(delivery_handlers.router)
dp.include_router(NP_handlers.router)
dp.include_router(buss_handlers.router)
dp.include_router(other_handlers.router)
