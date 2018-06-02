from django.db import models
from django.contrib.auth.models import User
from tinymce.models import HTMLField


class CookiesModel(models.Model):
    title = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    text = HTMLField(blank=True)

    def __str__(self):
        return f'{self.title}'

class PolicyModel(models.Model):
    title = models.CharField(max_length=120)
    active = models.BooleanField(default=True)
    text = HTMLField(blank=True)

    def __str__(self):
        return f'{self.title}'