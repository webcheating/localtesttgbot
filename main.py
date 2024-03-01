import logging
import aiogram
from aiogram import executor
from handlers import client, admin, other
# import handlers +надо добавить ко всем функциям хендлеры
from database import *

from create_bot import dp, bot, storage


logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.INFO)

async def on_startup(dp):
	await create_db()
	print('OPEN')

async def on_shutdown(dp):
	await storage.close()
	print('CLOSED')

admin.register_handlers_admin(dp)
other.register_handlers_other(dp)
client.register_handlers_client(dp)


if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True, on_startup=on_startup ,on_shutdown=on_shutdown)