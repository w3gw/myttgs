import datetime
import os
import unittest

from peewee import *

from app import adminapp as app

# test admin routes
class AppTest(unittest.TestCase):

    def setUp(self):
        self.tester = app.test_client(self)
    
    # test if flask was set up correctly
    def test_main(self):
        response = self.tester.get('/',content_type='html/test')
        self.assertEqual(response.status_code,200)
    
    # test if mainpage loads correctly
    def test_mainpage_loads(self):
        response = self.tester.get('/admin/home',content_type='html/test')
        self.assertTrue(b'WELCOME TO TOUR' in response.data)
    # test if login page loads correctly
    def test_login_page(self):
        response = self.tester.get('/admin/login',content_type='html/test')
        self.assertEqual(response.status_code,200)
    # test if registration page loads correctly
    def test_registration_page(self):
        response = self.tester.get('/admin/signup',content_type='html/test')
        self.assertEqual(response.status_code,200)
    # test if admin registration works correctly
    def test_admin_registration(self):
        response = self.tester.post(
            "/admin/signup",
            data=dict(
                fname="Wogayehu",
                lname="Gezahegn",
                email="w3gwmak@gmail.com",
                phone="0923280982",
                address="addis ababa",
                age=24,
                gender='male',
                password='password'   
            ),follow_redirects=True
        )
        self.assertTrue(b'You Are Registered You Can login' in response.data)

    # test if admin registration works correctly
    def test_admin_login(self):
        response = self.tester.post(
            "/admin/login",
            data=dict(
                email='w3gwmak@gmail.com',
                password='password'   
            ),follow_redirects=True
        )
        self.assertEqual(response.status_code,200)
    
    #test if admin logout works correctly
    def test_admin_logout(self):
        response = self.tester.post(
            "/admin/login",
            data=dict(
                email='w3gwmak@gmail.com',
                password='password'   
            ),follow_redirects=True)
        response = self.tester.get('/logout',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code,200)
    
    #test if admin index page responses correctly
    def test_admin_indexpage(self):
        response = self.tester.get('/admin/index',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code,200)
    
    # test if adding payment system does not work correctly
    def test_admin_add_paymentsystem(self):
        response = self.tester.post(
            '/admin/index',
            data=dict(
                system_name = "CBE-Birr",
                act_name = "TTGS-CBE",
                act_number = "0923912334",
                links = "we like cbe birr"
            ),follow_redirects=True
        )
        self.assertRaisesRegex(ValueError,'Internal Error try again later:')
    # test if admin package route works correctly
    def test_if_admin_package(self):
        response = self.tester.get('/admin/packages',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    # test if admin package route responds correct data
    def test_if_admin_package_response(self):
        response = self.tester.get('/admin/packages',content_type='html/text',follow_redirects=True)
        self.assertTrue(b'All packages',response.data)

    # test if adding packages route works correcty
    def test_admin_add_package_route(self):
        response = self.tester.get('/admin/add_new_packages',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    # test if adding new packages work correctly
    def test_admin_add_new_packages(self):
        response = self.tester.post(
            '/admin/add_new_packages',
            data=dict(
                title="Test Package",
                content="this package is for testing ",
                price=500,
                startdate=datetime.datetime.now(),
                tourdate=datetime.datetime.now(),
                days=10,
                num=200,
            ),follow_redirects=True
        ) 
        self.assertEqual(response.status_code,200)
    # test if hotels list route works fine
    def test_hotels_route(self):
        response = self.tester.get('/admin/hotel',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code,200)
    # test add new hotel route
    def test_add_new_hotels(self):
        response = self.tester.post(
            '/admin/add_new_hotel',
            data=dict(
                name="Centeral",
                loc="jimma",
                email="centeral@gmail.com",
                phone= '0917234543',
                std="5 star",
                bio="this is the best hotel in jimma",
                code=12345
            ),follow_redirects=True
        )
        self.assertEqual(response.status_code,200)
    # test if tourguides route works correctly
    def test_admin_tourguides_route(self):
        response = self.tester.get('/admin/tourguides',content_type='html/text',
                    follow_redirects=True)
        self.assertEqual(response.status_code,200)
    # test if admin addtourguides route works correctly
    def test_admin_addtourguides(self):
        response = self.tester.post(
            '/admin/add_new_tourguide',
            data=dict(
                fname="firstname",
                lname='lastname',
                email='email',
                phone='phone',
                address='address',
                age=30,
                gender='male',
                salary=5000
            ),follow_redirects=True,
        )
        self.assert_(response.status_code==200)

    # test if admin update tourguides route works correctly
    def test_admin_addtourguides(self):
        response = self.tester.post(
            '/admin/tourguides',
            data=dict(
                fname="firstname",
                lname='lastname',
                email='email',
                phone='phone',
                address='address',
                age=30,
                salary=5000,
                id=1
            ),follow_redirects=True,
        )
        self.assertEqual(response.status_code,200) 
    # test if admin places route works fine
    def test_admin_places_route(self):
        response = self.tester.get('/admin/place',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code,200)

    # test if admin add new places route works
    def test_admin_addnew_places(self):
        response = self.tester.post(
            '/admin/add_new_place',
            data=dict(
                name="Testplace",
                loc="jimma",
                long="20",
                lat="30",
                dist=400,
                detail="test place description",
                category="Historical",
                price=500
            ),follow_redirects=True
        )
        self.assertEqual(response.status_code,200)
    # test if booked tour route returns the right response
    def test_admin_bookedtour(self):
        response = self.tester.get('/admin/tours',content_type='html/text',follow_redirects=True)
        self.assertEqual(response.status_code,200)

if __name__ == '__main__':
    unittest.main()
