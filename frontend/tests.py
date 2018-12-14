from django.test import TestCase
from django.http import HttpResponse
from django.test import SimpleTestCase
from django.urls import reverse


class FrontPageTests(TestCase):

    def test_homepage_status_code(self):
        response = self.client.get('/')
        self.assertEquals(response.status_code, 200)

    def test_view_by_url_name(self):
        response = self.client.get(reverse('homepage'))
        self.assertEquals(response.status_code, 200)

    def test_view_use_correct_template(self):
        response = self.client.get(reverse('homepage'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_site/index.html')

    def test_homepage_contains_correct_html(self):
        response = self.client.get('/')
        self.assertContains(response, '<title>Amado - Furniture Ecommerce Template | Home</title>')
