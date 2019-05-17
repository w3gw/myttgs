import datetime
import os

from werkzeug.utils import secure_filename

import FormField
import models as MD
from flask import (Flask, flash, g, logging, redirect, render_template,
                   request, session, url_for)
from flask_login import (LoginManager, UserMixin, current_user, login_required,
                         login_user, logout_user)
from passlib.hash import pbkdf2_sha256
from flask_mail import Mail, Message

DEBUG = True
HOST = '10.42.0.1'
PORT = '7000'

UPLOAD_FOLDER = 'static/images'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# Initialize Manager app
managerapp = Flask(__name__)
managerapp.secret_key = 'mysecretkeytodoanything'

# initialize managers upload folder
managerapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


managerapp.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME='wnorar@gmail.com',
        MAIL_PASSWORD='wogayehumeki'
    )
mail = Mail(managerapp)

# manager session configuration
login_manager = LoginManager()
login_manager.init_app(managerapp)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
	"""Load manager session"""
	try:
		return MD.Manager.get(MD.Manager.id == user_id)
	except MD.DoesNotExist:
		abort(404)

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
###############Manager ROUTE####################

# route for logout
@managerapp.route('/logout')
@login_required
def logout():
	"""logout manager"""
	logout_user()
	flash('You are logged out', 'success')
	return redirect(url_for('login'))

@managerapp.route('/manager', methods=['POST','GET'])
@login_required
def manager():
	"""manager home page route"""
	rooms=''
	booked=''
	if MD.Hotel.select().exists():
		rooms = MD.Room.select().where(MD.Room.hotel == g.user.hotel)
		booked = MD.BookedRoom.select()
	if request.method == 'POST':
		try:
			with MD.DB.transaction():
				MD.PaymentSystem.create(
					hotel = request.form['hotel'],
					system_name = request.form['system-name'],
					act_name = request.form['account-name'],
					act_number = request.form['account-number'],
					links = request.form['system-info']
				)
		except Exception:
			flash("Internal Error try again later:",'danger')
			return redirect(url_for('manager'))
		return redirect(url_for('manager'))

	return render_template('hotel_manager/index.html',rooms=rooms,bookeds=booked)

@managerapp.route('/manager/signup',methods=['POST','GET'])
def signup():
	"""manager signup/register route"""
	form = FormField.RegistrationForm()
	if request.method == 'POST' :
		if MD.Hotel.select().where(MD.Hotel.manager_code == form.manager_code.data).exists():
			hotel = MD.Hotel.select().where(MD.Hotel.manager_code == form.manager_code.data).get()
			try:
				MD.Manager.create_manager(
					fname=form.first_name.data,
           			lname =form.last_name.data,
            		email = form.manager_email.data,
	            	phone = form.phone_number.data,
    	        	address=form.address.data,
        	    	age=form.age.data,
            		gender=form.gender.data,
            		hotel=hotel.id,
            		password=form.password.data
					)
			except Exception:
				flash('Internal Error Try again later','danger')
				return redirect(url_for('signup'))
			flash('Successfully registered please login ','success')
			return redirect(url_for('login'))
		else:
			flash('Invalid Code Try Again','danger')
			return redirect(url_for('signup'))
	hotels = MD.Hotel.select()
	return render_template('hotel_manager/signup.html',form=form, hotels=hotels)

@managerapp.route('/manager/login',methods=['POST','GET'])
def login():
	"""manager login route"""
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
	"""manager route for adding rooms"""
	form = FormField.RoomField()
	if request.method=='POST':
		try:
			MD.Room.create_room(
				beds=request.form['beds'],
				price=request.form['price'],
				number=request.form['totalnumber'],
				av_at=request.form['av_at'],
				hotel=g.user.hotel.id
				)
			os.mkdir('static/images/hotels/' + g.user.hotel.hotel_name+"/"+request.form['beds'])
		except Exception as e:
			print(e)
			flash('Internal Error Try again','danger')
			return redirect(url_for('addrooms'))
		flash(request.form['totalnumber']+' Rooms Registered','success')
		return redirect(url_for('addrooms'))
	return render_template('hotel_manager/add_hotel_rooms.html',form=form)

