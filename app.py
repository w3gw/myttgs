import datetime
import os

from werkzeug.utils import secure_filename

import FormField
import models as MD
from resources.attractions import attraction_api

from flask import (Flask, flash, g, jsonify, logging, redirect,
                   render_template, request, session, url_for)
from flask_login import (
    LoginManager, UserMixin, current_user, login_required, login_user,
    logout_user)
from flask_mail import Mail, Message
from passlib.hash import pbkdf2_sha256

DEBUG = True
HOST = '10.42.0.1'
PORT = '7000'

UPLOAD_FOLDER = 'static/images'

ALLOWED_EXTENSIONS = set(['txt', 'mp4', 'png', 'jpg', 'jpeg', 'gif'])

# Initialize flask app
adminapp = Flask(__name__)
adminapp.secret_key = "$#ds32Ds3SDS#e32"
adminapp.register_blueprint(attraction_api)

# configure upload folder for images and files
adminapp.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# flask mail configuration
adminapp.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
        MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=465,
        MAIL_USE_SSL=True,
        MAIL_USERNAME='wnorar@gmail.com',
        MAIL_PASSWORD='wogayehumeki'
    )
mail = Mail(adminapp)

# login manager configuration and bind with flask app
login_manager = LoginManager()
login_manager.init_app(adminapp)
login_manager.login_view = 'adminlogin'

admin_global = current_user
@login_manager.user_loader
def load_user(user_id):
    """Loads the logged in user/session """
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
    """check image extensions that are allowed to upload """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
###############ADMIN ROUTE####################

# route for logout
@adminapp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You are logged out', 'success')
    return redirect(url_for('adminlogin'))
# main home route
@adminapp.route("/admin/home")
def mainpage():
    """The Admin Home Page Interface Before Logged in """
    return render_template("admin/homepage.html")


