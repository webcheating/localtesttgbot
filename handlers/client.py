from aiogram import Bot, Dispatcher, executor, types

import logging
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import markdown as md
from aiogram.types import ParseMode

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.types.message import ContentType

from settings import markups as nav

from create_bot import dp, bot

from settings import config as cfg

from datetime import datetime
import database

from datetime import timedelta
import googlemaps

from settings.config import api_key_google

db = database.DBCommands()

active_req = '1'
gmaps = googlemaps.Client(key=api_key_google)
pay_token = '1744374395:TEST:67a61a650f94c99766e0'

class Applications(StatesGroup):
	waiting_for_respons = State()

class Form(StatesGroup):
    departure = State()
    arrival = State()
    people = State()
    relation = State()
    date = State()
    time = State()
    response = State()

async def buttons(message: types.Message):
	if message.chat.type == 'private':
		if message.text == '🖥 Меню':

			user_status = await db.get_user_status(message.from_user.id)

			if user_status.status == 'passenger':
				await bot.send_photo(message.from_user.id, photo = open('imgs/menu.jpg', 'rb'), caption=f'Выберите команду:', reply_markup=nav.mainMenu)
			if user_status.status == 'driver':
				await bot.send_photo(message.from_user.id, photo = open('imgs/menu.jpg', 'rb'), caption=f'Выберите команду:', reply_markup=nav.mainMenuForDrivers)


		if message.text == '📱 Чат':
			await bot.send_message(message.from_user.id, '*ссылка на чат*')
		if message.text == '👤 Владелец':
			await bot.send_message(message.from_user.id, '*ссылка на владельца*')


async def set_status(call: types.CallbackQuery):
	if call.data == 'setPassenger':

		await call.message.edit_reply_markup()
		identity = await db.identity_user(call.from_user.id, 'passenger')

		check_application = await db.get_application_info(call.from_user.id, 'driver')
		if check_application != None:
			delete_application = await db.delete_application(call.from_user.id, 'driver')


		await bot.send_message(call.from_user.id, f"✅ Вы были идентифицированы как {md.bold('пассажир')}!")
		await bot.send_message(call.from_user.id, f"🖥 Для взаимодействия с ботом используйте {md.bold('меню')}", reply_markup=nav.mainKeyboardMenu)

	elif call.data == 'setDriver':

		await call.message.edit_reply_markup()
		identity = await db.identity_user(call.from_user.id, 'driver')

		check_application = await db.get_application_info(call.from_user.id, 'passenger')
		if check_application != None:
			delete_application = await db.delete_application(call.from_user.id, 'passenger')

		await bot.send_message(call.from_user.id, f"✅ Вы были идентифицированы как {md.bold('водитель')}!")
		await bot.send_message(call.from_user.id, f"🖥 Для взаимодействия с ботом используйте {md.bold('меню')}", reply_markup=nav.mainKeyboardMenu)


