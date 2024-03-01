# from aiogram import Bot, Dispatcher, executor, types

# import logging
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.utils import markdown as md
# from aiogram.types import ParseMode
# import psycopg2

# from settings import markups as nav

# from create_bot import dp, bot

# from settings import config as cfg

# from datetime import datetime
# import database

# db = database.DBCommands()

# async def filtration(user_id, status):

# 	user = db.get_user_info(user_id, status)

# 	driver = await Driver.query.gino.first()

# 	passengers = await Passenger.query.gino.all()

