from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.utils.callback_data import CallbackData

import database
db = database.DBCommands()

get_item = CallbackData("get", "item_id")
buy_item = CallbackData("buy", "item_id")


############# MAIN KEYBOARD MENU #############
btnMenu = KeyboardButton('🖥 Меню')
btnChat = KeyboardButton('📱 Чат')
btnOwner = KeyboardButton('👤 Владелец')
mainKeyboardMenu = ReplyKeyboardMarkup(resize_keyboard = True, selective=True).row(btnMenu).add(btnOwner, btnChat)#one_time_keyboard=True

############# MAIN MENU #############

mainMenu = InlineKeyboardMarkup(row_width=2)
btnSendReq = InlineKeyboardButton(text='📝 Заявка', callback_data='sendReq')
btnSendProfile = InlineKeyboardButton(text='👨🏻‍💻 Профиль', callback_data='sendProfile')
btnSendChat = InlineKeyboardButton(text='📤 Чат', url='https://t.me/w4xdnu')


mainMenu.insert(btnSendReq)
mainMenu.insert(btnSendProfile)
mainMenu.insert(btnSendChat)

############# MAIN MENU FOR DRIVERS #############

mainMenuForDrivers = InlineKeyboardMarkup(row_width=2)
btnSendReq = InlineKeyboardButton(text='📝 Заявка', callback_data='sendReq')
btnSendProfile = InlineKeyboardButton(text='👨🏻‍💻 Профиль', callback_data='sendProfile')
btnSendChat = InlineKeyboardButton(text='📤 Чат', url='https://t.me/w4xdnu')
btnSendPassengers = InlineKeyboardButton(text='👥 Взять пассажиров', callback_data='sendSubscriptions')

mainMenuForDrivers.insert(btnSendReq)
mainMenuForDrivers.insert(btnSendProfile)
mainMenuForDrivers.insert(btnSendChat)
mainMenuForDrivers.insert(btnSendPassengers)

############# PROFILE MENU #############

profile = InlineKeyboardMarkup(row_width=2)
btnBack = InlineKeyboardButton(text='⬅️ назад', callback_data='showMainMenu')
btnApp = InlineKeyboardButton(text='📝 Моя заявка', callback_data='showApp')
btnChangeStatus = InlineKeyboardButton(text='📌 Поменять статус', callback_data='showOtherStatuses')

profile.insert(btnBack)
profile.insert(btnApp)
profile.insert(btnChangeStatus)

############# PROFILE MENU FOR DRIVERS #############

profileForDrivers = InlineKeyboardMarkup(row_width=2)
btnBack = InlineKeyboardButton(text='⬅️ назад', callback_data='showMainMenu')
btnApp = InlineKeyboardButton(text='📝 Моя заявка', callback_data='showApp')
btnChangeStatus = InlineKeyboardButton(text='📌 Поменять статус', callback_data='showOtherStatuses')
btnBuySub = InlineKeyboardButton(text='💳 Купить подписку', callback_data='showAllSubs')

profileForDrivers.insert(btnChangeStatus)
profileForDrivers.insert(btnApp)
profileForDrivers.insert(btnBuySub)
profileForDrivers.add(btnBack)


############# APPLICATION ERROR/ FROM APPLICATION TO MAIN MENU #############

applicationBack = InlineKeyboardMarkup(row_width=1)

applicationBack.insert(btnBack)


# CONFIRMATION APPLICATION #
btnConfirm = KeyboardButton('Подтвердить ✅')
btnCancel = KeyboardButton('Отменить ⛔')
confirmation = ReplyKeyboardMarkup(resize_keyboard = True, selective=True).add(btnConfirm, btnCancel)


# Application Menu #

request = InlineKeyboardMarkup(row_width=1)
btnBackToProfile = InlineKeyboardButton(text='⬅️ назад', callback_data='btnBackToProfile')
btnDeleteApplication = InlineKeyboardButton(text='🗑 удалить заявку', callback_data='btnDeleteApplication')

request.insert(btnBackToProfile)
request.insert(btnDeleteApplication)



# Identification #

identity = InlineKeyboardMarkup(row_width=2)
btnPassenger = InlineKeyboardButton(text='👤 Я пассажир', callback_data='setPassenger')
btnDriver = InlineKeyboardButton(text='🚗 Я водитель', callback_data='setDriver')

identity.insert(btnPassenger)
identity.insert(btnDriver)


