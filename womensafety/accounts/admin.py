from django.contrib import admin
from .models import EmergencyContact
from .models import DangerLocation
admin.site.register(EmergencyContact)
admin.site.register(DangerLocation)