async def main_menu(call: types.CallbackQuery):
	if call.data == 'sendReq':
		user_status = await db.get_user_status(call.from_user.id)

		if user_status.status == 'passenger':
			try:

				check_user = await db.get_application_info(call.from_user.id, user_status.status)

				if check_user != None:
					await bot.delete_message(call.from_user.id, call.message.message_id)
					await bot.send_message(call.from_user.id, 'Вы уже оставили заявку!', reply_markup=nav.applicationBack)
				else:
					await Form.departure.set()
					await bot.delete_message(call.from_user.id, call.message.message_id)
					await bot.send_message(call.from_user.id, "✈️ Укажите место отправления", reply_markup=types.ReplyKeyboardRemove())

			except Exception as _ex:
				print('[INFO]', _ex)

		elif user_status.status == 'driver':
			try:

				check_user = await db.get_application_info(call.from_user.id, user_status.status)

				if check_user != None:
					await bot.delete_message(call.from_user.id, call.message.message_id)
					await bot.send_message(call.from_user.id, 'Вы уже оставили заявку!', reply_markup=nav.applicationBack)
				else:
					await Form.departure.set()
					await bot.delete_message(call.from_user.id, call.message.message_id)
					await bot.send_message(call.from_user.id, "✈️ Укажите место отправления", reply_markup=types.ReplyKeyboardRemove())

			except Exception as _ex:
				print('[INFO]', _ex)


	elif call.data == 'sendProfile':

		user_status = await db.get_user_status(call.from_user.id)

		sub_status = await database.Subscriptions.query.where(database.Subscriptions.user_id == call.from_user.id).gino.first()

		await bot.delete_message(call.from_user.id, call.message.message_id)
		await bot.send_photo(call.from_user.id, photo = open('imgs/info.jpg', 'rb'), caption=f"🆔 {md.bold('Ваш id:')} {call.from_user.id}\n\n🧑🏻‍🔧 {md.bold('Ваш логин:')} {md.code(call.from_user.username)}\n\n📖 {md.bold('Ваш статус:')} {user_status.status}\n\n🔖 {md.bold('Статус подписки:')} {sub_status.amount}", reply_markup=nav.profile)

		# else:
		# 	await bot.send_message(message.from_user.id, '❌ У вас нет активных заявок!')


	elif call.data == 'sendSubscriptions':
		sub_status = await database.Subscriptions.query.where(database.Subscriptions.user_id == call.from_user.id).gino.first()

		if sub_status.amount > 0:
			await bot.delete_message(call.from_user.id, call.message.message_id)

			user_status	= await	db.get_user_status(call.from_user.id)
			global filters
			filters = await db.filtration(call.from_user.id, user_status.status)

			global abc
			abc = await bot.send_message(call.from_user.id, f'Найдено заявок: {md.bold(len(filters))}')

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

		elif sub_status.amount == 0:
			await bot.delete_message(call.from_user.id, call.message.message_id)
			items = await db.show_items()
			all_items_menu = await nav.create_items_menu()

			if len(items) == 1:
				await bot.send_message(call.from_user.id, f'Найден {md.bold(len(items))} товар', reply_markup=all_items_menu[1])
			elif len(items) > 1 and len(items) < 5:
				await bot.send_message(call.from_user.id, f'Найдено {md.bold(len(items))} товара', reply_markup=all_items_menu[1])
			elif len(items) > 5:
				await bot.send_message(call.from_user.id, f'Найдено {md.bold(len(items))} товаров', reply_markup=all_items_menu[1])
			else:
				await bot.send_message(call.from_user.id, f'Список товаров пуст', reply_markup=all_items_menu[1])
		else:
			await bot.send_message(call.from_user.id, '❌ Ошибка (если ошибка повториться, пожалуйста, свяжитесь с @w4xdwhyduwy)', reply_markup = nav.mainKeyboardMenu)

async def command_accept(call: types.CallbackQuery, state: FSMContext):

	user_status	= await	db.get_user_status(call.from_user.id)
	global filters

	if call.data == 'appAccept':
		set_sub = await database.Subscriptions.query.where(database.Subscriptions.user_id == call.from_user.id).gino.first()
		await set_sub.update(amount=set_sub.amount-1).apply()
		driver_contact = await db.get_application_info(call.from_user.id, user_status.status)
		passenger = await db.get_user_info(filters[0], 'passenger')
		await passenger.update(driver=call.from_user.id).apply()

		await bot.send_message(filters[0], f'❗️ {md.bold("Вашу заявку принял водитель")} ❗️\n\n☎️ {md.bold("Контакты для дальнейшей связи")}: {md.code(driver_contact.relation)}')

		# accepted_applications.append(filters[0])
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
		await bot.delete_message(call.from_user.id, abc.message_id)
		await bot.delete_message(call.from_user.id, call.message.message_id)

		await bot.send_message(call.from_user.id, f'{md.bold("Не найдено других заявок по вашему маршруту")}')
		await state.finish()

