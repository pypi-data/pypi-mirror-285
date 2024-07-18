from django.db import models

# Create your models here.
class user_info(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    adress = models.TextField(max_length=100)
    is_status = models.BooleanField()
    is_lock = models.BooleanField()
    user_name = models.CharField(max_length=100)
    avatar = models.BinaryField()

class config(models.Model):
    is_open = models.BooleanField()
    is_check = models.BooleanField()
