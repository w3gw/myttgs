import datetime
from flask import flash
from peewee import *
from flask_login import UserMixin
from passlib.hash import pbkdf2_sha256

db = 'tourandtravel'
db_user = 'root'
db_pass = ''
db_host = 'localhost'

# DB = MySQLDatabase(db,user=db_user,password=db_pass, host=db_host)

DB = SqliteDatabase('tourandtravel.db',pragmas={
                            'synchronous':0,
                            'journal_mode':'wal'})


class Admins(Model, UserMixin):
    """
        -The System Admins Database Model created to maintain admin information.
        -This class has create admin and get admin methods.
		-Maintains the basic information of system admin
    """
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
    def create_admin(self, fname, lname, email, phone, address, age, gender, password):
        try:
            with DB.transaction():
                self.create(
                    admin_fname=fname,
                    admin_lname=lname,
                    admin_email=email,
                    admin_phone=phone,
                    admin_address=address,
                    admin_age=age,
                    admin_gender=gender,
                    password=pbkdf2_sha256.hash(str(password))
                )
        except IntegrityError:
            pass

    @classmethod
    def get_admin(self, srchstr):
        for admin in Admins.select().where(Admins.admin_email == srchstr):
            return admin


class Package(Model):
    """
    Tour package model for adding and modifying tour packages
    It is extended by purchased package class as a foreignkeyfield
    """
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
    def create_package(self, title, content, price, startdate, tourdate, days, num):
        try:
            with DB.transaction():
                self.create(
                    package_title=title,
                    package_content=content,
                    package_price=price,
                    package_start=startdate,
                    tour_start=tourdate,
                    package_days=days,
                    total_package=num
                )
        except IntegrityError:
            pass

    @classmethod
    def get_package(self):
        for package in Package.select():
            return package

    @classmethod
    def purchasedtour(self):
        return PurchasedPackage.select().where(PurchasedPackage.package == self)


class PurchasedPackage(Model):
    """
        -PurchasePacage Model has foreignkey Field from packages model.
        -This model also contains makepaid function to change the is_paid field
                    if the purchased package is paid.
		-The class instances refer to the personal information of a person who purchased
			the packages
    """
    fullname = CharField()
    email = CharField()
    age = IntegerField()
    gender = CharField()
    package = ForeignKeyField(Package, backref='package',
                    on_delete='CASCADE',on_update='CASCADE')
    is_paid = BooleanField(default=False)
    purchased_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB
        order_by = ('-purchased_at',)

    @classmethod
    def purchase(self, fname, email, age,gender, package):
        try:
            with DB.transaction():
                self.create(
                    fullname=fname,
                    email=email,
                    age=age,
                    gender=gender,
                    package=package
                )
        except IntegrityError:
            pass

    @classmethod
    def makepaid(self, id):
        new = self.get(self.id == id)
        try:
            with DB.transaction():
                if new.is_paid == True:
                    self.update(is_paid=False).where(self.id == id).execute()
                else:
                    self.update(is_paid=True).where(self.id == id).execute()
        except Exception:
            pass


class ImageList(Model):
    """
	-ImageList model is for storing the name and time of images uploaded
	-Images are image of hotel and hotel rooms, and tourist attractions
	"""
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
    """
	-Hotel Model is for storing and modifying hotels list
	"""

    hotel_name = CharField(unique=True)
    hotel_location = CharField()
    hotel_email = CharField(unique=True)
    hotel_phone = CharField(unique=True)
    hotel_standard = CharField()
    hotel_bio = TextField()
    manager_code = IntegerField()
    reg_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB
        order_by = ('-hotel_name',)

    @classmethod
    def create_hotel(self, name, loc, email, phone, std, bio, code):
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
            pass

    @classmethod
    def update_hotel(self, name, loc, email, phone, std, bio, id):
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
    """
		-Manager Model is for handling hotel manager information 
		-It has hotel as ForeignkeyField and other manager personal informations
	"""
    first_name = CharField(max_length=50)
    last_name = CharField(max_length=50)
    email = CharField(unique=True)
    phone = DecimalField(default=None)
    address = CharField(max_length=100, default=None)
    age = CharField()
    gender = CharField(max_length=10)
    hotel = ForeignKeyField(Hotel, backref='hotels',
                    on_delete='CASCADE',on_update='CASCADE')
    password = CharField(max_length=255)

    class Meta:
        database = DB

    @classmethod
    def create_manager(self, fname, lname, email, phone, address, age, gender, hotel, password):
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
    def get_manager(self, srchstr):
        for manager in Manager.select().where(Manager.email == srchstr):
            return manager