async def profile_operations(call: types.CallbackQuery):

	if call.data == 'showApp':

		try:

			user_status = await db.get_user_status(call.from_user.id)
			get_passenger = await db.get_user_info(call.from_user.id, user_status.status)

			if get_passenger != None:
				date = datetime.strftime(get_passenger.date, '%d/%m/%Y')

				await bot.delete_message(call.from_user.id, call.message.message_id)
				await bot.send_message(call.from_user.id, f"📝 {md.bold('Ваша заявка')}\n\n1️⃣ {md.bold('Поездка')}:   {get_passenger.departure} - {get_passenger.arrival}\n\n2️⃣ {md.bold('Кол/во человек')}:   {get_passenger.people}\n\n3️⃣ {md.bold('Связь')}:   {md.code(get_passenger.relation)}\n\n4️⃣ {md.bold('Дата')}:   {date}\n\n5️⃣ {md.bold('Время')}:   {get_passenger.time}", reply_markup=nav.request)
			else:
				await bot.delete_message(call.from_user.id, call.message.message_id)
				await bot.send_message(call.from_user.id, '❌ У вас нет активных заявок!', reply_markup=nav.BackToProfile)

		except Exception as _ex:
			print('[INFO]', _ex)


	elif call.data == 'showMainMenu':

		user_status = await db.get_user_status(call.from_user.id)

		await bot.delete_message(call.from_user.id, call.message.message_id)

		if user_status.status == 'passenger':
			await bot.send_photo(call.from_user.id, photo = open('imgs/menu.jpg', 'rb'), caption=f'Выберите команду:', reply_markup=nav.mainMenu)
		if user_status.status == 'driver':
			await bot.send_photo(call.from_user.id, photo = open('imgs/menu.jpg', 'rb'), caption=f'Выберите команду:', reply_markup=nav.mainMenuForDrivers)

	elif call.data == 'showOtherStatuses':

		await bot.delete_message(call.from_user.id, call.message.message_id)
		user_status = await db.get_user_status(call.from_user.id)
		if user_status.status == 'passenger':
			await bot.send_message(call.from_user.id, f"❗️ Ваша старая заявка останется в вашем профиле со статусом {md.bold('пассажир')}", reply_markup=nav.identityChange)
		elif user_status.status == 'driver':
			await bot.send_message(call.from_user.id, f"❗️ Ваша старая заявка останется в вашем профиле со статусом {md.bold('водитель')}", reply_markup=nav.identityChange)

	elif call.data == 'showAllSubs':
		await bot.delete_message(call.from_user.id, call.message.message_id)
		items = await db.show_items()
		all_items_menu = await nav.create_items_menu()

		if len(items) == 1:
			await bot.send_message(call.from_user.id, f'Найден {md.bold(len(items))} товар', reply_markup=all_items_menu[1])
		elif len(items) > 1 and len(items) < 5:
			await bot.send_message(call.from_user.id, f'Найдено {md.bold(len(items))} товара', reply_markup=all_items_menu[1])
		elif len(items) > 5:
			await bot.send_message(call.from_user.id, f'Найдено {md.bold(len(items))} товаров', reply_markup=all_items_menu[1])
		else:
			all_items_menu.add(nav.btnBack)
			await bot.send_message(call.from_user.id, f'Список товаров пуст', reply_markup=all_items_menu[1])

async def change_status(call: types.CallbackQuery):
	if call.data == 'changePassenger':

		await bot.delete_message(call.from_user.id, call.message.message_id)

		update_status = await db.update_status(call.from_user.id, 'passenger')

		await bot.send_message(call.from_user.id, f"✅ Ваш статус был обновлен на {md.bold('пассажир')}!")

	elif call.data == 'changeDriver':

		await bot.delete_message(call.from_user.id, call.message.message_id)

		update_status = await db.update_status(call.from_user.id, 'driver')

		await bot.send_message(call.from_user.id, f"✅ Ваш статус был обновлен на {md.bold('водитель')}!")


