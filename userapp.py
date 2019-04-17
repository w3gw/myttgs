from flask import (Flask, render_template, url_for,request,
                    redirect, session,flash, logging, g)
from passlib.hash import pbkdf2_sha256
from flask_login import( UserMixin, LoginManager, login_user, current_user,
                        logout_user, login_required)

import os
from werkzeug.utils import secure_filename
import datetime
import models as MD
import FormField 
from utils import *

DEBUG = True
HOST = 'localhost'
PORT = '7000'

UPLOAD_FOLDER = 'static/images'

ALLOWED_EXTENSIONS = set(['txt' , 'pdf' , 'png' , 'jpg' , 'jpeg' , 'gif' ])

managerapp = Flask(__name__)
managerapp.secret_key = 'mysecretkeytodoanything'

managerapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(managerapp)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        return MD.Manager.get(MD.Manager.id == user_id)
    except MD.DoesNotExist:
        return None

@managerapp.before_request
def before_request():
    """ Connect to the database before each request"""
    g.db = MD.DB
    g.db.connect()
    g.user = current_user


@managerapp.after_request
def after_request(response):
    """ Close the database connection after each request """
    g.db.close()
    return response

def allowed_file(filename):
    return '.' in filename and \
    filename.rsplit('.' , 1 )[1 ].lower() in ALLOWED_EXTENSIONS
###############ADMIN ROUTE####################
# check if user is logged in

# route for logout
@managerapp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out', 'success')
    return redirect(url_for('login'))

@managerapp.route('/manager', methods=['POST','GET'])
@login_required
def manager():
	rooms=''
	booked=''
	if MD.Hotel.select().exists():
		rooms = MD.Room.select().where(MD.Room.hotel == g.user.hotel)
		booked = MD.BookedRoom.select()
	
	return render_template('hotel_manager/index.html',rooms=rooms,bookeds=booked)

@managerapp.route('/manager/signup',methods=['POST','GET'])
def signup():
	form = FormField.RegistrationForm()
	if form.validate_on_submit():
		if MD.Hotel.select().where(MD.Hotel.manager_code == form.manager_code.data).exists():
			hotel = MD.Hotel.select().where(MD.Hotel.manager_code == form.manager_code.data).get()
			try:
				MD.Manager.create_manager(
					fname=form.first_name.data,
           			lname =form.last_name.data,
            		email = form.email.data,
	            	phone = form.phone_number.data,
    	        	address=form.address.data,
        	    	age=form.age.data,
            		gender=form.gender.data,
            		hotel=hotel.id,
            		password=form.password.data
					)
			except MD.IntegrityError:
				flash('Already Exists','danger')
			flash('Successfully registered please login ','success')
			return redirect(url_for('login'))
		else:
			flash('Invalid Code Try Again','danger')
			return redirect(url_for('signup'))
	hotels = MD.Hotel.select()
	return render_template('hotel_manager/signup.html',form=form, hotels=hotels)

@managerapp.route('/manager/login',methods=['POST','GET'])
def login():
	form=FormField.LoginForm()
	if form.validate_on_submit():
		try:
		    user = MD.Manager.get_manager(form.email.data)
		except MD.DoesNotExist:
		    pass
		else:
		    if user == None:
		        flash("User DoesNotExist",'danger')
		    else:
		        if pbkdf2_sha256.verify(str(form.password.data), user.password):
		            login_user(user)
		            flash("You have been logged in",'success')
		            return redirect(url_for('manager'))
		        else:
		            flash('Your password or email does not match','danger')
	return render_template('hotel_manager/login.html',form=form)

@managerapp.route('/manager/add-rooms',methods=['POST','GET'])
@login_required
def addrooms():
	form = FormField.RoomField()
	if request.method=='POST':
		try:
			MD.Room.create_room(
				number=request.form['room_num'],
				beds=request.form['beds'],
				price=request.form['price'],
				av_at=request.form['av_at'],
				hotel=g.user.hotel.id
				)
			os.mkdir('static/images/hotels/' + g.user.hotel.hotel_name+"/"+request.form['room_num'])
		except MD.IntegrityError:
			flash('Already Exists','success')
		flash('1 Room Registered','success')
		return redirect(url_for('addrooms'))
	return render_template('hotel_manager/add_hotel_rooms.html',form=form)

@managerapp.route('/manager/update-rooms', methods=['POST','GET'])
@login_required
def updaterooms():
	rooms = MD.Room.select().where(MD.Room.hotel == g.user.hotel)
	if request.method == 'POST':
		try:
			MD.Room.update_room(
				av_at=request.form['av_at'],
				reserved=False,
				number=request.form['tag']
				)
		except MD.IntegrityError:
			flash('Error try again later please','danger')
			return redirect(url_for('updaterooms'))
		flash('You have updated rooms status Successfully','success')
		return redirect(url_for('updaterooms'))
	return render_template('hotel_manager/update_rooms.html',rooms=rooms)