class Room(Model):
    """
		-This Room Model is created to create and maintain a specific hotel's rooms
		-The hotel as Foreignkeyfield.
		-There are functions to create/add a room and  update reservation status  
	"""
    beds = IntegerField()
    price = IntegerField()
    total_room = IntegerField()
    available_at = DateTimeField()
    hotel = ForeignKeyField(Hotel, backref='rooms',
                    on_delete='CASCADE',on_update='CASCADE')

    class Meta:
        database = DB

    @classmethod
    def create_room(self, beds, price, number,av_at, hotel):
        try:
            with DB.transaction():
                self.create(
                    beds=beds,
                    price=price,
                    total_room=number,
                    available_at=av_at,
                    hotel=hotel,
                )
        except Exception:
            pass

    @classmethod
    def update_room(self, av_at,total_num, id):
        try:
            with DB.transaction():
                self.update(available_at=av_at,total_room=total_num).where(
                    Room.id == id).execute()
        except Exception as e:
            pass


class Skill(Model):
    """This Class has the list of language skills the tour guide should have"""
    skill_name = CharField(max_length=100)

    class Meta:
        database = DB


class Place(Model):
    """
		-Place Model refers to the tourist attractions/destinations.
		-The Model has methods that add,update and remove places.
		-Price field instace is the price a person has to pay to visit this place per day
	"""
    name = CharField(unique=True)
    location = CharField()
    longtude = DecimalField()
    latitude = DecimalField()
    distance = CharField()
    detail = TextField()
    category = CharField()
    price = IntegerField(default=200)
    reg_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB

    @classmethod
    def create_place(self, name, loc,long,lat,dist, detail, category, price):
        try:
            with DB.transaction():
                self.create(
                    name=name,
                    location=loc,
                    longtude=long,
                    latitude=lat,
                    distance=dist,
                    detail=detail,
                    category=category,
                    price=price
                )
        except IntegrityError:
            pass

    @classmethod
    def update_place(self, name, loc,long,lat, dist, detail, price, id):
        try:
            with DB.transaction():
                self.update(name=name, location=loc,
                            longtude=long,latitude=lat, 
                            distance=dist, detail=detail,
                            price=price).where(Place.id == id).execute()
        except Exception as e:
            pass


class TourGuide(Model):
    """
		-TourGuide Model as the name shows maintains the tour guide's informaiton
	"""
    first_name = CharField(max_length=100)
    last_name = CharField()
    email = CharField(unique=True)
    phone = CharField(unique=True)
    address = CharField()
    age = IntegerField()
    gender = CharField()
    salary = IntegerField()
    reg_time = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB

    @classmethod
    def create_tg(self, fname, lname, email, phone, address, age, gender, salary):
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
            pass

    @classmethod
    def update_tg(self, fname, lname, email, phone, address, age, salary, id):
        try:
            with DB.transaction():
                self.update(
                    first_name=fname,
                    last_name=lname,
                    email=email,
                    phone=phone,
                    address=address,
                    age=age,
                    salary=salary
                ).where(TourGuide.id == id).execute()
        except Exception as e:
            pass

    def getSkill(self, id):
        return (TourGuideSkill
                .select()
                .join(TourGuide,on=( TourGuideSkill.tourguide == id))
                .where(TourGuide.id == id)
                )

    def getPlace(self, id):
        return (TourGuidePlace
                .select()
                .join(TourGuide,on=(TourGuidePlace.tourguide == id) )
                .where(TourGuide.id == id)
                )