# @dp.message_handler(state='*', commands='cancel')
async def command_cancel(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':

	    current_state = await state.get_state()
	    if current_state is None:
	        return

	    logging.info('Cancelling state %r', current_state)

	    await state.finish()

	    await message.reply('Отменено.', reply_markup=types.ReplyKeyboardRemove())


async def set_departure(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':

	    await state.update_data(departure=message.text)

	    await Form.next()
	    await message.reply("🏠 Укажите место назначения")


# @dp.message_handler(state=Form.destination)
async def set_arrival(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':

	    await state.update_data(arrival=message.text)

	    await Form.next()
	    check_user = await db.get_user_status(message.from_user.id)

	    if check_user.status == 'passenger':
	    	await message.reply("👥 Укажите количество человек")
	    elif check_user.status == 'driver':
	    	await message.reply("👥 Сколько человек вы готовы взять?")


# @dp.message_handler(state=Form.relation)
async def set_people(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':

	    await state.update_data(people=message.text)

	    await Form.next()
	    await message.reply("☎️ Укажите свой телефон или телеграмм аккаунт")


async def set_relation(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':

	    await state.update_data(relation=message.text)

	    await Form.next()

	    await message.reply("📆 Укажите дату поездки (дд.мм.гг):")


async def set_date(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':

		try:
			date_bd = datetime.strptime(message.text, "%d.%m.%y")

			await state.update_data(date=message.text)

			await Form.next()

			check_user = await db.get_user_status(message.from_user.id)

			if check_user.status == 'passenger':
				await message.reply("⏱ Укажите к скольки вам надо быть в пункте назначения (XX:XX):")
			elif check_user.status == 'driver':
				await message.reply("⏱ Укажите во сколько вы готовы выехать (XX:XX):")
		except Exception as _ex:
			return await bot.send_message(message.from_user.id, f'Неправильный формат {_ex}')


# @dp.message_handler(state=Form.date)
async def set_time(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':

		try:
			time_bd = datetime.strptime(message.text, "%H:%M")

			await state.update_data(time=message.text)

			await Form.next()
			async with state.proxy() as data:
				await bot.send_message(message.from_user.id, md.text(
					f'❗️Пожалуйста, проверьте заявку❗️\n\n1️⃣ Поездка:   {data["departure"]} - {data["arrival"]}\n\n2️⃣ Количество человек:   {data["people"]}\n\n3️⃣ Связь:   {data["relation"]}\n\n4️⃣ Дата:   {data["date"]}\n\n5️⃣ Время:   {data["time"]}'), reply_markup=nav.confirmation)
			
		except Exception as _ex:
			return await bot.send_message(message.from_user.id, f'Неправильный формат {_ex}')


# @dp.message_handler(state=Form.response)
async def save_data(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':
		async with state.proxy() as data:
			data['response'] = message.text
			if message.text == 'Подтвердить ✅':

				departure_bd = data['departure']
				arrival_bd = data['arrival']
				people_bd = int(data['people'])
				relation_bd = data['relation']
				date_bd = data['date']
				time_bd = data['time']

				date_bd = datetime.strptime(date_bd, "%d.%m.%y")
				time_bd = datetime.strptime(time_bd, "%H:%M")

				try:

					user_status = await db.get_user_status(message.from_user.id)
					await db.add_new_application(message.from_user.id, departure_bd, arrival_bd, people_bd, relation_bd, date_bd, time_bd, user_status.status)

					await bot.send_message(message.from_user.id, '✅ Заявка была успешно создана!', reply_markup = nav.mainKeyboardMenu)


				except Exception as _ex:
					print('[INFO] Error while working with PostgreSQL', _ex)

			else:
				current_state = await state.get_state()
				if current_state is None:
					return

				await bot.send_message(message.from_user.id, '🗑 Заявка удалена.', reply_markup = nav.mainKeyboardMenu)
		await state.finish()

async def application_menu(call: types.CallbackQuery):

	await bot.delete_message(call.from_user.id, call.message.message_id)

	if call.data == 'btnBackToProfile':
		user_status = await db.get_user_status(call.from_user.id)

		await bot.send_photo(call.from_user.id, photo = open('imgs/info.jpg', 'rb'), caption=f"🆔 {md.bold('Ваш id:')} {call.from_user.id}\n\n🧑🏻‍🔧 {md.bold('Ваш логин:')} {md.code(call.from_user.username)}\n\n📖 {md.bold('Ваш статус:')} {user_status.status}\n\n🔖 {md.bold('Активные заявки:')} {active_req}", reply_markup=nav.profile)

	elif call.data == 'btnDeleteApplication':

		try:

			user_status = await db.get_user_status(call.from_user.id)
			delete_application = await db.delete_application(call.from_user.id, user_status.status)

			await bot.send_message(call.from_user.id, '✅ Заявка успешно удалена', reply_markup = nav.mainKeyboardMenu)

			await bot.send_photo(call.from_user.id, photo = open('imgs/info.jpg', 'rb'), caption=f"🆔 {md.bold('Ваш id:')} {call.from_user.id}\n\n🧑🏻‍🔧 {md.bold('Ваш логин:')} {md.code(call.from_user.username)}\n\n📖 {md.bold('Ваш статус:')} {user_status.status}\n\n🔖 {md.bold('Активные заявки:')} {active_req}", reply_markup=nav.profile)

		except Exception as _ex:

			print('[INFO]', _ex)
			await bot.send_message(call.from_user.id, '❌ Ошибка (если ошибка повториться, пожалуйста, свяжитесь с @w4xdwhyduwy)', reply_markup = nav.mainKeyboardMenu)

	else:
		pass

async def show_subscription(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
	items = await db.show_items()

	item_id = int(callback_data.get("item_id"))

	item = await database.Item.get(item_id)

	await call.message.edit_text(f'{md.bold("ID товара")}:  {item_id}\n\n{md.bold(item.quantity)} заявок  -  {md.code(item.price)} руб', reply_markup=nav.itemPurchase)
	async with state.proxy() as data:
		data['item_id'] = item_id

async def item_menu(call: types.CallbackQuery, state: FSMContext):
	if call.data == 'ItemUserBack':
		await bot.delete_message(call.from_user.id, call.message.message_id)
		items = await db.show_items()
		all_items_menu = await nav.create_items_menu()

		if len(items) == 1:
			await bot.send_message(call.from_user.id, f'Найден {md.bold(len(items))} товар', reply_markup=all_items_menu[1])
		elif len(items) > 1 and len(items) < 5:
			await bot.send_message(call.from_user.id, f'Найдено {md.bold(len(items))} товара', reply_markup=all_items_menu[1])
		elif len(items) > 5:
			await bot.send_message(call.from_user.id, f'Найдено {md.bold(len(items))} товаров', reply_markup=all_items_menu[1])
		else:
			all_items_menu.add(nav.btnBack)
			await bot.send_message(call.from_user.id, f'Список товаров пуст', reply_markup=all_items_menu[1])

	elif call.data == 'ItemUserBuy':
		async with state.proxy() as data:
			item_id = data['item_id']
			item = await database.Item.get(item_id)

			purchase=database.Purchase(
				buyer=call.from_user.id,
            	item_id=item_id,
            	amount=item.price,
            	purchase_time=datetime.now(),
            	successful=False
            	)

		qwe = await purchase.create()

		# await call.message.edit_text(f'buyer - {call.from_user.id}\n\nitem id - {item_id}\n\namount - {item.price}\n\npurchase time - {datetime.now()}')

		currency = "RUB"
		need_name = False
		need_phone_number = False
		need_email = False
		need_shipping_address = False
		await bot.delete_message(call.from_user.id, call.message.message_id)
		await bot.send_invoice(chat_id=call.from_user.id,
                           title=item.quantity,
                           description=item.quantity,
                           payload=str(purchase.id),
                           start_parameter=str(purchase.id),
                           currency=currency,
                           prices=[
                               types.LabeledPrice(label=item.quantity, amount=item.price * 100)
                           ],
                           provider_token=pay_token,
                           need_name=need_name,
                           need_phone_number=need_phone_number,
                           need_email=need_email,
                           need_shipping_address=need_shipping_address
                           )

		await state.update_data(purchase=purchase)

async def checkout(query: types.PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)


async def successful_payment(message: types.Message, state: FSMContext):

    async with state.proxy() as data:
        purchase = data['purchase']

    item_id = purchase.item_id
    item = await database.Item.get(item_id)

    set_sub = await database.Subscriptions.query.where(database.Subscriptions.user_id == message.from_user.id).gino.first()
    await set_sub.update(amount=set_sub.amount+item.quantity).apply()

    await purchase.update(
		successful=True
		).apply()
    await bot.send_message(message.from_user.id, "Спасибо за покупку")
    # else:
    #     await bot.send_message(query.from_user.id, ("Покупка не была подтверждена, попробуйте позже..."))

def register_handlers_client(dp:Dispatcher):
	dp.register_callback_query_handler(set_status, text_contains='set')
	dp.register_message_handler(buttons)
	dp.register_message_handler(command_cancel, state='*', commands='отмена')
	dp.register_callback_query_handler(main_menu, text_contains='send')
	dp.register_callback_query_handler(command_accept, text_contains='app', state=Applications.waiting_for_respons)
	dp.register_callback_query_handler(show_subscription, nav.buy_item.filter())
	dp.register_callback_query_handler(item_menu, text_contains='ItemUser')
	dp.register_pre_checkout_query_handler(checkout)
	dp.register_message_handler(successful_payment, content_types=ContentType.SUCCESSFUL_PAYMENT)
	dp.register_callback_query_handler(profile_operations, text_contains='show')
	dp.register_callback_query_handler(change_status, text_contains='change')
	dp.register_message_handler(set_departure, state=Form.departure)
	dp.register_message_handler(set_arrival, state=Form.arrival)
	dp.register_message_handler(set_people, state=Form.people)
	dp.register_message_handler(set_relation, state=Form.relation)
	# dp.register_message_handler(process_date_invalid, state=Form.date) #lambda message: not message.text.isdigit()
	dp.register_message_handler(set_date, state=Form.date)
	dp.register_message_handler(set_time, state=Form.time)
	dp.register_message_handler(save_data, state=Form.response)
	dp.register_callback_query_handler(application_menu, text_contains='btn')