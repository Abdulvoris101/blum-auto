import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from aiogram import types
import uvicorn
from fastapi import Request

from apps.accounts.handlers import accountsRouter
from apps.admin.handlers import adminRouter
from apps.common.middleware import MessageMiddleware
from apps.common.settings import settings
from apps.core.handlers import coreRouter
from apps.payment.api import PaymentProcessor
from apps.payment.handlers import paymentRouter
from bot import bot, dp
from utils.proxies import ProxyDbUtils

WEBHOOK_PATH = f"/bot/3/{settings.BOT_TOKEN}"
WEBHOOK_URL = settings.WEB_URL + WEBHOOK_PATH


@asynccontextmanager
async def lifespan(app: FastAPI):
    webhookInfo = await bot.get_webhook_info()
    dp.include_router(coreRouter)
    dp.include_router(adminRouter)
    dp.include_router(paymentRouter)
    dp.include_router(accountsRouter)
    dp.message.middleware(MessageMiddleware())
    if webhookInfo.url != WEBHOOK_URL:
        await bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True
        )

    yield

    await dp.storage.close()
    await bot.delete_webhook(drop_pending_updates=True)


app = FastAPI(lifespan=lifespan)


@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    tgUpdate = types.Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, tgUpdate)


@app.post("/payment-webhook")
async def paymentWebhook(request: Request):
    payment = PaymentProcessor(await request.json())
    await payment.handle()


if __name__ == "__main__":
    asyncio.run(ProxyDbUtils().dumpProxiesToDb())
    uvicorn.run("app:app", host='0.0.0.0', port=3030, reload=False, workers=2)
