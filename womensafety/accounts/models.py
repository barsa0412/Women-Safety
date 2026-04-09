from django.db import models
from django.contrib.auth.models import User




# -----------------------------
# Emergency Contacts
# -----------------------------
class EmergencyContact(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    phone = models.CharField(
        max_length=15,
        unique=True   # ✅ prevent duplicate phone
    )

    email = models.EmailField(
        unique=True   # ✅ prevent duplicate email
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# -----------------------------
# SOS Alerts (Location Sent)
# -----------------------------
class SOSAlert(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    latitude = models.FloatField()

    longitude = models.FloatField()

    location_link = models.URLField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"SOS Alert - {self.user.username}"
    

 ### FAKE CALL 

class CallRecording(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    audio = models.FileField(upload_to="call_recordings/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

# ===============================
# 🚨 DANGER LOCATION MODEL
# ===============================

class DangerLocation(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.description or "Danger Zone"


# -----------------------------
# Audio Evidence Recorder
# -----------------------------
class AudioRecord(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    audio = models.FileField(
        upload_to="recordings/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Recording - {self.user.username}"

# =========================
# LIVE TRACKING MODEL (UBER STYLE)
# =========================

class LiveLocation(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    latitude = models.FloatField()
    longitude = models.FloatField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Live Location"