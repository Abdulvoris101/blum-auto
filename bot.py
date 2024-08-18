import logging
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from redis.asyncio import Redis

from apps.common.middleware import DynamicI18nMiddleware
from apps.common.settings import settings
WORKDIR = Path(__file__).parent


i18n = I18n(path=WORKDIR / 'locales', default_locale='uz', domain='messages')
i18n_middleware = DynamicI18nMiddleware(i18n=i18n)

_ = i18n.gettext
__ = i18n.lazy_gettext


redis = Redis(host=settings.REDIS_HOST, port=6379, db=1)
WORKDIR = Path(__file__).parent

bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
storage = RedisStorage(redis=redis)


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot.log',  # Logs will be stored in 'bot.log'
                    filemode='a')  # 'a' means append (add new log entries to the end of the file)
logger = logging.getLogger(__name__)

dp = Dispatcher(storage=storage)
dp.update.outer_middleware(i18n_middleware)
