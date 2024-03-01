from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils import markdown as md
from aiogram.types import ParseMode
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.markdown import link

from settings import markups as nav

from create_bot import dp, bot
import database
from datetime import datetime
from datetime import timedelta
import googlemaps

from settings.config import api_key_google

gmaps = googlemaps.Client(key=api_key_google)
db = database.DBCommands()

class Applications(StatesGroup):
	waiting_for_respons = State()

# @dp.message_handler(commands=['start'])
async def command_identity(message: types.Message):
	try:

		check_user = await db.get_user_status(message.from_user.id)

		if check_user == None:
			await bot.send_photo(message.from_user.id, photo = open('imgs/welcome.jpg', 'rb'), caption=f'👋Привет, {message.from_user.first_name}, я бот для заявок!', reply_markup=nav.identity)

			set_sub = database.Subscriptions(user_id=message.from_user.id, amount=0)
			await set_sub.create()
		else:
			await bot.send_photo(message.from_user.id, photo = open('imgs/welcome.jpg', 'rb'), caption=f'👋Привет, {message.from_user.first_name}, я бот для заявок!')

			if check_user.status == 'passenger':

				await bot.send_message(message.from_user.id, f"✅ Вы были идентифицированы как {md.bold('пассажир')}!")
				await bot.send_message(message.from_user.id, f"🖥 Для взаимодействия с ботом используйте {md.bold('меню')}", reply_markup=nav.mainKeyboardMenu)

			elif check_user.status == 'driver':

				await bot.send_message(message.from_user.id, f"✅ Вы были идентифицированы как {md.bold('водитель')}!")
				await bot.send_message(message.from_user.id, f"🖥 Выберите {md.bold('меню')} для взаимодействия с ботом", reply_markup=nav.mainKeyboardMenu)

			else:
				await bot.send_message(message.from_user.id, '[INFO] Error, пожалуйста свяжитесь по поводу ошибки с @w4xdwhyduwy')
			
	except Exception as _ex:
		print(_ex)
		await message.reply('Чтобы отправить заявку - напишите боту:\nt.me/kachger_bot ')




async def number_of_applications(call: types.CallbackQuery):
	await bot.delete_message(call.from_user.id, call.message.message_id)

	user_status	= await	db.get_user_status(call.from_user.id)
	global accepted_applications
	accepted_applications = []
	global filters
	filters = await db.filtration(call.from_user.id, user_status.status)

	await bot.send_message(call.from_user.id, f'Найдено заявок: {md.bold(len(filters))}')

	passenger = await db.get_user_info(filters[0], 'passenger')

	date = datetime.strftime(passenger.date, "%d/%m/%Y")

	full_time_and_date = datetime.combine(passenger.date, passenger.time)

	now = datetime.now()
	directions_result = gmaps.distance_matrix(passenger.departure,
                                    passenger.arrival,
                                    mode="driving",
                                    avoid="ferries",
                                    departure_time=now
                                   )

	duration = str(directions_result['rows'][0]['elements'][0]['duration']['text'])
	parts = duration.split(' ')
	duration = int(parts[0])

	proposed_time = full_time_and_date - timedelta(hours=duration)
	proposed_time = datetime.strftime(proposed_time, '%d.%m.%Y %H:%M')

	await Applications.waiting_for_respons.set()
	await bot.send_message(call.from_user.id, f"🚗 Поездка: {passenger.departure} - {passenger.arrival}\n\nСвязь: {passenger.relation}\n\nНадо быть в месте назначения {md.bold(date)} в {md.bold(passenger.time)}\n\nПоездка займет примерно {duration}ч.\n\nПредлагаемое время выезда: {proposed_time}", reply_markup=nav.ChooseApplication)