class TourGuideSkill(Model):
    """The Model is A relationship model between tourguide and the skill"""
    
    tourguide = ForeignKeyField(TourGuide, backref='tourguide')
    skill = ForeignKeyField(Skill, backref='skill')

    class Meta:
        database = DB


class TourGuidePlace(Model):
    """The Model is a relationship between tourguide and the Place """

    tourguide = ForeignKeyField(TourGuide, backref='tguide')
    place = ForeignKeyField(Place, backref='place')

    class Meta:
        database = DB


class TourInfo(Model):
    """
		-This Model creates and maintains the custom booked tour information.
		-It is mainly about tourist who booked a tour
		-Foreignkey Fields are Place and tourguide.
		-the method makem_paid changes the payment status of the tour if paid and not paid 
    """

    fullname = CharField()
    email = CharField()
    age = CharField()
    gender = CharField()
    place = ForeignKeyField(Place, backref='places',
                    on_delete='CASCADE',on_update='CASCADE')
    people = IntegerField()
    days = IntegerField()
    startdate = DateTimeField()
    tourguide = ForeignKeyField(TourGuide, backref='tourguide',
                    on_delete='CASCADE',on_update='CASCADE')
    is_paid = BooleanField(default=False)
    is_active = BooleanField(default=True)
    book_date = DateTimeField(default=datetime.datetime.now)


    class Meta:
        database = DB
        order_by = ('-book_date',)

    @classmethod
    def create_tour(self, fname, email, age, gender, place, people, days, startdate, tourguide):
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

    @classmethod
    def makepaid(self, id):
        new = self.get(self.id == id)
        try:
            with DB.transaction():
                if new.is_paid == True:
                    self.update(is_paid=False).where(self.id == id).execute()
                else:
                    self.update(is_paid=True).where(self.id == id).execute()
        except Exception:
            pass
    
    @classmethod
    def deativate(self, id):
        new = self.get(self.id == id)
        try:
            with DB.transaction():
                if new.is_active == True:
                    self.update(is_active=False).where(self.id == id).execute()
                else:
                    self.update(is_active=True).where(self.id == id).execute()
        except Exception:
            pass


class BookedRoom(Model):
    """
		-BookedRoom Model Stores the preson information who booked a tour
			then booked hotel room for their tour
		-there are person,room and hotel foreignkeyfields
	"""
    person  = ForeignKeyField(TourInfo,backref='tourinfo')
    phone = CharField()
    days = IntegerField(default=1)
    room = ForeignKeyField(Room, backref='reservedroom')
    reserved = IntegerField()
    hotel = ForeignKeyField(Hotel, backref='hotel',
                    on_delete='CASCADE',on_update='CASCADE')
    is_paid = BooleanField(default=False)
    booked_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB
        order_by = ('-booked_at',)

    @classmethod
    def reserve_room(self, person, phone, days, room, reserved,hotel):
        try:
            with DB.transaction():
                self.create(
                    person=person,
                    phone=phone,
					days=days,
                    room=room,
                    reserved=reserved,
                    hotel=hotel
                )
        except IntegrityError:
            pass

    @classmethod
    def makepaid(self, id):
        new = self.get(self.id == id)
        try:
            with DB.transaction():
                if new.is_paid == True:
                    self.update(is_paid=False).where(self.id == id).execute()
                else:
                    self.update(is_paid=True).where(self.id == id).execute()
        except Exception:
            pass


class PaymentSystem(Model):
    """
		-The Payment Systems list integrated with our system and hotels
		-if the hotel field value is 0 the payment account is for the system
		-if the hotel field value is gt 1 the payment account is for th hotel with id
			value given in the field.
    """
    hotel = ForeignKeyField(Hotel, backref='hotel',default=0,
                    on_delete='CASCADE',on_update='CASCADE')
    system_name = CharField(max_length=255)
    act_name = CharField(max_length=255)
    act_number = CharField(max_length=255)
    links = CharField(max_length=255)
    reg_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB


