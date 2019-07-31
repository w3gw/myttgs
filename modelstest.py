import datetime
import os
import unittest

from peewee import *
import models

class ModelTest(unittest.TestCase):

    # test if admin created correctly and password hashed
    def test_admin_password_hashed(self):
        models.Admins.create_admin(
                fname="Wogayehu",
                lname="Gezahegn",
                email="w3gwmak@gmail.com",
                phone="0923280982",
                address="addis ababa",
                age=24,
                gender='male',
                password='password'
        )
        self.password = models.Admins.get_admin('w3gwmak@gmail.com')
        self.assertNotEqual(self.password.password,'password')
    
    # test_if package created correctly and 
    def test_create_package(self):
        models.Package.create_package(
                title="Test Package",
                content="this package is for testing ",
                price=500,
                startdate=datetime.datetime.now(),
                tourdate=datetime.datetime.now(),
                days=10,
                num=200
        )
        self.package = models.Package.get(models.Package.package_title=='Test Package')
        self.assertLessEqual(self.package.posted_at,datetime.datetime.now())

    # test if create packagte raises Exception 
    def test_create_package_raiseExp(self):
        models.Package.create_package(
                title="Test Package",
                content="this package is for testing ",
                price=500,
                startdate=datetime.datetime.now(),
                tourdate=datetime.datetime.now(),
                days=10,
                num=200
        )
        self.assertRaises(IntegrityError)
        # self.assertRaisesRegex(ValueError,"Package Already Exists")

    # test if package is purchased correctly
    def test_purchasedpackage(self):
        self.package = models.Package.get(models.Package.package_title=='Test Package')
        models.PurchasedPackage.purchase(
                fname="test person",
                email="test@gmail.com",
                age=23,
                gender="male",
                package=1
        )
        self.purchased = models.PurchasedPackage.get(
            models.PurchasedPackage.fullname=='test person')
        self.assertEqual(self.purchased.package.package_title,'Test Package')

    # test if create_hotel works correctly
    def test_create_hotel(self):
        models.Hotel.create_hotel(
            name="Centeral",
            loc="jimma",
            email="centeral@gmail.com",
            phone= '0917234543',
            std="5 star",
            bio="this is the best hotel in jimma",
            code=12345
        )
        self.hotel = models.Hotel.get(models.Hotel.hotel_email=='centeral@gmail.com')
        self.assertLess(self.hotel.reg_at,datetime.datetime.now())
    
    # test if create_hotel raises exception
    def test_create_hotel_raisesError(self):
        models.Hotel.create_hotel(
            name="Centeral",
            loc="jimma",
            email="centeral@gmail.com",
            phone= '0917234543',
            std="5 star",
            bio="this is the best hotel in jimma",
            code=12345
        )
        self.assertRaises(IntegrityError)
    # test if manager is created correctly
    def test_create_manager(self):
        models.Manager.create_manager(
            fname="henok",
            lname="bahiru",
            email="henok@gmail.com",
            phone="0923280982",
            address="jimma",
            age=24,
            gender='male',
            hotel=1,
            password='password'
        )
        self.manager = models.Manager.get(models.Manager.first_name == 'henok')
        self.assertEqual(self.manager.hotel.hotel_name,'Centeral')
    
    # test if hotel room is created correctly
    def test_creaate_room(self):
        models.Room.create_room(
            beds=3,
            price=200,
            number=15,
            av_at=datetime.datetime.now(),
            hotel=1
        )
        self.room = models.Room.get(models.Room.beds == 3)
        self.assertEqual(self.room.hotel.hotel_name, 'Centeral')
    
    #test place model if creation works
    def test_create_place(self):
        models.Place.create_place(
            name="Testplace",
            loc="jimma",
            long="20",
            lat="30",
            dist=400,
            detail="test place description",
            category="Historical",
            price=500
        ) 
        self.place = models.Place.get(models.Place.name == "Testplace")
        self.assertLessEqual(self.place.reg_time,datetime.datetime.now())
    
    #test place model if creation raises Integrity Error
    def test_create_place_Error(self):
        models.Place.create_place(
            name="Testplace",
            loc="jimma",
            long="20",
            lat="30",
            dist=400,
            detail="test place description",
            category="Historical",
            price=500
        ) 
        self.assertRaises(IntegrityError)

    # test if tourguide creation works fine
    def test_create_tourguide(self):
        models.TourGuide.create_tg(
            fname="firstname",
            lname='lastname',
            email='email',
            phone='phone',
            address='address',
            age=30,
            gender='male',
            salary=5000
        )
        self.tguide = models.TourGuide.get(models.TourGuide.first_name == 'firstname')
        self.assertLessEqual(self.tguide.reg_time,datetime.datetime.now())

    # test the tourinfo model if tour is created
    def test_create_tour(self):
        models.TourInfo.create_tour(
                fname="fullname",
                email="booktour@gmail.com",
                age=30,
                gender="male",
                place=1,
                people=3,
                days=3,
                startdate=datetime.datetime.now(),
                tourguide=1
        )
        self.tour = models.TourInfo.get(models.TourInfo.fullname == 'fullname')
        self.assertLessEqual(self.tour.book_date,datetime.datetime.now())

    # test bookedroom model if booking works fine
    def test_book_room(self):
        models.BookedRoom.reserve_room(
            person=1,
            phone="0912345432",
            days=3,
            room=1,
            reserved = 2,
            hotel=1
        )
        self.room = models.BookedRoom.get(models.BookedRoom.phone=="0912345432")
        self.assertLessEqual(self.room.booked_at,datetime.datetime.now())

    # test bookedroom model if the right room is booked
    def test_book_room_correctly(self):
        models.BookedRoom.reserve_room(
            person=1,
            phone="0912345432",
            days=3,
            room=1,
            reserved = 2,
            hotel=1
        )
        self.room = models.BookedRoom.get(models.BookedRoom.phone=="0912345432")
        self.assertEqual(self.room.person.fullname,'fullname') 

if __name__ == "__main__":
    unittest.main()