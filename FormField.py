from flask import Flask 
from flask_wtf import FlaskForm
from wtforms import ( StringField, TextAreaField, PasswordField,
					 SelectField,SelectMultipleField)
# from wtforms.validators import (DataRequired, Regexp,ValidationError,Email,
								# InputRequired, Length, EqualTo, NumberRange)
from wtforms import validators
from wtforms.fields import html5
from models import *

def email_exists(form, field):
	if Admins.select().where(Admins.admin_email == field.data).exists():
		raise validators.ValidationError('Admin with that email already exists.')

def hotel_email_exists(form, field):
	if Hotel.select().where(Hotel.hotel_email == field.data).exists():
		raise validators.ValidationError('Hotel with that email already exists.')

def room_exists(form, field):
	if Room.select().where(Room.number == field.data).exists():
		raise validators.ValidationError('The Room You Entered already exists')


def tg_email_exists(form, field):
	if TourGuide.select().where(TourGuide.email == field.data).exists():
		raise validators.ValidationError('Tour guide with this email already exists')
	

def phone_exists(form,field):
	if Admins.select().where(Admins.admin_phone == field.data).exists():
		raise validators.ValidationError('Admin with that phone number already exists.')

def hotel_phone_exists(form, field):
	if Hotel.select().where(Hotel.hotel_phone == field.data).exists():
		raise validators.ValidationError('Hotel with that phone number already exists.')

def tg_phone_exists(form, field):
	if TourGuide.select().where(TourGuide.phone == field.data).exists():
		raise validators.ValidationError('Tour guide with that phone number already exists.')

def hotel_exists(form, field):
	if Hotel.select().where(Hotel.hotel_name == field.data).exists():
		raise validators.ValidationError('Hotel exists')

def destination_exists(form, field):
	if Place.select().where(Place.name == field.data).exists():
		raise validators.ValidationError('Tourist Destination exists')
		


class RegistrationForm(FlaskForm):

	"""docstring for ClassName"""
	first_name = StringField('First Name',
							 [
							 validators.DataRequired()
							 ])

	last_name = StringField('Last Name',[
							validators.DataRequired()])

	email = StringField('Email',[
								validators.Email(),
						  		validators.DataRequired(),
						  			 email_exists])

	phone_number = StringField("Phone Number",
								[ validators.DataRequired(),
								 			phone_exists])

	address = StringField("Address",[validators.DataRequired()])

	age = html5.IntegerField("Age", [validators.NumberRange(min=18, max=50,
									message="Age must be between 18-50"),
									validators.DataRequired()])

	gender = SelectField("Gender",[validators.DataRequired()],
						choices=[('male','Male'),('female','Female')])
	manager_code = html5.IntegerField('Enter the Your Code',[validators.DataRequired()])
	password = PasswordField('Password', 
							[validators.DataRequired(),
							validators.EqualTo('confirm', message='Passwords do not match')])

	confirm = PasswordField('Confirm Password', [validators.DataRequired()])

		
class LoginForm(FlaskForm):
	email = StringField('Email',[validators.DataRequired(),validators.Email()])
	password = PasswordField('Password', [validators.DataRequired()])

	
class PackageForm(FlaskForm):
	package_title = StringField('package title',[validators.DataRequired()])
	package_detail = TextAreaField('Details',[validators.DataRequired()])
	package_price = html5.IntegerField('Price',[validators.DataRequired()])
	package_days = html5.IntegerField('Number of Days',[validators.DataRequired()])
	package_num = html5.IntegerField('Number of tickets',[validators.DataRequired()])



class NewsForm(FlaskForm):
	news_title = StringField('News title',[validators.DataRequired()])
	news_tag = SelectMultipleField('Tags',[validators.DataRequired()],
							choices=[('#tour and travel','tour and travel' ),
									('#tourism','tourism' ),('#ethiopia','ethiopia'),
									('#packages','packages'),('#News','News'),
									('#tour guides','tour guides'),
									('#tourism minister','tourism minister'),
									('#culture','culture'),('#tourists','tourists')]
							)
	article = TextAreaField('Article',[validators.DataRequired()])



class HotelField(FlaskForm):
	"""docstring for ClassName"""
	hotelname = StringField('Hotel Name',[validators.DataRequired(), hotel_exists])
	location = StringField('Hotel location',[validators.DataRequired()])
	hotelemail = StringField('Hotel Email',[validators.DataRequired(),
											validators.Email(),
											hotel_email_exists])
	hotelphone = StringField('Hotel phone',[validators.DataRequired(),
											hotel_phone_exists])
	hotelstd = SelectField('Standard',[validators.DataRequired()],
								choices=[('3 star','3 star'),
								('4 star','4 star'),
								('5 star','5 star')])
	hotelbio = TextAreaField('Hotel Description',[validators.DataRequired()])
	manager_code = html5.IntegerField('manager code',[validators.DataRequired()])


class RoomField(FlaskForm):
	room_num = StringField('Room Number',[validators.DataRequired(),room_exists])
	beds = html5.IntegerField('Number Of Beds',[validators.DataRequired()])
	price = StringField('Price Of the room per night',[validators.DataRequired()])
	av_at = html5.DateTimeLocalField('av at',[validators.DataRequired()])
	




class TourGuideField(FlaskForm):
	"""Tourguides wtf form """
	def getSkills():
		for skill in Skill.select():
			return skill

	
	tg_fname = StringField('First Name',[validators.DataRequired()])
	tg_lname = StringField('Last Name',[validators.DataRequired()])
	tg_email = StringField('Email',[validators.DataRequired(),
											validators.Email(),
											tg_email_exists])
	tg_phone = StringField('phone Number',[validators.DataRequired(),
										tg_phone_exists])
	tg_address = StringField('Address',[validators.DataRequired()])
	tg_age = html5.IntegerField('Age',[validators.DataRequired(),
										validators.NumberRange(min=18, max=40, 
											message='age must be between 18 and 40') ])
	tg_gender = SelectField('gender',[validators.DataRequired()],
								choices=[('Male','Male'),('Female','Female')])
	tg_skill = SelectMultipleField('Language Skill',
							choices=[
									
							])
	tg_destin = SelectField('location of expertise',[validators.DataRequired()],
							choices=[('',''),('1','South'),('North','North'),('East','East'),('West','West')])


class PlaceField(FlaskForm):
	pname = StringField('Tourist Destination name',
						[validators.DataRequired()])
	plocation=StringField('Tourist Destination location',
						[validators.DataRequired()])
	pdistance=StringField('Distance From A.A',
						[validators.DataRequired()])
	pdetail=TextAreaField('Destination Detail',
						[validators.DataRequired()])


class FBookingForm(FlaskForm):
	fname = StringField('First Name',[validators.DataRequired()])
	lname = StringField('Last Name',[validators.DataRequired()])
	email = StringField('Email',[validators.DataRequired(),
											validators.Email(),
											tg_email_exists])
	phone = StringField('phone Number',[validators.DataRequired(),
										tg_phone_exists])
	nationality = SelectField('Nationality',[validators.DataRequired()],
									choices=[

									])
	tg_age = html5.IntegerField('Age',[validators.DataRequired(),
										validators.NumberRange(min=18, max=40, 
											message='age must be between 18 and 40') ])
	tg_gender = SelectField('gender',[validators.DataRequired()],
								choices=[('Male','Male'),('Female','Female')])
	
	