# BackToProfile if Application doesnt exsist #

BackToProfile = InlineKeyboardMarkup(row_width=2)

BackToProfile.insert(btnBackToProfile)


# Сhoose Application #

ChooseApplication = InlineKeyboardMarkup(row_width=2)
btnAccept = InlineKeyboardButton(text='✅ Подтвердить', callback_data='appAccept')
btnRefuse = InlineKeyboardButton(text='⛔ Отказать', callback_data='appRefuse')

ChooseApplication.insert(btnAccept)
ChooseApplication.insert(btnRefuse)

###############
identityChange = InlineKeyboardMarkup(row_width=2)
changePassenger = InlineKeyboardButton(text='👤 Я пассажир', callback_data='changePassenger')
changeDriver = InlineKeyboardButton(text='🚗 Я водитель', callback_data='changeDriver')

identityChange.insert(changePassenger)
identityChange.insert(changeDriver)

# Add New Item #

addItem = InlineKeyboardMarkup(row_width=2)
btnAddItem = InlineKeyboardButton(text='✅ Подтвердить', callback_data='addItem')
btnCancelItem = InlineKeyboardButton(text='⛔ Отказать', callback_data='cancelItem')

addItem.insert(btnAddItem)
addItem.insert(btnCancelItem)

# Item Process #

item = InlineKeyboardMarkup(row_width=1)
backToAllItemsAdmin = InlineKeyboardButton(text='⬅️ назад', callback_data='ItemAdminBack')
deleteItem = InlineKeyboardButton(text='🗑 удалить товар', callback_data='ItemAdminDelete')

item.insert(backToAllItemsAdmin)
item.insert(deleteItem)

# Item Purchase
itemPurchase = InlineKeyboardMarkup(row_width=1)
backToAllItemsUser = InlineKeyboardButton(text='⬅️ назад', callback_data='ItemUserBack')
buyItem = InlineKeyboardButton(text='Купить товар', callback_data='ItemUserBuy')

itemPurchase.insert(backToAllItemsUser)
itemPurchase.insert(buyItem)

async def create_items_menu():
	items = await db.show_items()

	items_menu_for_users = InlineKeyboardMarkup(row_width=2)
	items_menu_for_admins = InlineKeyboardMarkup(row_width=2)
	if len(items) > 0:


		for x, item in enumerate(items):

			x = InlineKeyboardButton(text=f'{item.quantity} заявок - {item.price} руб', callback_data=buy_item.new(item.id))
			items_menu_for_users.insert(x)

			x = InlineKeyboardButton(text=f'{item.quantity} заявок - {item.price} руб', callback_data=get_item.new(item.id))
			items_menu_for_admins.insert(x)

		if len(items) % 2 == 0:
			pass
		else:
			btnEmpty = InlineKeyboardButton(text=' ', callback_data=' ')
			items_menu_for_users.insert(btnEmpty)
			items_menu_for_admins.insert(btnEmpty)

		items_menu_for_users.add(btnBack)

		btnAddSub = InlineKeyboardButton(text='🎟 Добавить подписку', callback_data='btnAddSub')
		items_menu_for_admins.add(btnAddSub)

		btnBackToAdminPanel = InlineKeyboardButton(text='⬅️ назад', callback_data='AdminPanelBack')
		items_menu_for_admins.add(btnBackToAdminPanel)


	else:
		items_menu_for_users.add(btnBack)

		btnAddSub = InlineKeyboardButton(text='🎟 Добавить подписку', callback_data='btnAddSub')
		items_menu_for_admins.add(btnAddSub)

		btnBackToAdminPanel = InlineKeyboardButton(text='⬅️ назад', callback_data='AdminPanelBack')
		items_menu_for_admins.add(btnBackToAdminPanel)

	return items_menu_for_admins, items_menu_for_users

############# ADMIN PANEL #############

adminPanelMain = InlineKeyboardMarkup(row_width=2)
btnItemsManagement = InlineKeyboardButton(text='⚙️ Управление подписками', callback_data='AdminPanelItemsManagement')
btnCloseAdminPanel = InlineKeyboardButton(text='❌ закрыть панель', callback_data='AdminPanelbtnCloseAdminPanel')

adminPanelMain.insert(btnItemsManagement)
adminPanelMain.add(btnCloseAdminPanel)
# adminPanelMain.insert(btnAddSub)