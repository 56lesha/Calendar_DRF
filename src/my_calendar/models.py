from django.contrib.auth.models import User
from django.db import models

from django_countries.fields import CountryField


# Create your models here.
class Event(models.Model):

    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    finish_date = models.DateTimeField()
    CHOICES = (
        ('1', "1 hour"),
        ('2', "2 hour"),
        ('3', "4 hour"),
        ('4', "1 day"),
        ('5', "1 week"),)
    reminder = models.CharField(max_length=255, choices=CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = CountryField()




