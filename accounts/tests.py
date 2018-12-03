from django.test import TestCase as DjangoTestCase
from django.contrib.auth import get_user_model
import requests
from unittest import TestCase

User = get_user_model()


class TestLogin:

    @property
    def client(self):
        return requests.Session()

    @property
    def username(self):
        raise NotImplementedError()

    @property
    def password(self):
        raise NotImplementedError()

    @property
    def payload(self):
        return {
            'username': self.username,
            'password': self.password
        }

    expected_status_code = 200
    expected_return_payload = {}

    def setUp(self):
        url = ''
        self.response = self.client.post(
            url, json=self.payload
        )

    def test_should_return_exprected_status_code(self):
        self.assertEqual(
            self.response.status,
            self.expected_status_code
        )

    def test_should_return_exprected_payload(self):
        self.assertEqual(
            self.response.json(),
            self.expected_return_payload
        )


class TestSuccessfulLogin(TestLogin, TestCase):
    username = 'haki'
    password = 'correct-password'
    expected_status_code = 200
    expected_return_payload = {
        'id': 1,
        'username': 'Haki',
        'full_name': 'Haki Benita'
    }

    def test_should_update_last_login_date_in_user_model(self):
        user = User.objects.get(self.response.data['id'])
        self.assertIsNotNone(user.last_login_date)


class TestInvalidPassword(TestLogin, TestCase):
    username = 'Haki'
    password = 'wrong-password'