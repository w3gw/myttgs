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
PORT = '5000'

UPLOAD_FOLDER = 'static/images'

ALLOWED_EXTENSIONS = set(['txt' , 'mp4' , 'png' , 'jpg' , 'jpeg' , 'gif' ])

# Initialize app and configure database database
adminapp = Flask(__name__)
adminapp.secret_key = "$#ds32Ds3SDS#e32"
adminapp.config['UPLOAD_FOLDER']=UPLOAD_FOLDER


login_manager = LoginManager()
login_manager.init_app(adminapp)
login_manager.login_view = 'adminlogin'

admin_global = current_user 
@login_manager.user_loader
def load_user(user_id):
    try:
        return MD.Admins.get(MD.Admins.id == user_id)
    except MD.DoesNotExist:
        abort(404)
        return None

@adminapp.before_request
def before_request():
    """ Connect to the database before each request"""
    g.db = MD.DB
    g.db.connect()
    g.user = current_user


@adminapp.after_request
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
@adminapp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out', 'success')
    return redirect(url_for('adminlogin'))
# main home route
@adminapp.route("/home")
def mainpage():
    return render_template("admin/homepage.html")    
# login route
@adminapp.route("/admin/login", methods=['POST','GET'])
def adminlogin():
    form = FormField.LoginForm()
    if form.validate_on_submit():    
        try:
            user = MD.Admins.get_admin(form.email.data)
        except MD.DoesNotExist:
            pass
        else:
            if user == None:
                flash("User DoesNotExist",'danger')
            else:
                if pbkdf2_sha256.verify(str(form.password.data), user.password):
                    login_user(user)
                    flash("You have been logged in",'success')
                    return redirect(url_for('index'))
                else:
                    flash('Your password or email does not match','danger')
    return render_template("admin/adminlogin.html",form=form)

# signup route
@adminapp.route("/admin/signup",methods=['POST','GET'] )
def signup():    
    form = FormField.RegistrationForm()
    if form.validate_on_submit():    
        try:
            MD.Admins.create_admin(
                fname=form.first_name.data,
                lname =form.last_name.data,
                email = form.email.data,
                phone = form.phone_number.data,
                address=form.address.data,
                age=form.age.data,
                gender=form.gender.data,
                password=form.password.data
                )
        except ValueError:
            print('error')
        flash("You Are Registered You Can login!","success")
        return redirect(url_for('adminlogin'))
    return render_template("admin/register.html",form=form)


# dashboard route
@adminapp.route("/admin/index")
@login_required
def index():
    comments = MD.Comment.select().limit(2)
    return render_template("admin/index.html",comments=comments)

# packages route
@adminapp.route("/admin/packages")
@login_required
def packages():
    package = MD.Package.select()
    purchased = MD.PurchasedPackage.select()
    return render_template("admin/packages.html", purchased=purchased,packages=package)

# new packages route
@adminapp.route("/admin/add_new_packages", methods=['POST','GET'])
@login_required
def add_packages():
    # form = FormField.PackageForm()
    if request.method == 'POST' :
        MD.Package.create_package(
            title = request.form['title'],
            content=request.form['package_details'],
            price = request.form['price'],
            startdate = request.form['startdate'],
            tourdate = request.form['tourdate'],
            days = request.form['tourdays'],
            num=request.form['tickets'],
            )
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
            destin = os.path.join(adminapp.config['UPLOAD_FOLDER']+"/packages/"
                ,str(request.form['title'])+".jpg")
            file.save(destin)
        flash("You have posted a package successfully",'success')
    return render_template("admin/add_new_package.html")

# news route
@adminapp.route("/admin/news")
@login_required
def news():
    articles = MD.News.select().limit(25)
    return render_template("admin/news.html", articles=articles, user=admin_global)

#add news route
@adminapp.route("/admin/add_news",methods=['POST','GET'])
@login_required
def addnews():
    form = FormField.NewsForm()
    if form.validate_on_submit():
        MD.News.create_news(
            title=form.news_title.data,
            tag=form.news_tag.data,
            article=form.article.data
            )
        flash("News posted successfully",'success')
    return render_template("admin/add_news.html", form=form, user=admin_global)