@adminapp.route("/admin/login", methods=['POST', 'GET'])
def adminlogin():
    """admin login route   """
    form = FormField.LoginForm()
    if form.validate_on_submit():
        try:
            user = MD.Admins.get_admin(form.email.data)
        except MD.DoesNotExist:
            pass
        else:
            if user == None:
                flash("User DoesNotExist", 'danger')
            else:
                if pbkdf2_sha256.verify(str(form.password.data), user.password):
                    login_user(user)
                    flash("You have been logged in", 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Your password or email does not match', 'danger')
    return render_template("admin/adminlogin.html", form=form)


@adminapp.route("/admin/signup", methods=['POST', 'GET'])
def signup():
    """Admin Signup/registration route"""
    form = FormField.RegistrationForm()
    if request.method == 'POST':
        try:
            MD.Admins.create_admin(
                fname=form.first_name.data,
                lname=form.last_name.data,
                email=form.email.data,
                phone=form.phone_number.data,
                address=form.address.data,
                age=form.age.data,
                gender=form.gender.data,
                password=form.password.data
            )
        except ValueError:
            flash("Internal Error Try Again Later", 'danger')
            return redirect(url_for('signup'))
        flash("You Are Registered You Can login!", "success")
        return redirect(url_for('adminlogin'))
    return render_template("admin/register.html", form=form)


# dashboard route
@adminapp.route("/admin/index", methods=['GET','POST'])
@login_required
def index():
    """The admin home route it shows some of comments and reports and add payment systems """
    if request.method == 'POST':
        try:
            with MD.DB.transaction():
                MD.PaymentSystem.create(
                    system_name = request.form['system-name'],
                    act_name = request.form['account-name'],
                    act_number = request.form['account-number'],
                    links = request.form['system-info']
                )
        except Exception:
            flash("Internal Error try again later:",'danger')
            return redirect(url_for('index'))
        return redirect(url_for('index'))

    comments = MD.Comment.select().limit(2)
    tourist_report = MD.TouristReport.select().limit(3)
    tourguide_report = MD.TourGuideReport.select().limit(3)
    paymentsystems = MD.PaymentSystem.select().where(MD.PaymentSystem.hotel == 0)
    return render_template("admin/index.html",
                           comments=comments,
                           tourist_report=tourist_report,
                           tourguide_report=tourguide_report,
                           paymentsystems=paymentsystems)

# packages route
@adminapp.route("/admin/packages")
@login_required
def packages():
    """The admin package route for listing created packages"""
    package = MD.Package.select()
    purchased = MD.PurchasedPackage.select()
    return render_template("admin/packages.html",
                           purchased=purchased,
                           packages=package)

# new packages route
@adminapp.route("/admin/add_new_packages", methods=['POST', 'GET'])
@login_required
def add_packages():
    """The admin route for adding new packages and images for the package """
    # form = FormField.PackageForm()
    if request.method == 'POST':
        MD.Package.create_package(
            title=request.form['title'],
            content=request.form['package_details'],
            price=request.form['price'],
            startdate=request.form['startdate'],
            tourdate=request.form['tourdate'],
            days=request.form['tourdays'],
            num=request.form['tickets'],
        )
        """ uploading package images"""
         # check if the post request has the file part
        if 'file' not in request.files:
            flash(' No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
         # submit an empty part without filename
        if file.filename == ' ':
            flash(' No selected image', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            destin = os.path.join(
                adminapp.config['UPLOAD_FOLDER']+"/packages/",
                str(request.form['title'])+".jpg")
            file.save(destin)
        flash("You have Created a Tour Package successfully", 'success')
        return redirect(url_for('packages'))
    return render_template("admin/add_new_package.html")


# hotels route
@adminapp.route("/admin/hotels")
@login_required
def hotels():
    """The admin route for listing registered hotels """
    hotels = MD.Hotel.select().limit(25)
    return render_template("admin/hotels.html", hotels=hotels)

# add new hotels route
@adminapp.route("/admin/add_new_hotel", methods=['POST', 'GET'])
@login_required
def new_hotel():
    """The admin route for adding new hotels """
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
        flash("Hotel Registered Successfully", 'success')
    return render_template("admin/add_new_hotel.html", form=form)

# tour guides route
@adminapp.route("/admin/tourguides", methods=['GET', 'POST'])
@login_required
def tourguides():
    """admin route for listing tourguides that are registered and updating their status"""
    tourguides = MD.TourGuide.select().limit(20)
    skills = MD.Skill.select()
    places = MD.Place.select()
    # update tourguide information.
    if request.method == 'POST':
        try:
            MD.TourGuide.update_tg(
                fname=request.form['firstname'],
                lname=request.form['lastname'],
                email=request.form['email'],
                phone=request.form['phone'],
                address=request.form['address'],
                age=request.form['age'],
                salary=request.form['salary'],
                id=request.form['id'])
        except Exception as e:
            flash('Internal Error Please Try Again later', 'danger')
            return redirect(url_for('tourguides'))
        flash('You Successfully updated ' +
              request.form['firstname']+'\'s information', 'success')
        return redirect(url_for('tourguides'))
    return render_template("admin/tourguides.html",
                            tourguides=tourguides,
                            skills=skills,
                           places=places)

# add skills for tour guide
@adminapp.route("/addskill", methods=['POST'])
@login_required
def addskill():
    """admin route for adding language skill and sites the tourguides work on"""
    if request.method == 'POST':
        try:
            with MD.DB.transaction():
                if request.form['skill'] == '':
                    pass
                else:
                    MD.TourGuideSkill.create(
                        tourguide=request.form['tourguide'],
                        skill=request.form['skill']
                    )
                if request.form['place'] == '':
                    pass
                else:
                    MD.TourGuidePlace.create(
                        tourguide=request.form['tourguide'],
                        place=request.form['place']
                    )
        except MD.IntegrityError as e:
            flash('Internal Error Try Again Later', 'danger')
            return redirect(url_for('tourguides'))
        flash("You Successfully updated tour guide status", 'success')
        return redirect(url_for('tourguides'))
    return render_template('/admin/tourguides.html')


# add new tourguides route
@adminapp.route("/admin/add_new_tourguide", methods=['GET', 'POST'])
@login_required
def addtourguide():
    """admin route for adding/registering new tourguide and uploading image"""

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
                salary=request.form['salary'])
        except MD.IntegrityError:
            flash("Tour Guide Exists Try again", 'danger')
            return redirect(url_for("addtourguide"))

        """uploading tourguide avatar image"""
        if 'file' not in request.files:
            flash(' No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == ' ':
            flash(' No selected image', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            destin = os.path.join(
                adminapp.config['UPLOAD_FOLDER']+"/tourguides/",
                str(request.form['firstname'])+".jpg")
            file.save(destin)
        flash("TourGuide Saved Successfully", 'success')
        return redirect(url_for('addtourguide'))
    return render_template("admin/add_new_tourguide.html")

# tourist destinations route
@adminapp.route("/admin/place", methods=['GET', 'POST'])
@login_required
def places():
    """admin route for listing registered tourist attractions 
       and to update these informations. """
    place = MD.Place.select()
    # update places information
    if request.method == 'POST':
        try:
            MD.Place.update_place(
                name=request.form['placename'],
                loc=request.form['location'],
                long= request.form['long'],
                lat= request.form['latitude'],
                dist=request.form['distance'],
                detail=request.form['detail'],
                price=request.form['price'],
                id=request.form['id']
            )
        except Exception as e:
            flash('Internal Error please Try again later', 'danger')
            return redirect(url_for('places'))
        flash('You have updated ' +
              request.form['placename']+'\'s information', 'success')
        return redirect(url_for('places'))
    return render_template("admin/tourist_destinations.html", places=place)

# add new places route
@adminapp.route("/admin/add_new_place", methods=['POST', 'GET'])
@login_required
def addplaces():
    """admin route for addint new tourist attractions."""
    form = FormField.PlaceField()
    if form.validate_on_submit():
        MD.Place.create_place(
            name=form.pname.data,
            loc=form.plocation.data,
            long=form.longfield.data,
            lat=form.latfield.data,
            dist=form.pdistance.data,
            detail=form.pdetail.data,
            category=form.category.data,
            price=form.pprice.data
        )
        os.mkdir('static/images/places/' + form.pname.data)
        return redirect(url_for('places'))
        flash("Tourist Destination Successfully Saved!", 'success')
    return render_template("admin/new_place.html", form=form)

# edit places
@adminapp.route("/admin/addplaceimage", methods=['POST', 'GET'])
@login_required
def addplaceimage():
    """admin route for adding images for tourist attractions"""
    if request.method == 'POST':
        name = request.form['place_name']
        time = datetime.datetime.now()

        try:
            MD.ImageList.saveit(name=name, savetime=time)
        except Exception as e:
            pass

        """uploading place image"""
        # check if the post request has the file part
        if 'file' not in request.files:
            flash(' No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == ' ':
            flash(' No selected image', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            destin = os.path.join(
                adminapp.config['UPLOAD_FOLDER']+"/places/"+name+"/", str(name)+str(time)+".jpg")
            file.save(destin)
            flash('You Have Added Image For '+name+' Successfully', 'success')
            return redirect(url_for('places'))
        return render_template('admin/tourist_destinations.html', name=name)


# tours route
@adminapp.route('/admin/tours', methods=['GET', 'POST'])
def bookedtours():
    """admin route for listing/viewing booked tours and updating tour status"""
    tours = ''
    bookedrooms = MD.BookedRoom.select()
    if MD.TourInfo.select().exists():
        tours = MD.TourInfo.select()
    paymentinfo = MD.PaymentList.select().where(MD.PaymentList.tourpayment > 0)
    if request.method == 'POST':
        MD.TourInfo.makepaid(
            id=request.form['id']
        )
        tour_person = MD.TourInfo.select().where(MD.TourInfo.id == request.form['id']).get()
        booked_hotel = MD.BookedRoom.select().where(MD.BookedRoom.person == tour_person.id).get()
    #    send email notification
        send_mail(
            receiver=tour_person.email,
            message = """\n
                        Hello there %s You have completed booking and payed for your
                        custom tour to %s. Email will be sent to you for further notifications.

                        Thank You!
                    """%(tour_person.fullname,tour_person.place.name )
            ) 
            # send mail notification to the tour guide
        send_mail(
            receiver=tour_person.tourguide.email,
            message = """
                        Hello there %s %s !\n
                        Tourist with the following information selected you to guide him/her\n
                        for a custom tour he/she booked. please be there at the provided time.\n

                        Thank You!\n\n

                        Tourist Name: %s ,\n
                        Tourist Email: %s,\n
                        Tourist Phone: %s,\n
                        Tourist Gender: %s,\n
                        Tourist age: %s\n
                        Number of people: %s,\n
                        Number of days: %s,\n
                        Tourist Attraction: %s,\n
                        location:%s,\n
                        Tour Date: %s,\n
                        Hotel Booked: %s Hotel \n
                        Hotel Location: %s \n
                        
                    """%(tour_person.tourguide.first_name,
                        tour_person.tourguide.last_name, 
                        tour_person.fullname,tour_person.email,
                        booked_hotel.phone,tour_person.gender,
                        tour_person.age,tour_person.people,
                        tour_person.days,tour_person.place.name,
                        tour_person.place.location,
                        tour_person.startdate.strftime('%D'),
                        booked_hotel.hotel.hotel_name,booked_hotel.hotel.hotel_location,
                        )
            ) 

        return redirect(url_for('bookedtours'))
    return render_template('admin/bookedtour.html',bookedrooms=bookedrooms, 
                            tours=tours, paymentinfo=paymentinfo)


@adminapp.route('/admin/purchased-package', methods=['GET', 'POST'])
def purchasedpackege():
    """admin route for listing packages that are purchased 
       and the payment status of the package"""

    packageid = request.args.get('id')
    purchasedpackege = MD.PurchasedPackage.select().where(MD.PurchasedPackage.package == packageid)
    paymentinfo = MD.PaymentList.select().where(MD.PaymentList.packagepayment > 0)
    if request.method == 'POST':
        MD.PurchasedPackage.makepaid(
            id=request.form['id']
        )
        # get information of person purchased the package
        package_person = MD.PurchasedPackage.select().where(MD.PurchasedPackage.id == request.form['id']).get()
        #send email notification to the tourist
        send_mail(
            receiver=package_person.email,
            message = """
                        Hello there %s You have completed buying a ticket for %s 
                        package. Your ticket number is %s be shure to be present 
                        at our office on specified date being(%s). We will be waiting for you
                        Thank You!
                    """%(package_person.fullname,
                            package_person.package.package_title,
                            package_person.id, 
                            package_person.package.tour_start.strftime('%D'))
            ) 

        return redirect(url_for('packages'))
    return render_template('admin/purchasedpackage.html',
                            purchasedpackege=purchasedpackege,
                            paymentinfo=paymentinfo)


@adminapp.route('/reportslist', methods=['GET', 'POST'])
def reportslist():
    images = MD.ImageList.select()
    tourist_report = MD.TouristReport.select()
    tourguide_report = MD.TourGuideReport.select()
    return render_template('admin/reportslist.html', 
                            tourist_report=tourist_report,
                            tourguide_report=tourguide_report,
                            images=images)

@adminapp.route('/admin/reports-from-tourgudes', methods=['GET', 'POST'])
def tourguidereport():
    images = MD.ImageList.select()
    tourist_report = MD.TouristReport.select()
    tourguide_report = MD.TourGuideReport.select()
    return render_template('admin/tourguidereports.html', 
                            tourist_report=tourist_report,
                            tourguide_report=tourguide_report,
                            images=images)


# comments list
@adminapp.route('/admin/comments', methods=['GET', 'POST'])
@login_required
def comments():
    """admin route for listing and updating status of the comments from customers."""

    comments = MD.Comment.select()
    if request.method == 'POST':
        MD.Comment.approve(
            value=request.form['approve'],
            comentid=request.form['commentid']
        )
    return render_template('admin/comments.html', comments=comments)


@adminapp.route("/admin/assets-manager", methods=['GET', 'POST'])
@login_required
def assetsmanager():
    """the admin route for managing the organization assets."""
    assets = MD.Asset.select()
    if request.method == 'POST':
        MD.Asset.create_asset(
            name=request.form['asset-name'],
            atype=request.form['asset-type'],
            av_at=request.form['available-at']
        )
        flash("Asset Registered", 'success')
        return redirect(url_for('assetsmanager'))
    return render_template("admin/settings.html", assets=assets)

# ###############USER ROUTE###########################
""" routes for the tourist. """
# ####################################################
# home page route
@adminapp.route('/')
def userhome():
    """index route for the tourist or the user homepage"""
    attraction = MD.Place.select()
    hotels = MD.Hotel.select().limit(4)
    imglist = MD.ImageList.select()
    return render_template('user/index.html',
                            atts=attraction, 
                            hotels=hotels,
                            imglist=imglist)

@adminapp.route('/user/show-hotels-list')
def morehotels():
    hotels = MD.Hotel.select().limit(4)
    imglist = MD.ImageList.select()
    return render_template('user/morehotels.html',
                            hotels=hotels,
                            imglist=imglist)


@adminapp.route('/user/tourist-attractions', methods=['GET', 'POST'])
def attraction():
    """user/customer route for viewing tourist destinations"""
    category = request.args.get('category')
    attraction = ''
    if category:
        attraction = MD.Place.select().where(MD.Place.category == category)
    else:
        attraction = MD.Place.select()
    imglist = MD.ImageList.select()

    return render_template('user/view_attractions.html',
                           attractions=attraction,
                           imagelist=imglist)


@adminapp.route('/select-tour', methods=['GET', 'POST'])
def selecttour():
    """user route for booking a tour."""
    places = MD.Place.select()
    tourguides = MD.TourGuide.select().limit(3)
    tourguideplace = MD.TourGuidePlace.select()
    imglist = MD.ImageList.select()
    tgskills = MD.TourGuideSkill.select()

    form = FormField.FBookingForm()
    form.destination.choices = [(destin.id, destin.name)
                                for destin in MD.Place.select()]
    form.tourguide.choices = [(tgs.id, tgs.first_name+" "+tgs.last_name)
                              for tgs in MD.TourGuide.select()]
    if request.method == 'POST':
        name = form.fname.data
        try:
            MD.TourInfo.create_tour(
                fname=form.fname.data,
                email=form.email.data,
                age=form.age.data,
                gender=form.gender.data,
                place=form.destination.data,
                people=form.people.data,
                days=form.days.data,
                startdate=form.startday.data,
                tourguide=form.tourguide.data
            )
        except Exception:
            flash("Internal Error please Try again later:",'danger')
            return redirect(url_for('selecttour'))

        send_mail(
            receiver=form.email.data,
            message="""
                    Hello There %s You Have Booked A Tour to %s Successfully!
                    Please Click the link below to make payments

                    http://%s:%s/makepayment/%s 

                    thank you !!
                    """%(form.fname.data,form.destination.data,HOST,PORT ,form.fname.data)
        )
        return redirect(url_for('makepayment', name=name))
    return render_template('user/select_tour.html', 
                    form=form, places=places, 
                    tourguides=tourguides,
                    tgplaces = tourguideplace,
                    imagelist=imglist,
                    tgskills=tgskills)


@adminapp.route('/get-tourguide/<place>')
def gettg(place):
    """return toure guide when the user/customer selects the tourist attractions."""
    t_guides = MD.TourGuidePlace.select().where(MD.TourGuidePlace.place == place)
    tg_array = []
    for tg in t_guides:
        tgObj = {}
        tgObj['id'] = tg.tourguide.id
        tgObj['name'] = tg.tourguide.first_name
        tgObj['lname'] = tg.tourguide.last_name
        tg_array.append(tgObj)
    return jsonify({'tourguides': tg_array})

@adminapp.route('/user/more-tourguides',methods=['GET','POST'])
def getmoretourguides():
    tourguides = MD.TourGuide.select()
    tgskills = MD.TourGuideSkill.select()
    tgplaces = MD.TourGuidePlace.select()
    return render_template('user/moretourguides.html',
                tourguides=tourguides,
                tgplaces=tgplaces,
                tgskills=tgskills)

@adminapp.route('/makepayment/<name>', methods=['GET', 'POST'])
def makepayment(name):
    """user route for selecting payment systems to make payment."""

    person = MD.TourInfo.select().where(MD.TourInfo.fullname == name).get()
    payments = MD.PaymentSystem.select().where(MD.PaymentSystem.hotel == 0)
    if request.method == 'POST':
        try:
            with MD.DB.transaction():
                MD.PaymentList.create(
                    tourpayment=person.id,
                    acount_name=request.form['acc-name'],
                    acount_number=request.form['acc-number'],
                    reason='Payment For Booking a tour',
                    price=person.days*person.place.price*person.people,
                    paymentoption=request.form['paymentoption']
                )
        except Exception as e:
            flash("Internal Error occured try again later", 'danger')
            return redirect(url_for('makepayment',name=name))
        single_pay_sys = MD.PaymentSystem.select().where(
                MD.PaymentSystem.id == request.form['paymentoption']).get()
        # send email notification
        send_mail(
            receiver=person.email,
            message="""\n
                    Hello There %s You submited your %s account Successfully!\n
                    This is our %s account/phone number [ %s ]. Use this to transfer\n
                    the money you have to pay for Booking a tour. the cost is ETB %s Birr.\n\n

                    thank you !!
                    """%(person.fullname, 
                        single_pay_sys.system_name,
                        single_pay_sys.system_name,
                        single_pay_sys.act_number,
                        person.days*person.place.price*person.people
                        )
                 )
        return redirect(url_for('gethotelslist', person=person.id))
    return render_template('user/tourpaymentoption.html', person=person, options='tour', payments=payments)


@adminapp.route('/get-hotels-list/<person>', methods=['GET', 'POST'])
def gethotelslist(person):
    """ user route that gets list of hotels for the tourist based
        on the places he/she booked a tour"""
    person = MD.TourInfo.select().where(MD.TourInfo.id == person).get()
    hotels = MD.Hotel.select().where(MD.Hotel.hotel_location == person.place.location)
    rooms = MD.Room.select()
    images = MD.ImageList.select()
    return render_template('user/hotels_list.html',
                           hotels=hotels, rooms=rooms,
                           person=person, images=images)


@adminapp.route('/book-hotel-room/', methods=['POST', 'GET'])
def bookrooms():
    """ user route displays lists of rooms that are for a selected hotel."""
    hotelid = request.args.get('id')
    personid = request.args.get('person')
    person=''
    hotel = ''
    rooms = ''
    if MD.TourInfo.select().where(MD.TourInfo.id == personid).exists():
        person = MD.TourInfo.get(MD.TourInfo.id == personid)
    if MD.Hotel.select().where(MD.Hotel.id == hotelid).exists():
        hotel = MD.Hotel.select().where(MD.Hotel.id == hotelid).get()
    if MD.Room.select().where(MD.Room.hotel == hotelid):
        rooms = MD.Room.select().where(MD.Room.hotel == hotelid)
    images = MD.ImageList.select()
    if request.method == 'POST':
        try:
            MD.BookedRoom.reserve_room(
                person=person.id,
                phone=request.form['phone'],
                days=request.form['days'],
                room=request.form['room'],
                reserved = request.form['reservednumber'],
                hotel=request.form['hotel']
            )
            rooms = MD.Room.get(MD.Room.id == request.form['room'])
            MD.Room.update(
                total_room = int(rooms.total_room)-int(request.form['reservednumber'])
            ).where(MD.Room.id == request.form['room']).execute()
        except Exception as e:
            print(e)
            flash("Internal Error Please try Again later:", 'danger')
            return redirect(url_for('bookrooms'))
        # send email notification to the tourist.
        send_mail(
            receiver=person.email,
            message="""\n
                    Hello There %s You Have Booked A Room Successfully!\n
                    Please Click the link below to make payments\n
                    http://%s:%s/makeroompayment/%s \n\n

                    Thank you!
                    """%(person.fullname,HOST,PORT, person.fullname)
        )
        return redirect(url_for('payfor_room', name=person.id))
    return render_template('user/bookhotelroom.html',
                           hotel=hotel, rooms=rooms, 
                           images=images, person=person)


@adminapp.route('/makeroompayment/<name>', methods=['GET', 'POST'])
def payfor_room(name):
    """user route for making room payment"""
    person = MD.BookedRoom.select().where(MD.BookedRoom.person == name).get()
    payments = MD.PaymentSystem.select().where(MD.PaymentSystem.hotel > 0)
    if request.method == 'POST':
        try:
            with MD.DB.transaction():
                MD.PaymentList.create(
                    acount_name=request.form['acc-name'],
                    acount_number=request.form['acc-number'],
                    reason='Payment For Room Resrvation',
                    price=person.days*person.room.price,
                    paymentoption=request.form['paymentoption'],
                    roomspayment=person.id,

                )
        except Exception:
            flash("Internal Error occured try again", 'danger')
            return redirect(url_for('payfor_room'))
        single_pay_sys = MD.PaymentSystem.select().where(
                        MD.PaymentSystem.id == request.form['paymentoption']).get()
        # send email notification
        send_mail(
            receiver=person.person.email,
            message="""\n
                    Hello There %s You submited your %s account Successfully!\n
                    This is our %s account/phone number [ %s ]. Use this to transfer\n
                    the money you have to pay for Booking a tour. the cost is ETB %s Birr.\n\n

                    thank you !!
                    """%(person.person.fullname, 
                        single_pay_sys.system_name,
                        single_pay_sys.system_name,
                        single_pay_sys.act_number,
                        person.days*person.room.price
                        )
                 )
        return redirect(url_for('selecttour'))
    return render_template('user/hotelpaymentoption.html', person=person, options='rooms', payments=payments)


@adminapp.route('/getpackages', methods=['GET', 'POST'])
def getPackages():
    """user route for listing all the tour packages available."""

    packages = MD.Package.select()
    if request.method == 'POST':
        name = request.form['fullname']
        try:
            MD.PurchasedPackage.purchase(
                fname=request.form['fullname'],
                email=request.form['email'],
                age=request.form['age'],
                gender=request.form['gender'],
                package=request.form['package'])
        except Exception:
            flash("Internal Error try again later:",'danger')
            return redirect(url_for('getpackages'))
        # send email notification to the perosn purchased the package.
        send_mail(
            receiver=request.form['email'],
            message="""\n
                    Hello There %s You Have Purchased a %s tour package Successfully!\n
                    Please Click the link below to make payments\n
                    http://%s:%s/make-package-payment/%s \n\n

                    thank you!
                    """%(request.form['fullname'], 
                        request.form['packagename'],
                        HOST,PORT,
                        request.form['fullname'])
        )
        return redirect(url_for('payfor_package', name=name))
    return render_template('user/packageslist.html', packages=packages)


@adminapp.route('/make-package-payment/<name>', methods=['GET', 'POST'])
def payfor_package(name):
    """user route for making package payments """

    person = MD.PurchasedPackage.select().where(
        MD.PurchasedPackage.fullname == name).get()
    payments = MD.PaymentSystem.select().where(MD.PaymentSystem.hotel == 0)
    if request.method == 'POST':
        try:
            with MD.DB.transaction():
                MD.PaymentList.create(
                    acount_name=request.form['acc-name'],
                    acount_number=request.form['acc-number'],
                    reason='Payment For Tour Package',
                    price=person.package.package_price,
                    paymentoption=request.form['paymentoption'],
                    packagepayment=person.id,

                )
        except Exception as e:
            flash("Internal Error occured try again", 'danger')
            print(e)
        
        single_pay_sys = MD.PaymentSystem.select().where(
                        MD.PaymentSystem.id == request.form['paymentoption']).get()
        # send email notification
        send_mail(
            receiver=person.email,
            message="""\n
                    Hello There %s You submited your %s account Successfully!\n
                    This is our %s account/phone number [ %s ]. Use this to transfer\n
                    the money you have to pay for Booking a tour. the cost is ETB %s Birr.\n\n

                    thank you !!
                    """%(person.fullname, 
                        single_pay_sys.system_name,
                        single_pay_sys.system_name,
                        single_pay_sys.act_number,
                        person.package.package_price
                        )
                 )
        return redirect(url_for('getPackages'))
    return render_template('user/tourpaymentoption.html', person=person, options='package', payments=payments)


@adminapp.route('/makereports', methods=['GET', 'POST'])
def makereports():
    if request.method == 'POST':
        try:
            MD.TouristReport.create_report(
                name=request.form['fullname'],
                email=request.form['email'],
                victim=request.form['victim'],
                victim_name=request.form['victimname'],
                report=request.form['content']
            )
        except MD.IntegrityError:
            flash('Already Sent', 'danger')

        # check if the post request has the file part
        if 'file' not in request.files:
            flash(' No image part but report saved', 'danger')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == ' ':
            flash(' No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            destin = os.path.join(adminapp.config['UPLOAD_FOLDER']+"/reports/",
                                  str(request.form['fullname'])+".jpg")
            file.save(destin)
        flash('You have sent a report successfully', 'success')
        return redirect(url_for('makereports'))

    return render_template('user/makereport.html')

@adminapp.route('/tourguide-makereports', methods=['GET', 'POST'])
def savetourguidereport():
    if request.method == 'POST':
        try:
            MD.TourGuideReport.create_report(
                reporter=request.form['fullname'],
                email=request.form['email'],
                category=request.form['category'],
                title=request.form['title'],
                report=request.form['content']
            )
        except MD.IntegrityError:
            flash('Already Sent', 'danger')

        # check if the post request has the file part
        if 'file' not in request.files:
            flash(' No image part but report saved', 'danger')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == ' ':
            flash(' No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            destin = os.path.join(adminapp.config['UPLOAD_FOLDER']+"/reports/",
                                  str(request.form['title'])+".jpg")
            file.save(destin)
        flash('You have sent a report successfully', 'success')
        return redirect(url_for('savetourguidereport'))

    return render_template('user/tourguidereportform.html')


@adminapp.route('/connect', methods=['GET', 'POST'])
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
            flash('Something Went Wrong try Again', 'danger')
            return redirect(url_for('connect'))
        flash('Thank You For Your Feedbacks', 'success')
        return redirect(url_for('connect'))
    return render_template('user/connect.html', comments=comments)

@adminapp.route('/about')
def about():
    return render_template('user/about.html')

# ######################################################
# Other util routes log in and logouts
#
@adminapp.errorhandler(404)
def not_found(error):
    return render_template('includes/404.html', user=admin_global), 404

# util routes
@adminapp.route('/delete/<id>/<db_urls>/<name>', methods=['GET', 'POST'])
@login_required
def delete(id, db_urls, name):
    """this route handles deleting package,hotels,palces 
        reports tourguides and their folders for uploading files"""
    try:
        if db_urls == 'Package':
            MD.Package.get(MD.Package.id == id).delete_instance()
            os.remove('static/images/packages/'+str(name)+'.jpg')
            flash("Package Deleted Successfully", "success")
            return redirect(url_for('packages'))
        elif db_urls == 'Hotel':
            MD.Hotel.get(MD.Hotel.id == id).delete_instance()
            os.rmdir('static/images/hotels/'+str(name))
            flash('Hotel deleted Successfully', 'success')
            return redirect(url_for('hotels'))
        elif db_urls == 'Place':
            MD.Place.get(MD.Place.id == id).delete_instance()
            for images in MD.ImageList.select().where(MD.ImageList.imagename == name):
                os.remove('static/images/places/'+str(name)+'/' +
                          str(name)+str(image.savetime)+'.jpg')
            os.rmdir('static/images/places'+str(name))
            flash('Place deleted Successfully', 'success')
            return redirect(url_for('places'))
        elif db_urls == 'Report':
            MD.Report.get(MD.Report.id == id).delete_instance()
            os.remove('static/images/reports/'+str(name)+'.jpg')
            flash('Report deleted Successfully', 'success')
            return redirect(url_for('reportslist'))
        elif db_urls == 'TourGuide':
            MD.TourGuide.get(MD.TourGuide.id == id).delete_instance()
            os.remove('static/images/tourguides/'+str(name)+'.jpg')
            flash('TourGuide deleted Successfully', 'success')
            return redirect(url_for('tourguides'))
    except Exception:
        flash("Error Deleting "+db_urls,"danger")
    return render_template('admin/index.html', user=admin_global)

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
    adminapp.run(debug=DEBUG, port=PORT, host=HOST)