@managerapp.route('/manager/update-rooms', methods=['POST','GET'])
@login_required
def updaterooms():
	"""manager route for updating rooms."""

	rooms = MD.Room.select().where(MD.Room.hotel == g.user.hotel)
	bookedrooms = MD.BookedRoom.select().where(MD.BookedRoom.hotel == g.user.hotel)
	if request.method == 'POST':
		try:
			MD.Room.update_room(
				av_at=request.form['av_at'],
				total_num=request.form['totalnumber'],
				id=request.form['tag']
				)
		except Exception as e:
			print(e)
			flash('Internal Error try again later please','danger')
			return redirect(url_for('updaterooms'))
		flash('You have updated rooms status Successfully','success')
		return redirect(url_for('updaterooms'))
	return render_template('hotel_manager/update_rooms.html',
						bookedrooms=bookedrooms,rooms=rooms)


@managerapp.route('/manager/makepaid/',methods=['GET','POST'])
@login_required
def makepayment():
	"""manager route for making the payment status of booked rooms"""

	if request.method == 'POST':
		try:
			MD.BookedRoom.makepaid(
				id = request.form['id'],
			)
		except Exception as e:
			flash("Internal Error try again later: ","danger")
			return redirect(url_for('reservedroom'))
		# get person booked a room
		room_person = MD.BookedRoom.select().where(MD.BookedRoom.id == request.form['id']).get()
		# send email notification
		send_mail(
            receiver=room_person.person.email,
            message = """\n
                        Hello there %s You have completed booking a room and payed \n
						the appropriate fee thank you. the rooms you requested will\n
						be waiting for you.  \n
                
				        Thank You!
                    """%(room_person.person.fullname)
            ) 
	return redirect(url_for('reservedroom'))

@managerapp.route('/manager/reserved-rooms',methods=['GET','POST'])
@login_required
def reservedroom():
	"""manager route for list of reserved rooms """

	roomid = request.args.get('id')	
	bookedrooms = ''
	paymentinfo = MD.PaymentList.select().where(MD.PaymentList.roomspayment > 0)
	if MD.Room.select().where(MD.Room.hotel == g.user.hotel).exists():
		bookedrooms = MD.BookedRoom.select().where(MD.BookedRoom.room == roomid)
	else:
		flash("No Reserved Rooms Yet",'danger')
	return render_template('/hotel_manager/reserved_rooms.html',paymentinfo=paymentinfo,
						bookedrooms=bookedrooms)

@managerapp.route('/manager/update-hotel',methods=['GET','POST'])
@login_required
def updatehotel():
	"""manger route for updating the hotel status"""
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
	"""route for uploading hotel image to the static folder"""
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
			return redirect(url_for('addhotelimage'))
			"""upload image"""
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


# add room image
@managerapp.route('/addroomimage',methods=['POST','GET'])
@login_required
def addroomimage():
	if request.method == 'POST':
		hname=request.form['hotel_name']
		name = request.form['beds']
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
@managerapp.route('/manager/history',methods=['GET','POST'])
@login_required
def history():
	"""route for booked rooms history"""
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
    except Exception:
        flash("Internal Error try again later:",'danger')
    return render_template('admin/index.html')

# error handler
@managerapp.errorhandler(404)
def not_found(error):
    return render_template('includes/404m.html'),404

# Function to send email
def send_mail(receiver, message):
    try:
        msg = Message("Tour And Travel Guidance System",
                      sender="wnorar@gmail.com",
                      recipients=[receiver])
        msg.body = message
        mail.send(msg)
        print('Mail sent! to '+receiver)
    except Exception as e:
        return(str(e))

if __name__ == '__main__':
	MD.init_All()
	managerapp.run(debug=DEBUG,port=PORT)
