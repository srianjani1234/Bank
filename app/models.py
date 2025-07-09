from django.db import models

# Create your models here.
class Account(models.Model):
    name = models.CharField(max_length=32)
    acc_num = models.BigAutoField(primary_key=True,unique=True,default=12345678912)
    phone = models.PositiveIntegerField(unique=True)
    email = models.EmailField()
    address = models.TextField()
    pin = models.CharField(default=0,max_length=4)
    balance = models.DecimalField(max_digits=10, decimal_places=2 , default=1000)


