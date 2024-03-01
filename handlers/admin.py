from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import markdown as md
from aiogram.types import ParseMode



from aiogram.utils.callback_data import CallbackData

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from settings import markups as nav
from create_bot import dp, bot
import database

from settings import config as cfg

db = database.DBCommands()


class Item(StatesGroup):
	item_id = State()

class NewItem(StatesGroup):
	quantity = State()
	price = State()
	confirm = State()

async def main_admin_menu(message: types.Message):
	await bot.send_message(message.from_user.id, '👨‍🔧 Панель администратора', reply_markup=nav.adminPanelMain)


async def admin_panel_operations(call: types.CallbackQuery):
	if call.data == 'AdminPanelItemsManagement':
		items = await db.show_items()
		all_items_menu = await nav.create_items_menu()

		if len(items) == 1:
			await call.message.edit_text(f'Найдена {md.bold(len(items))} подписка', reply_markup=all_items_menu[0])
		elif len(items) > 1 and len(items) < 5:
			print(all_items_menu[0])
			await call.message.edit_text(f'Найдено {md.bold(len(items))} подписки', reply_markup=all_items_menu[0])
		elif len(items) > 5:
			await call.message.edit_text(f'Найдено {md.bold(len(items))} подписок', reply_markup=all_items_menu[0])
		else:
			await call.message.edit_text(f'Список товаров пуст', reply_markup=all_items_menu[0])

	elif call.data == 'AdminPanelbtnCloseAdminPanel':
		await bot.delete_message(call.from_user.id, call.message.message_id)

		user_status = await db.get_user_status(call.from_user.id)

		if user_status.status == 'passenger':
			await bot.send_photo(call.from_user.id, photo = open('imgs/menu.jpg', 'rb'), caption=f'Выберите команду:', reply_markup=nav.mainMenu)
		if user_status.status == 'driver':
			await bot.send_photo(call.from_user.id, photo = open('imgs/menu.jpg', 'rb'), caption=f'Выберите команду:', reply_markup=nav.mainMenuForDrivers)

	elif call.data == 'AdminPanelBack':
		await call.message.edit_text('👨‍🔧 Панель администратора', reply_markup=nav.adminPanelMain)


async def add_item(call: types.CallbackQuery):
	await call.message.edit_text('Введите количество заявок:')
	await NewItem.quantity.set()


async def set_quantity(message: types.Message, state: FSMContext):

	try:
		quantity = int(message.text)
	except ValueError:
		await message.answer("Неверное значение, введите число")
		return

	await state.update_data(quantity=message.text)

	await bot.send_message(message.from_user.id, 'Введите цену:')
	await NewItem.next()

async def set_price(message: types.Message, state: FSMContext):

	try:
		price = int(message.text)
	except ValueError:
		await message.answer("Неверное значение, введите число")
		return

	await state.update_data(price=message.text)

	await NewItem.next()

	async with state.proxy() as data:
		await bot.send_message(message.from_user.id, f'Вы хотите добавить новый товар?\n\n{data["quantity"]} - {data["price"]}', reply_markup=nav.addItem)

async def add_item_confirm(call: types.CallbackQuery, state: FSMContext):
	if call.data == 'addItem':
		async with state.proxy() as data:
			quantity = int(data['quantity'])
			price = int(data['price'])

			await db.add_item(quantity, price)
	elif call.data == 'cancelItem':

		await state.reset_state()

		await bot.send_message(call.from_user.id, 'Вы отменили создание товара.')
	await state.finish()


async def cancel_item_creation(message: types.Message, state: FSMContext):
	if message.chat.type == 'private':

	    current_state = await state.get_state()
	    if current_state is None:
	        return

	    await state.finish()

	    await message.reply('Отменено.', reply_markup=nav.adminPanelMain)



async def show_item(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
	items = await db.show_items()

	item_id = int(callback_data.get("item_id"))

	item = await database.Item.get(item_id)

	await call.message.edit_text(f'{md.bold("ID товара")}:  {item_id}\n\n{md.bold(f"{item.quantity} поездок")}  -  {md.code(item.price)}', reply_markup=nav.item)
	async with state.proxy() as data:
		data['item_id'] = item_id


async def item_menu(call: types.CallbackQuery, state: FSMContext):
	if call.data == 'ItemAdminBack':
		items = await db.show_items()
		all_items_menu = await nav.create_items_menu()

		if len(items) == 1:
			await call.message.edit_text(f'Найден {md.bold(len(items))} товар', reply_markup=all_items_menu[0])
		elif len(items) > 1 and len(items) < 5:
			await call.message.edit_text(f'Найдено {md.bold(len(items))} товара', reply_markup=all_items_menu[0])
		elif len(items) > 5:
			await call.message.edit_text(f'Найдено {md.bold(len(items))} товаров', reply_markup=all_items_menu[0])
		else:
			all_items_menu.add(nav.btnBack)
			await call.message.edit_text(f'Список товаров пуст', reply_markup=all_items_menu[0])
			
	elif call.data == 'ItemAdminDelete':
		async with state.proxy() as data:
			item_id = data['item_id']
		item_delete = await db.delete_item(item_id)
		await call.message.edit_text('Товар был удален!')


def register_handlers_admin(dp:Dispatcher):
	dp.register_message_handler(main_admin_menu, user_id=cfg.admin_id, commands=['a'])
	dp.register_callback_query_handler(admin_panel_operations, text_contains='AdminPanel')
	# dp.register_message_handler(cancel_item_creation, user_id=cfg.admin_id, state='*', commands=['отмена'])
	dp.register_callback_query_handler(add_item, text='btnAddSub')
	dp.register_message_handler(set_quantity, state=NewItem.quantity)
	dp.register_message_handler(set_price, state=NewItem.price)
	dp.register_callback_query_handler(add_item_confirm, state=NewItem.confirm)
	dp.register_callback_query_handler(show_item, nav.get_item.filter())
	dp.register_callback_query_handler(item_menu, text_contains='ItemAdmin')