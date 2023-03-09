from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class InviteEmployee(models.Model):
    email = models.CharField(max_length=300, null=False, blank=False, primary_key=True)
    token = models.CharField(max_length=100,null=False, blank=True)
    county = models.CharField(max_length=100,null=False, blank=True)

    def __str__(self):
        return self.email

class Machinery(models.Model):
    model = models.CharField(max_length=100, null=False)
    vin = models.CharField(max_length=17, null=False, unique=True, primary_key=True)
    tank_capacity = models.FloatField(null=False)
    consumption = models.FloatField(null=False)
    county = models.CharField(max_length=50, null=False, default='temp')
    ready = models.BooleanField(default=False)
    driver_id1 = models.IntegerField(null=True)
    driver_id2 = models.IntegerField(null=True)

    def __str__(self):
        return self.model

class Schedule(models.Model):
    start_time=models.TimeField()
    end_time=models.TimeField()
    city = models.CharField(max_length=50, null=False, default='temp')

    def __str__(self):
        return self.start_time.__str__() + "-" + self.end_time.__str__()

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="driver")
    machinery = models.ForeignKey(to=Machinery, on_delete=models.CASCADE)
    schedule = models.ForeignKey(to=Schedule, on_delete=models.CASCADE, null=True)
    route = models.TextField(null=True)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

class VehiclesAddress(models.Model):
    county = models.CharField(max_length=50, null=False)
    latitude = models.FloatField(max_length=50, null=False)
    longitude = models.FloatField(max_length=50, null=False)

    def __str__(self):
        return self.county

class ConfigMode(models.Model):
    county = models.CharField(max_length=50, null=False)
    city = models.CharField(max_length=50, null=False)
    configArea = models.CharField(max_length=50, null=False)
    startApp = models.BooleanField(null=False, default=False)

    def __str__(self):
        return self.county
