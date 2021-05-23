import unittest
import json
from app.test.base import BaseTestCase


def register_user(self):
    return self.client.post(
        '/user/',
        data=json.dumps(dict(
            email='example@gmail.com',
            username='username',
            password='123456'
        )),
        content_type='application/json'
    )


def login_user(self):
    return self.client.post(
        '/auth/login',
        data=json.dumps(dict(
            username='username',
            password='123456'
        )),
        content_type='application/json'
    )


class TestAuthBlueprint(BaseTestCase):

    def test_registered_user_login(self):
            """ Test for login of registered-user login """
            with self.client:
                # register the user
                registration_response = register_user(self)
                reg_json = registration_response.json
                self.assertEqual(registration_response.status_code, 201)
                self.assertTrue(reg_json['Authorization'])

                # registered user login
                login_response = login_user(self)
                login_json = login_response.json
                self.assertEqual(login_response.status_code, 200)
                self.assertTrue(login_json['Authorization'])

    def test_valid_logout(self):
        """ Test for logout before token expires """
        with self.client:
            # user registration
            registration_response = register_user(self)
            reg_json = registration_response.json
            self.assertTrue(reg_json['Authorization'])
            self.assertEqual(registration_response.status_code, 201)

            # registered user login
            login_response = login_user(self)
            login_json = login_response.json
            self.assertTrue(login_json['Authorization'])
            self.assertEqual(login_response.status_code, 200)

            # valid token logout
            logout_response = self.client.post(
                '/auth/logout',
                headers=dict(
                    Authorization='Bearer ' + login_response.json['Authorization']
                )
            )
            logout_json = logout_response.json
            self.assertTrue(logout_json['status'] == 'success')
            self.assertEqual(logout_response.status_code, 200)


if __name__ == '__main__':
    unittest.main()