from django.test import TestCase as DjangoTestCase
import requests
from unittest import TestCase


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