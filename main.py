from fastapi import FastAPI
from aiogram import types
from bot import dp, bot, config


app = FastAPI()
WEBHOOK_PATH = f"/bot/{config.tg_bot.token}"
WEBHOOK_URL = "https://9c19-46-172-156-66.eu.ngrok.io" + WEBHOOK_PATH


@app.on_event("startup")
async def on_startup():
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )


@app.post(WEBHOOK_PATH)
async def bot_webhook(update: dict):
    telegram_update = types.Update(**update)
    await dp.feed_update(bot, telegram_update)


@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