#hotels route
@adminapp.route("/admin/hotels")
@login_required
def hotels():
    hotels=MD.Hotel.select().limit(25)
    return render_template("admin/hotels.html",hotels=hotels, user=admin_global)

# add new hotels route
@adminapp.route("/admin/add_new_hotel",methods=['POST','GET'])
@login_required
def new_hotel():
    form = FormField.HotelField()
    if form.validate_on_submit():
        MD.Hotel.create_hotel(
            name=form.hotelname.data,
            loc=form.location.data,
            email=form.hotelemail.data,
            phone=form.hotelphone.data,
            std=form.hotelstd.data,
            bio=form.hotelbio.data,
            code=form.manager_code.data
            )
        os.mkdir('static/images/hotels/' + form.hotelname.data)
        flash("Hotel Registered Successfully",'success')
    return render_template("admin/add_new_hotel.html",form=form, user=admin_global)

# tour guides route
@adminapp.route("/admin/tourguides",methods=['GET','POST'])
@login_required
def tourguides():
    tourguides = MD.TourGuide.select().limit(20)
    skills = MD.Skill.select()
    places = MD.Place.select()
    if request.method == 'POST':
        try:
            MD.TourGuide.update_tg(
                fname=request.form['firstname'],
                lname=request.form['lastname'],
                email=request.form['email'],
                phone=request.form['phone'],
                address=request.form['address'],
                age=request.form['age'],
                gender=request.form['gender'],
                skill=request.form['skills'],
                destin=request.form['places'],
                id=request.form['id'] )
        except Exception as e:
            flash('Internal Error Please Try Again later','danger')
            return redirect(url_for('tourguides'))
        flash('Successfully updated '+request.form['firstname']+'\'s information','success')
        return redirect(url_for('tourguides'))
    return render_template("admin/tourguides.html",tourguides=tourguides,skills=skills,places=places)

#add new tourguides route
@adminapp.route("/admin/add_new_tourguide",methods=['GET','POST'])
@login_required
def addtourguide():
    skills = MD.Skill.select()
    places = MD.Place.select()

    if request.method == 'POST':
        try:
            MD.TourGuide.create_tg(
                fname=request.form['firstname'],
                lname=request.form['lastname'],
                email=request.form['email'],
                phone=request.form['phone'],
                address=request.form['address'],
                age=request.form['age'],
                gender=request.form['gender'],
                salary = request.form['salary'])
        except MD.IntegrityError:
            flash("Tour Guide Exists",'danger')

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
            destin = os.path.join(adminapp.config['UPLOAD_FOLDER']+"/tourguides/"
                ,str(request.form['firstname'])+".jpg")
            file.save(destin)
        flash("TourGuide Saved Successfully",'success')
        return redirect(url_for('addtourguide'))
    return render_template("admin/add_new_tourguide.html", 
        places=places,skills=skills,user=admin_global)

# tourist destinations route
@adminapp.route("/admin/place",methods=['GET','POST'])
@login_required
def places():
    place = MD.Place.select()
    # update places information
    if request.method == 'POST':
        try:
            MD.Place.update_place(
                name=request.form['placename'],
                loc=request.form['location'],
                dist=request.form['distance'],
                detail=request.form['detail'],
                id=request.form['id']
                )
        except Exception as e:
            flash('Error please Try again','danger')
            return redirect(url_for('places'))
        flash('You have updated '+request.form['placename']+'\'s information','success' )
        return redirect(url_for('places'))
    return render_template("admin/tourist_destinations.html",places=place, user=admin_global)

# add new places route
@adminapp.route("/admin/add_new_place",methods=['POST','GET'])
@login_required
def addplaces():
    form = FormField.PlaceField()
    if form.validate_on_submit():
        MD.Place.create_place(
            name=form.pname.data,
            loc=form.plocation.data,
            dist=form.pdistance.data,
            detail=form.pdetail.data
            )
        os.mkdir('static/images/places/' + form.pname.data)
        return redirect(url_for('places'))
        flash("Tourist Destination Successfully Saved!",'success')
    return render_template("admin/new_place.html",form=form, user=admin_global)

