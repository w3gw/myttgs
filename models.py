import datetime
from flask import flash
from peewee import *
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256

db = 'tourandtravel'
db_user = 'wogayehu'
db_pass = '123456'
db_host = 'localhost'

# DB = MySQLDatabase(db,user=db_user,password=db_pass, host=db_host)

DB = SqliteDatabase('tourandtravel.db')

class Admins(Model, UserMixin):
	admin_fname = CharField(max_length=50)
	admin_lname = CharField(max_length=50)
	admin_email = CharField(unique=True)
	admin_phone = DecimalField(default=None)
	admin_address = CharField(max_length=100, default=None)
	admin_age = CharField()
	admin_gender = CharField(max_length=10)
	password = CharField(max_length=255)

	class Meta:
		database = DB


	@classmethod
	def create_admin(self,fname,lname,email,phone,address,age,gender,password):
		try:
			with DB.transaction():
				self.create(
					admin_fname=fname,
           			admin_lname =lname,
           			admin_email = email,
            		admin_phone = phone,
            		admin_address=address,
            		admin_age=age,
            		admin_gender=gender,
            		password=pbkdf2_sha256.hash(str(password))
					)
		except IntegrityError:
			raise ValueError("Admin Already Exists!")

	@classmethod
	def get_admin(self,srchstr):
		for admin in Admins.select().where(Admins.admin_email == srchstr):
			return admin



class Package(Model):
	package_title = CharField(unique=True)
	package_content = TextField()
	package_price = BigIntegerField()
	package_start = DateTimeField()
	tour_start = DateTimeField()
	package_days = IntegerField()
	total_package = IntegerField()
	posted_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DB
		order_by = ('-posted_at',)

	@classmethod
	def create_package(self,title,content,price,startdate,tourdate,days,num):
		try:
			with DB.transaction():
				self.create(
                    package_title =title,
                    package_content=content,
                    package_price = price,
                    package_start = startdate,
                    tour_start = tourdate,
                    package_days=days,
                    total_package=num
					)
		except IntegrityError:
			raise ValueError("Package Already Exists")
	
	@classmethod
	def get_package(self):
		for package in Package.select():
			return package

	@classmethod
	def purchasedtour(self):
		return PurchasedPackage.select().where(PurchasedPackage.package == self)
		

class PurchasedPackage(Model):
	fullname = CharField()
	email = CharField()
	age = IntegerField()
	package = ForeignKeyField(Package, backref='package')
	purchased_at = DateTimeField(default = datetime.datetime.now)
	
	class Meta:
		database = DB
		order_by=('-purchased_at',)
		
	@classmethod
	def purchase(self,fname,email,age,package):
		try:
			with DB.transaction():
				self.create(
					fullname=fname,
					email=email,
					age=age,
					package=package
				)
		except IntegrityError:
			pass


class ImageList(Model):
	imagename = CharField()
	save_time = DateTimeField()

	class Meta:
		database = DB

	@classmethod
	def saveit(self, name, savetime):
		try:
			with DB.transaction():
				self.create(
					imagename=name,
					save_time=savetime
					)
		except IntegrityError:
			raise ValueError()


class Hotel(Model):
	hotel_name = CharField(unique=True)
	hotel_location = CharField()
	hotel_email= CharField(unique=True)
	hotel_phone = CharField(unique=True)
	hotel_standard = CharField()
	hotel_bio = TextField()
	manager_code = IntegerField()
	reg_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DB
		order_by=('-hotel_name',)

	@classmethod
	def create_hotel(self, name, loc,email,phone,std,bio,code):
		try:
			with DB.transaction():
				self.create(
					hotel_name=name,
					hotel_location=loc,
					hotel_email=email,
					hotel_phone=phone,
					hotel_standard=std,
					hotel_bio=bio,
					manager_code=code
					)
		except IntegrityError:
			raise ValueError('Hotel Already Exists')
			flash(ValueError)
	@classmethod		
	def update_hotel(self, name, loc,email,phone,std,bio,id):
		with DB.transaction():
			self.update(
				hotel_name=name,
				hotel_location=loc,
				hotel_email=email,
				hotel_phone=phone,
				hotel_standard=std,
				hotel_bio=bio
				).where(self.id == id).execute()


