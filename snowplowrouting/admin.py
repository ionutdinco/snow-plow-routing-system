from django.contrib import admin
from .models import  InviteEmployee, Machinery, Driver, VehiclesAddress, Schedule, ConfigMode
from django_google_maps import widgets as map_widgets
from django_google_maps import fields as map_fields

# Register your models here.

admin.site.register(InviteEmployee)
admin.site.register(Machinery)
admin.site.register(Driver)
admin.site.register(VehiclesAddress)
admin.site.register(Schedule)
admin.site.register(ConfigMode)