# edit places
@adminapp.route("/admin/addplaceimage", methods=['POST','GET'])
@login_required
def addplaceimage():
    if request.method == 'POST':
        name = request.form['place_name']
        time = datetime.datetime.now()

        try:
            MD.ImageList.saveit(name=name,savetime=time)
        except Exception as e:
            raise e
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
            destin = os.path.join(adminapp.config['UPLOAD_FOLDER']+"/places/"+name+"/"
                ,str(name)+str(time)+".jpg")
            file.save(destin)
            flash('You Have Added Image For '+name+' Successfully','success')
            return redirect(url_for('places'))
        return render_template('/admin/addplaceimage.html',name=name,user=admin_global)
# tours route
@adminapp.route('/admin/tours', methods=['GET','POST'])
def bookedtours():
    tours = MD.TourInfo.select()
    return render_template('admin/bookedtour.html',tours=tours)

@adminapp.route('/reportslist', methods=['GET','POST'])
def reportslist():
    images = MD.ImageList.select()
    reports = MD.Report.select()
    return render_template('admin/reportslist.html',reports=reports,images=images)
# comments list
@adminapp.route('/admin/comments', methods=['GET','POST'])
@login_required
def comments():
    comments = MD.Comment.select()
    if request.method == 'POST':
        MD.Comment.approve(
            value=request.form['approve'],
            comentid=request.form['commentid']
            )
    return render_template('admin/comments.html',comments=comments)
# settings route
        
@adminapp.route("/admin/settings")
@login_required
def setting():
    return render_template("admin/settings.html", user=admin_global)

# ###############USER ROUTE###########################
# home page route
@adminapp.route('/')
def userhome():
    return render_template('user/index.html')

@adminapp.route('/select-tour', methods=['GET','POST'])
def selecttour():
    places = MD.Place.select()
    tourguides = MD.TourGuide.select()
    if request.method == 'POST':
        try:
            MD.TourInfo.create_tour(
                fname=request.form['fullname'],
                email=request.form['email'] ,
                age=request.form['age'] ,
                gender=request.form['gender'] ,
                place=request.form['placetotravel'],
                people = request.form['people'],
                days=request.form['days'],
                startdate=request.form['start_date'],
                tourguide=request.form['tourguide']
                  )
        except MD.IntegrityError:
            flash('Already Registered','danger')
        # tg = MD.TourGuide.select().where(MD.TourGuide.id == request.form['tourguide']).get()
        # EmailSender.toTourGuide(
        #         fname=request.form['fullname'],
        #         email=request.form['email'] ,
        #         age=request.form['age'] ,
        #         gender=request.form['gender'] ,
        #         place=request.form['placetotravel'],
        #         people = request.form['people'],
        #         days=request.form['days'],
        #         startdate=request.form['start_date'],
        #         tourguide=tg
        #     )
        price = 200 * int(request.form['days'])
        flash('Successfull this is the total price: '+str(price),'success')
    return render_template('user/select_tour.html',places=places,tourguides=tourguides)


@adminapp.route('/book-hotel-room',methods=['POST','GET'])
def bookrooms():
    hotels = MD.Hotel.select()
    rooms = MD.Room.select()
    images =  MD.ImageList.select()
    if request.method == 'POST':
        try:
            MD.BookedRoom.reserve_room(
                name=request.form['fullname'],
                email=request.form['email'],
                phone=request.form['phone'],
                time=request.form['arrivaldate'],
                days=request.form['days'],
                room = request.form['room'],
                hotel=request.form['hotel']
                )
            MD.Room.change_status(reserved=True,room=request.form['room'])
        except MD.IntegrityError:
            flash("Already Reserved",'danger')
        flash('Thank You For Working With us Your Room Will be waiting for you','success')
    return render_template('user/bookhotelroom.html',hotels=hotels,rooms=rooms,images=images)

