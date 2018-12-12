from django.test import TestCase as DjangoTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework import status
import requests
import json
from unittest import TestCase

User = get_user_model()
from products.models import Product


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


class BaseViewTest(APITestCase):
    client = APIClient()

    @staticmethod
    def create_product(title='', price=0):
        if title != "" and price > 0:
            Product.objects.create(title=title, price=price)

    def login_a_user(self, username='', password=''):
        url = reverse("api:auth-login", kwargs={"version": "v1"})
        return self.client.post(
            url,
            data=json.dumps({
                "username": username,
                "password": password
            }),
            content_type="aplication/json"
        )

    def setUp(self):
        self.user = User.objects.create_superuser(
            username="test_user",
            email="test@mail.com",
            password="testing",
            first_name="test",
            last_name="user",
        )

    def login_client(self, username="", password=""):
        response = self.client.post(
            reverse('create-token'),
            data=json.dumps({
                'username': username,
                'password': password
            }
            ),
            content_type='application/json'
        )
        self.token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client.login(username=username, password=password)
        return self.token


class AuthLoginUserTest(BaseViewTest):

    def test_login_user_with_valid_crdentials(self):
        response = self.login_a_user("test_user", "testing")
        self.assertIn("token", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.login_a_user("anonymus", "pass")


class AuthRegisterUserTest(BaseViewTest):

    def test_register_a_user_with_valid_data(self):
        url=reverse('auth-register', kwargs={"version": "v1"})
        response = self.client.post(
            url,
            data=json.dumps({
                "username": "new_user",
                "password": "new_pass",
                "email": "new_user@mail.com"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_a_user_with_invalid_data(self):
        url = reverse("auth-register", kwargs={"version": 'v1'})
        response = self.client.post(
            url,
            data=json.dumps({
                "username": "",
                'password': "",
                "email": ""
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)