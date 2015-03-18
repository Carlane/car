from django.db import models

# Create your models here.

# Types of customers in the system
class Type(models.Model):
    name = models.CharField(max_length = 15)
    descr = models.CharField(max_length = 15)
    is_active = models.BinaryField(default = True)
    
# Types of customer addresses in the system
class Address_Type(models.Model):
    name = models.CharField(max_length = 15)
    descr = models.CharField(max_length = 15)
    is_active = models.BinaryField(default = True)
    
# Personal profile of the customer
class Profile(models.Model):
    type = models.ForeignKey(Type)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    mobile_number = models.DecimalField(max_digits=20, decimal_places=0)
    email = models.EmailField(max_length = 50)
    
# Customer's addresses in the system
class Address(models.Model):
    address_type = models.ForeignKey(Address_Type)
    line1 = models.CharField(max_length = 50)
    line2 = models.CharField(max_length = 50)
    latitude = models.DecimalField(max_digits=8, decimal_places=3)
    longitude = models.DecimalField(max_digits=8, decimal_places=3)