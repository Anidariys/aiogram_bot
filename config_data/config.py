import dotenv
import os

from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    mongo_con: str
    admin: int


@dataclass
class Config:
    tg_bot: TgBot


def load_config() -> Config:
    dotenv.load_dotenv()
    return Config(tg_bot=TgBot(
        token=os.getenv("TOKEN"),
        mongo_con=os.getenv("MONGO_CON"),
        admin=os.getenv("ADMIN"))
    )