async def command_accept(call: types.CallbackQuery, state: FSMContext):

	user_status	= await	db.get_user_status(call.from_user.id)
	global filters

	if call.data == 'appAccept':
		accepted_applications.append(filters[0])
	elif call.data == 'appRefuse':
		pass
	else:
		await bot.send_message(call.from_user.id, f'Неизвествная команда, пожалуйста, воспользуйтесь всплывающим меню')

	try:

		filters.pop(0)
		passenger = await db.get_user_info(filters[0], 'passenger')

		date = datetime.strftime(passenger.date, "%d/%m/%Y")

		full_time_and_date = datetime.combine(passenger.date, passenger.time)
		date_and_time = datetime.strftime(full_time_and_date, '%d.%m.%Y %H:%M')

		now = datetime.now()
		directions_result = gmaps.distance_matrix(passenger.departure,
                                    	passenger.arrival,
                                    	mode="driving",
                                    	avoid="ferries",
                                    	departure_time=now
                                   	)

		duration = str(directions_result['rows'][0]['elements'][0]['duration']['text'])
		parts = duration.split(' ')
		duration = int(parts[0])

		proposed_time = full_time_and_date - timedelta(hours=duration)
		proposed_time = datetime.strftime(proposed_time, '%d.%m.%Y %H:%M')

		await bot.delete_message(call.from_user.id, call.message.message_id)
		await Applications.waiting_for_respons.set()
		await bot.send_message(call.from_user.id, f"🚗 Поездка: {passenger.departure} - {passenger.arrival}\n\nСвязь: {passenger.relation}\n\nНадо быть в месте назначения {md.bold(date)} в {md.bold(passenger.time)}\n\nПоездка займет примерно {duration}ч.\n\nПредлагаемое время выезда: {proposed_time}", reply_markup=nav.ChooseApplication)
	except:
		await bot.delete_message(call.from_user.id, call.message.message_id)
		await state.finish()

async def send_accepted_applications(message: types.Message):
	await bot.send_message(message.from_user.id, accepted_applications)


# async def choose_applications(call: types.CallbackQuery):
# 	if call.data == 'appShow':

# 		await bot.delete_message(call.from_user.id, call.message.message_id)

# 		user_status	= await	db.get_user_status(call.from_user.id)
# 		filters = await db.filtration(call.from_user.id, user_status.status)

# 		await bot.send_message(call.from_user.id, f'Найдено заявок: {md.bold(len(filters))}')

# 		filters = await db.filtration(call.from_user.id, user_status.status)

# 		accepted_applications = []

# 		for passenger in filters:

# 			client = await db.get_user_info(passenger, 'passenger')


# 			full_time_and_date = datetime.combine(client.date, client.time)
# 			proposed_time = full_time_and_date - timedelta(hours=12)
# 			proposed_time = datetime.strftime(proposed_time, '%d.%m.%Y %H:%M')
# 			date_and_time = datetime.strftime(full_time_and_date, '%d.%m.%Y %H:%M')

# 			await bot.send_message(call.from_user.id, f"🚗 Поездка: {client.departure} - {client.arrival}\n\nСвязь: {client.relation}\n\nНадо быть в месте назначения в: {date_and_time}", reply_markup=nav.ChooseApplication)
			
# 			if call.data == 'appAccept':
# 				accepted_applications = []
# 				accepted_applications.append
# 			elif call.data == 'appRefuse':
# 				pass
# 			#await bot.send_message(call.from_user.id, f"Поездка: {client.departure} - {client.arrival}\n\nДата: {client.date}\n\nВремя: {client.time}\n\nСвязь: {client.relation}")
# 		await bot.send_message(call.from_user.id, f'Вы выбрали: {accepted_applications}')


def register_handlers_other(dp:Dispatcher):
	dp.register_message_handler(command_identity, commands='start')
	# dp.register_callback_query_handler(number_of_applications, text='sendPassengers', state="*")
	# dp.register_callback_query_handler(command_accept, text_contains='app', state=Applications.waiting_for_respons)
	# dp.register_message_handler(send_accepted_applications, commands='show')
	
	# dp.register_callback_query_handler(choose_applications, text_contains='app')