from django.contrib import admin
from .models import EmergencyContact, DangerLocation

admin.site.register(EmergencyContact)
admin.site.register(DangerLocation)