class Manager(Model, UserMixin):
	first_name = CharField(max_length=50)
	last_name = CharField(max_length=50)
	email = CharField(unique=True)
	phone = DecimalField(default=None)
	address = CharField(max_length=100, default=None)
	age = CharField()
	gender = CharField(max_length=10)
	hotel = ForeignKeyField(Hotel, backref='hotels')
	password = CharField(max_length=255)

	class Meta:
		database = DB

   
	@classmethod
	def create_manager(self, fname,lname,email,phone,address,age,gender,hotel,password):
		try:
			with DB.transaction():
				self.create(
					first_name=fname,
					last_name=lname,
					email=email,
					phone=phone,
					address=address,
					age=age,
					gender=gender,
					hotel=hotel,
					password=pbkdf2_sha256.hash(str(password))
					)
		except IntegrityError:
			pass


	@classmethod
	def get_manager(self,srchstr):
		for manager in Manager.select().where(Manager.email == srchstr):
			return manager

class Room(Model):
	number = CharField(unique=True)
	beds = IntegerField()
	price = IntegerField()
	available_at = DateTimeField()
	hotel = ForeignKeyField(Hotel,backref='rooms')
	reserved = BooleanField(default=False)


	class Meta:
		database=DB

	@classmethod
	def create_room(self,number,beds,price,av_at,hotel):
		try:
			with DB.transaction():
				self.create(
					number=number,
					beds=beds,
					price=price,
					available_at=av_at,
					hotel=hotel
					)
		except IntegrityError:
			pass

	
	@classmethod
	def update_room(self,av_at, reserved,number):
		try:
			with DB.transaction():
				self.update(available_at=av_at, reserved=reserved).where(Room.number == number).execute()
		except Exception as e:
			pass


	@classmethod
	def change_status(self,reserved,room):
		try:
			with DB.transaction():
				self.update(reserved=reserved).where(Room.id == room).execute()
		except Exception as e:
			pass
		

class BookedRoom(Model):
	fullname = CharField()
	email = CharField()
	phone = CharField()
	arrival = DateTimeField()
	days = IntegerField(default=1)
	room = ForeignKeyField(Room, backref='reservedroom')
	hotel = ForeignKeyField(Hotel, backref='hotel')
	booked_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database=DB
		order_by=('-booked_at',)

	@classmethod
	def reserve_room(self, name,email,phone,time,days,room,hotel):
		try:
			with DB.transaction():
				self.create(
					fullname=name,
					email=email,
					phone=phone,
					arrival=time,
					days=days,
					room=room,
					hotel=hotel
					)
		except IntegrityError:
			pass



class News(Model):
	news_title = CharField(unique=True)
	news_tag = CharField(default=None)
	article = TextField()
	posted_at = DateTimeField(default=datetime.datetime.now)


	class Meta:
		database = DB
		order_by = ('-posted_at',)

	@classmethod
	def create_news(self, title,tag,article):
		try:
			with DB.transaction():
				self.create(
					news_title=title,
					news_tag=tag,
					article=article
					)
		except IntegrityError:
			raise ValueError('article with this title Already Exists')
class Skill(Model):
	skill_name = CharField(max_length=100)

	class Meta:
		database=DB


class Place(Model):
	name=CharField(unique=True)
	location=CharField()
	distance=CharField()
	detail=TextField()
	reg_time=DateTimeField(default=datetime.datetime.now)

	class Meta:
		database=DB

	@classmethod
	def create_place(self, name,loc,dist,detail):
		try:
			with DB.transaction():
				self.create(
					name=name,
					location=loc,
					distance=dist,
					detail=detail
					)
		except IntegrityError:
			raise ValueError("Place Exists")

	@classmethod
	def update_place(self, name,loc, dist,detail,id):
		try:
			with DB.transaction():
				self.update(name=name,location=loc,distance=dist,detail=detail).where(Place.id == id).execute()
		except Exception as e:
			print(e)