@managerapp.route('/manager/update-hotel',methods=['GET','POST'])
@login_required
def updatehotel():
	if request.method == 'POST':
		MD.Hotel.update_hotel(
			name=request.form['hotel_name'],
			loc=request.form['location'],
			email=request.form['email'],
			phone=request.form['phone'],
			std=request.form['std'],
			bio=request.form['bio'],
			id=g.user.hotel.id
			)
		flash("Successfully Updated Hotel Information",'success')
		return redirect(url_for('updatehotel'))
	return render_template('hotel_manager/update_hotel_info.html')
# upload images
@managerapp.route("/addimages", methods=['POST','GET'])
@login_required
def addhotelimage():
	if request.method == 'POST':
		name=request.form['hotel_name']
		time = datetime.datetime.now()
		try:
			MD.ImageList.saveit(
                name=name,
                savetime=time
                )
		except MD.IntegrityError:
			flash('Already saved','danger')

        # check if the post request has the file part
		if 'file' not in request.files:
			flash(' No file part','danger' )
			return redirect(request.url)
		file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
		if file.filename == ' ' :
			flash(' No selected file','danger' )
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			destin = os.path.join(managerapp.config['UPLOAD_FOLDER']+"/hotels/"+str(name)+"/",
                str(name)+str(time)+".jpg")
			file.save(destin)
		flash('You have added image ','success')
		return redirect(url_for('updatehotel'))
	return render_template('hotel_manager/update_hotel_info.html')
# add hotel Video
# add room image
@managerapp.route('/addroomimage',methods=['POST','GET'])
@login_required
def addroomimage():
	if request.method == 'POST':

		hname=request.form['hotel_name']
		name = request.form['room_num']
		time = datetime.datetime.now()
		try:
			MD.ImageList.saveit(
                name=name,
                savetime=time
                )
		except MD.IntegrityError:
			flash('Already saved','danger')

        # check if the post request has the file part
		if 'file' not in request.files:
			flash(' No file part','danger' )
			return redirect(request.url)
		file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
		if file.filename == ' ' :
			flash(' No selected file','danger' )
			return redirect(request.url)
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			destin = os.path.join(managerapp.config['UPLOAD_FOLDER']+"/hotels/"+str(hname)+"/"+str(name),
                str(name)+str(time)+".jpg")
			file.save(destin)
		flash('You have added image ','success')
		return redirect(url_for('updaterooms'))
	return render_template('hotel_manager/update_rooms.html')
# booking history
@managerapp.route('/manager/history')
@login_required
def history():
	bookedrooms = ''
	if MD.Room.select().where(MD.Room.hotel == g.user.hotel).exists():
		bookedrooms = MD.BookedRoom.select().where(MD.BookedRoom.hotel == g.user.hotel)
	else:
		flash("No Reserved Rooms Yet",'danger')
	return render_template('hotel_manager/boked_history.html',bookedrooms=bookedrooms)
# delete 
@managerapp.route('/delete/<id>/<db_urls>/<name>',methods=['GET','POST'])
@login_required
def delete(id,db_urls,name):  
    try:
        if db_urls == 'Hotel':
            MD.Hotel.get(MD.Hotel.id == id).delete_instance()
            for image in MD.ImageList.select().where(MD.ImageList.imagename==name):
            	os.remove('static/images/hotels/'+name+'/'+str(name)+str(image.save_time)+'.jpg')
            MD.ImageList.get(MD.ImageList.imagename == name).delete_instance()
            flash('Hotel deleted Successfully','success')
            return redirect(url_for('manager'))
        elif db_urls == 'Room':
        	MD.Room.get(MD.Room.id == id).delete_instance()
        	for image in MD.ImageList.select().where(MD.ImageList.imagename==name): 
        		try:
	        		os.remove('static/images/hotels/'
    	    			+g.user.hotel.hotel_name+'/'+name+'/'+str(name)+str(image.save_time)+'.jpg')
	        	except Exception:
	        		flash('Already Deleted ','danger')
	        		return redirect(url_for('updaterooms'))
	        try:
	        	os.rmdir('static/images/hotels/'+g.user.hotel.hotel_name+'/'+str(name))
	        except Exception:
	        	flash('Already Deleted ','danger')
	        	return redirect(url_for('updaterooms'))

        	MD.ImageList.get(MD.ImageList.imagename == name).delete_instance()
        	flash('You have deleted a room Successfully','success')
        	return redirect(url_for('updaterooms'))
    except MD.IntegrityError:
        pass
    return render_template('admin/index.html')

# error handler
@managerapp.errorhandler(404)
def not_found(error):
    return render_template('includes/404.html'),404

if __name__ == '__main__':
	MD.init_All()
	managerapp.run(debug=DEBUG,port=PORT)


	                       