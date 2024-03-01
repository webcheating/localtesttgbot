from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode


from settings import config as cfg



storage = MemoryStorage()
bot = Bot(token=cfg.BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)
dp = Dispatcher(bot, storage=storage)