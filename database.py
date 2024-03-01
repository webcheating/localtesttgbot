from aiogram import types, Bot
from gino import Gino
from sqlalchemy import (Column, Integer, BigInteger, String, Sequence, TIMESTAMP, Boolean, JSON, Text, Date, Time)
from sqlalchemy import sql
from gino.schema import GinoSchemaVisitor

from settings.config import db_password, db_user, db_host, db_name

import datetime

db = Gino()

class User(db.Model):
	__tablename__ = 'users'
	id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
	user_id = Column(BigInteger)
	status = Column(Text)
	# relation = Column(String)


	# def __repr__(self):
	# 	return f"<User(destination={self.destination})>"#, people={self.people}, relation={self.relation}, date={self.date}, time={self.time}

class Passenger(db.Model):
	__tablename__ = 'passengers'
	id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
	user_id = Column(BigInteger)
	departure = Column(Text)
	arrival = Column(Text)
	people = Column(Integer)
	relation = Column(String)
	date = Column(Date)
	time = Column(Time)
	driver = Column(BigInteger)


class Driver(db.Model):
	__tablename__ = 'drivers'
	id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
	user_id = Column(BigInteger)
	departure = Column(Text)
	arrival = Column(Text)
	people = Column(Integer)
	relation = Column(String)
	date = Column(Date)
	time = Column(Time)

class Item(db.Model):
	__tablename__ = 'items'
	id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
	quantity = Column(Integer)
	price = Column(Integer)

class Purchase(db.Model):
	__tablename__ = 'purchases'
	id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
	buyer = Column(BigInteger)
	item_id = Column(Integer)
	amount = Column(Integer)
	purchase_time = Column(TIMESTAMP)
	successful = Column(Boolean, default=False)

class Subscriptions(db.Model):
	__tablename__ = 'subscriptions'
	id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
	user_id = Column(BigInteger)
	amount = Column(Integer)

	

class DBCommands:

	#################### USER STATUS/ALL USERS ###############################################

	async def get_user_status(self, user_id) -> User:
		
		user = await User.query.where(User.user_id == user_id).gino.first()
		return user


	async def identity_user(self, user_id, status) -> User:

		user = await User.query.where(User.user_id == user_id).gino.first()
		if user:
			return user
		else:
			new_user = User()
			new_user.user_id = user_id
			new_user.status = status

			await new_user.create()
			return new_user


	#################### PASSENGERS/DRIVERS ###############################################

	async def get_user_info(self, user_id, status) -> Passenger:

		if status == 'passenger':
			passenger = await Passenger.query.where(Passenger.user_id == user_id).gino.first()
		# passengers = await Passenger.query.where(Passenger.destination == 'мск-самара').gino.all()
		# return passengers
			return passenger

		elif status == 'driver':
			driver = await Driver.query.where(Driver.user_id == user_id).gino.first()
			return driver
		###
		# users_info = await db.get_passengers_info(call.from_user.id)
		# for i in users_info:
		# 	print(i.user_id)

	async def get_application_info(self, user_id, status) -> Passenger:

		if status == 'passenger':
			passenger = await Passenger.query.where(Passenger.user_id == user_id).gino.first()
			return passenger
		elif status == 'driver':
			driver = await Driver.query.where(Driver.user_id == user_id).gino.first()
			return driver


	async def add_new_application(self, user_id, departure, arrival, people, relation, date, time, status): #, destination, people, relation, date, time
		user = types.User.get_current()
		old_user = await self.get_user_info(user_id, status)

		if old_user:
				return old_user

		if status == 'passenger':

			new_user = Passenger()
			new_user.user_id = user.id
			new_user.departure = departure
			new_user.arrival = arrival
			new_user.people = people
			new_user.relation = relation
			new_user.date = date
			new_user.time = time
			new_user.driver = None

			await new_user.create()
			return new_user

		elif status == 'driver':

			new_user = Driver()
			new_user.user_id = user.id
			new_user.departure = departure
			new_user.arrival = arrival
			new_user.people = people
			new_user.relation = relation
			new_user.date = date
			new_user.time = time

			await new_user.create()
			return new_user


	async def delete_application(self, user_id, status) -> Passenger:

		if status == 'passenger':
			user = await self.get_user_info(user_id, 'passenger')

			await user.delete()

		elif status == 'driver':
			user = await self.get_user_info(user_id, 'driver')

			await user.delete()

	async def update_status(self, user_id, status):

		user = await self.get_user_status(user_id)

		await user.update(status = status).apply()


	#################### FILTRATION ###############################################

	async def filtration(self, user_id, status):

		user = await self.get_user_info(user_id, status)

		passengers = await Passenger.query.gino.all()

		proposed_passengers = []

		for passenger in passengers:
			if passenger.driver == None:
				if passenger.departure == user.departure:
					if passenger.arrival == user.arrival:
						if passenger.date == user.date:

							proposed_passengers.append(passenger.user_id)

		return proposed_passengers

	#################### ITEMS ###############################################

	async def add_item(self, quantity, price):

		new_item = Item()
		new_item.quantity = quantity
		new_item.price = price

		await new_item.create()
		return new_item

	async def show_items(self):
		items = await Item.query.gino.all()

		return items

	async def delete_item(self, item_id):
		item = await Item.query.where(Item.id == item_id).gino.first()

		await item.delete()

async def create_db():
	await db.set_bind(f'postgresql://{db_user}:{db_password}@{db_host}/{db_name}')
	await db.gino.drop_all()
	await db.gino.create_all()
	db.gino: GinoSchemaVisitor
	print('good!')