@adminapp.route('/getpackages', methods=['GET','POST'])
def getPackages():
    packages = MD.Package.select()
    if request.method == 'POST':
        try:
            MD.PurchasedPackage.purchase(
                fname=request.form['fullname'],
                email=request.form['email'],
                age=request.form['age'],
                package=request.form['package'])
        except DB.IntegrityError:
            flash('Your Email Exists retry please')
            return redirect(url_for('getpackages'))
        flash('Thank You For Using Our Services','success')
    return render_template('user/packageslist.html',packages=packages)

@adminapp.route('/makereports', methods=['GET','POST'])
def makereports():
    if request.method == 'POST':
        try:
            MD.Report.create_report(
                name=request.form['fullname'],
                email=request.form['email'],
                victim=request.form['victim'],
                victim_name=request.form['victimname'],
                report=request.form['content']
                )
        except MD.IntegrityError:
            flash('Already Sent','danger')

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
            destin = os.path.join(adminapp.config['UPLOAD_FOLDER']+"/reports/",
                str(request.form['fullname'])+".jpg")
            file.save(destin)
        flash('You have sent a report successfully','success')
        return redirect(url_for('makereports'))

    return render_template('user/makereport.html')

@adminapp.route('/connect', methods=['GET','POST'])
def connect():
    comments = MD.Comment.select().limit(10)
    if request.method == 'POST':
        try:
            MD.Comment.create_comment(
                name=request.form['fullname'],
                email=request.form['email'],
                content=request.form['content']
                )
        except Exception as e:
            flash('Something Went Wrong try Again','danger')
            return redirect(url_for('connect'))
        flash('Thank You For Your Feedbacks','success')
        return redirect(url_for('connect'))
    return render_template('user/connect.html',comments=comments)

# ######################################################
# Other util routes log in and logouts
# 
@adminapp.errorhandler(404)
def not_found(error):
    return render_template('includes/404.html',user=admin_global),404
# util routes
@adminapp.route('/delete/<id>/<db_urls>/<name>',methods=['GET','POST'])
@login_required
def delete(id,db_urls,name):  
    try:
        if db_urls == 'News':
            MD.News.get(MD.News.id == id).delete_instance()
            flash("Article Deleted Successfully","success")
            return redirect(url_for('news'))
        elif db_urls == 'Package':
            MD.Package.get(MD.Package.id == id).delete_instance()
            os.remove('static/images/packages/'+str(name)+'.jpg')    
            flash("Package Deleted Successfully","success")
            return redirect(url_for('packages'))
        elif db_urls == 'Hotel':
            MD.Hotel.get(MD.Hotel.id == id).delete_instance()
            os.rmdir('static/images/hotels/'+str(name))
            flash('Hotel deleted Successfully','success')
            return redirect(url_for('hotels'))
        elif db_urls == 'Place':
            MD.Place.get(MD.Place.id == id).delete_instance()
            for images in MD.ImageList.select().where(MD.ImageList.imagename == name):
                os.remove('static/images/places/'+str(name)+'/'+str(name)+str(image.savetime)+'.jpg')
            os.rmdir('static/images/places'+str(name))
            flash('Place deleted Successfully','success')
            return redirect(url_for('places'))
        elif db_urls == 'Report':
            MD.Report.get(MD.Report.id == id).delete_instance()
            os.remove('static/images/reports/'+str(name)+'.jpg')
            flash('Report deleted Successfully','success')
            return redirect(url_for('reportslist'))    
        elif db_urls == 'TourGuide':
            MD.TourGuide.get(MD.TourGuide.id == id).delete_instance()
            os.remove('static/images/tourguides/'+str(name)+'.jpg')
            flash('TourGuide deleted Successfully','success')
            return redirect(url_for('tourguides'))    
    except MD.IntegrityError:
        pass
    return render_template('admin/index.html', user=admin_global)

if __name__ == '__main__':
    MD.init_All()
    adminapp.run(debug=DEBUG,port=PORT,host=HOST)
