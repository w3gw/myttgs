import datetime
import os
import unittest
from peewee import *

from app import adminapp as  app

# test if admin created and gets admin and password hashed
# class AdminModelTest(unittest.TestCase):

#     @staticmethod
#     def create_admin(self):
#         self.admin = models.Admins.create_admin(
#                 fname="testadmin",
#                 lname="testadminlastname",
#                 email="testemail@gmail.com",
#                 phone="0912345494",
#                 address="testaddress",
#                 age="30",
#                 gender="male",
#                 password="testpassword"
#         )

#     def test_admin_creation(self):
#         self.create_admin(self)
#         self.assertEqual(models.Admins.select().count(),2)

#     def test_password_hashed(self):
#         self.create_admin(self)
#         self.assertNotEqual(models.Admins.select().get().password,'testpassword')

#     def test_get_admin(self):
#         self.create_admin(self)
#         self.assertEqual(models.Admins.get_admin('testemail@gmail.com').admin_fname ,'testadmin' )

class RoutesTest(unittest.TestCase):
    
    def test_mainpage(self):
        tester = app.test_client(self)
        response = tester.get('/admin/home',content_type='html/test')
        self.assertEqual(response.status_code,200)


if __name__ == '__main__':
    unittest.main()