class TourGuide(Model):
	first_name = CharField(max_length=100)
	last_name = CharField()
	email = CharField(unique=True)
	phone=CharField(unique=True)
	address=CharField()
	age=IntegerField()
	gender = CharField()
	salary = IntegerField()
	reg_time = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database=DB

	@classmethod
	def create_tg(self, fname,lname,email,phone,address,age,gender,salary):
		try:
			with DB.transaction():
				self.create(
					first_name=fname,
					last_name=lname,
					email=email,
					phone=phone,
					address=address,
					age=age,
					gender=gender,
					salary=salary
					)
		except IntegrityError:
			raise ValueError('TourGuide with that email Already Exists')

	@classmethod
	def update_tg(self, fname,lname,email,phone,address,age,gender,salary,id):
		try:
			with DB.transaction():
				self.update(
					first_name=fname,
					last_name=lname,
					email=email,
					phone=phone,
					address=address,
					age=age,
					gender=gender,
					salary=salary
					).where(TourGuide.id == id).execute()
		except Exception as e:
			pass

	def funcname(parameter_list):
		pass

class TourGuideSkill(Model):
	tourguide_name = ForeignKeyField(TourGuide, backref='tourguide')
	skill_name = ForeignKeyField(Skill, backref='skill')
	
	class Meta:
		database = DB


class TourGuidePlace(Model):
	tg_name = ForeignKeyField(TourGuide, backref='tguide')
	place_name = ForeignKeyField(Place, backref='place')

	class Meta:
		database = DB




class TourInfo(Model):
	fullname = CharField()
	email = CharField(unique=True)
	age = CharField()
	gender = CharField()
	place = ForeignKeyField(Place, backref='places')
	people = IntegerField()
	days = IntegerField()
	startdate = DateTimeField()
	tourguide =ForeignKeyField(TourGuide, backref='tourguide')
	book_date = DateTimeField(default=datetime.datetime.now)
	
	class Meta:
		database = DB
		order_by = ('-book_date',)

	@classmethod
	def create_tour(self, fname,email,age,gender,place,people,days, startdate,tourguide):
		try:
			with DB.transaction():
				self.create(
					fullname=fname,
					email=email,
					age=age,
					gender=gender,
					place=place,
					people=people,
					days=days,
					startdate=startdate,
					tourguide=tourguide
					)
		except IntegrityError:
			pass

class Report(Model):
	reporter_name = CharField()
	email = CharField()
	victim = CharField()
	victim_name=CharField()
	report = TextField()
	reported_at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database = DB
		order_by = ('-reported_at',)

	@classmethod
	def create_report(self, name,email,victim,victim_name,report):
		try:
			with DB.transaction():
				self.create(
					reporter_name = name,
					email=email,
					victim=victim,
					victim_name=victim_name,
					report=report
					)
		except IntegrityError:
			pass


class Comment(Model):
	fullname = CharField()
	email = CharField()
	content = TextField()
	approved = BooleanField(default=False)
	at = DateTimeField(default=datetime.datetime.now)

	class Meta:
		database=DB
		order_by=('-at',)

	@classmethod
	def create_comment(self,name,email,content):
		try:
			with DB.transaction():
				self.create(
					fullname=name,
					email=email,
					content=content
					)
		except Exception as e:
			pass

	@classmethod
	def approve(self, value, comentid):
		try:
			with DB.transaction():
				if value == 'True':
					self.update(approved=True).where(Comment.id == comentid).execute()
				elif value == 'False':
					self.update(approved=False).where(Comment.id == comentid).execute()
		except Exception as e:
			pass

class Asset(Model):
	aname = CharField(max_length=255)
	atype = CharField(max_length=255)
	reg_at = DateTimeField(default=datetime.datetime.now())
	is_available = BooleanField(default=True)

def init_All():
	DB.connect()
	DB.create_tables([Admins,Package,News,Hotel,Skill,
	                  TourGuide, Place,
					  ImageList, TourInfo,PurchasedPackage,
					  Report,Manager,Room,BookedRoom,Comment,
					  TourGuidePlace,TourGuideSkill],safe=True)
	DB.close()

# if __name__ == '__main__':
# 	DB.connect()
	# DB.create_tables([Package],safe=True)
	# Skill.create(skill_name = input('Enter lang name:').strip())
	# myp	= Place.select().where(Place.name=='barbara').get()
	# print(Place.select().where(Place.name=='barbara').get().reg_time)
	