from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class DefaultBasicModel(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=150)
    timestamp = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    user_account = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    costum_ordering = models.IntegerField(default=1)

    class Meta:
        abstract = True