class PaymentList(Model):
    """
        -This Model lists all the payment informations provided for  purchasing a package
                ,booking a tour and booking a room.
        -The Model contains three payment informations tourpayment,packagepayment and 
            roomspayment for storing one of them at a time. if one of these three is gt 0 
            the other two fields are 0  
        -Other attributes like account_name number refer to the account info of the tourist.
    """
    acount_name = CharField(max_length=255)
    acount_number = CharField(max_length=255)
    reason = CharField(max_length=255)
    price = IntegerField()
    paymentoption = ForeignKeyField(PaymentSystem, backref='option',
                    on_delete='CASCADE',on_update='CASCADE')
    tourpayment = ForeignKeyField(
        TourInfo, backref='tourinfo', default=0, null=True,
                    on_delete='CASCADE',on_update='CASCADE')
    packagepayment = ForeignKeyField(
        PurchasedPackage, backref='purchasedpackage', default=0, null=True,
                    on_delete='CASCADE',on_update='CASCADE')
    roomspayment = ForeignKeyField(
        BookedRoom, backref='bookedrooms', default=0, null=True,
                    on_delete='CASCADE',on_update='CASCADE')

    class Meta:
        database = DB


class TouristReport(Model):
    """
        -This Model Stores reports given from tourists 
    """
    reporter_name = CharField()
    email = CharField()
    victim = CharField()
    victim_name = CharField()
    report = TextField()
    reported_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB
        order_by = ('-reported_at',)

    @classmethod
    def create_report(self, name, email, victim, victim_name, report):
        try:
            with DB.transaction():
                self.create(
                    reporter_name=name,
                    email=email,
                    victim=victim,
                    victim_name=victim_name,
                    report=report
                )
        except IntegrityError:
            pass

class TourGuideReport(Model):
    """
        -This Model Stores reports given from tourguides 
        -Those reports include progress reports and if any issues are raised
        -reports are categorized by progress report, issues report,site details
            like pictures  
    """
    reporter = CharField()
    email = CharField()
    category = CharField() 
    title = CharField()
    report = TextField()
    reported_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB
        order_by = ('-reported_at',)

    @classmethod
    def create_report(self, reporter,email,category,title,report):
        try:
            with DB.transaction():
                self.create(
                    reporter=reporter,
                    email=email,
                    category=category,
                    title=title,
                    report=report
                )
        except IntegrityError:
            pass


class Comment(Model):
    """
        -This Model stores all the feedbacks and comments from the customers.
    """
    fullname = CharField()
    email = CharField()
    content = TextField()
    approved = BooleanField(default=False)
    at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DB
        order_by = ('-at',)

    @classmethod
    def create_comment(self, name, email, content):
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
                    self.update(approved=True).where(
                        Comment.id == comentid).execute()
                elif value == 'False':
                    self.update(approved=False).where(
                        Comment.id == comentid).execute()
        except Exception as e:
            pass


class Asset(Model):
    """Lists of some of the assets of the organization"""
    asset_name = CharField(max_length=255)
    asset_type = CharField(max_length=255)
    available_at = DateTimeField(default=datetime.datetime.now)
    reg_at = DateTimeField(default=datetime.datetime.now())
    is_available = BooleanField(default=True)

    class Meta:
        database = DB

    @classmethod
    def create_asset(self, name, atype, av_at):
        try:
            with DB.transaction():
                self.create(
                    asset_name=name,
                    asset_type=atype,
                    available_at=av_at
                )
        except IntegrityError:
            pass
	

def init_All():
    DB.connect()
    DB.create_tables([	Admins, Package, Hotel, Skill,
                    	TourGuide, Place,
                    	ImageList, TourInfo, PurchasedPackage,
                    	TourGuideReport,TouristReport, Manager,
						Room, BookedRoom, Comment,
                    	TourGuidePlace, TourGuideSkill,
                    	PaymentSystem, PaymentList, Asset], safe=True)
    DB.close()
