# =========================
# IMPORTS
# =========================
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages

from .models import (
    EmergencyContact,
    SOSAlert,
    AudioRecord,
    LiveLocation,
    DangerLocation,
    CallRecording
)

import json
import requests

def safe_map(request):
    return render(request, 'safe_map.html')
# =========================
# HOME PAGE
# =========================
def home(request):
    return render(request, 'home.html')


# =========================
# REGISTER
# =========================
def register(request):

    if request.method == "POST":

        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {"error": "Username already exists"})

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect("/login/")

    return render(request, "register.html")


# =========================
# LOGIN
# =========================
def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/features/")
        else:
            return render(request, "login.html", {"error": "Invalid login credentials"})

    return render(request, "login.html")


# =========================
# LOGOUT
# =========================
def user_logout(request):
    logout(request)
    return redirect("/login/")


# =========================
# FEATURES PAGE (MAIN DASHBOARD)
# =========================
@login_required
def features(request):

    contacts = EmergencyContact.objects.filter(user=request.user)

    audio_recordings = AudioRecord.objects.filter(
        user=request.user
    ).order_by('-created_at')

    call_recordings = CallRecording.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, "features.html", {
        "contacts": contacts,
        "audio_recordings": audio_recordings,
        "call_recordings": call_recordings
    })


# =========================
# ADD CONTACT
# =========================
@login_required
def contact(request):

    if request.method == "POST":

        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        if EmergencyContact.objects.filter(phone=phone).exists() or EmergencyContact.objects.filter(email=email).exists():
            messages.error(request, "Contact already saved!")
        else:
            EmergencyContact.objects.create(
                user=request.user,
                name=name,
                phone=phone,
                email=email
            )
            messages.success(request, "Contact saved successfully!")

        return redirect('contact')

    return render(request, "contact.html")


# =========================
# SAFETY MAP
# =========================
@login_required
def safety_map(request):
    return render(request, "map.html")


# =========================
# SOS ALERT
# =========================
@csrf_exempt
@login_required
def send_sos(request):

    if request.method == "POST":

        data = json.loads(request.body)

        lat = data.get("lat")
        lon = data.get("lon")

        location_link = f"https://www.google.com/maps?q={lat},{lon}"
        message = f"🚨 EMERGENCY! I am in danger. My location: {location_link}"

        contacts = EmergencyContact.objects.filter(user=request.user)
        numbers = [c.phone for c in contacts]

        if numbers:
            send_sms(numbers, message)

        return JsonResponse({
            "status": "success",
            "numbers": numbers
        })

    return JsonResponse({"status": "failed"})


# =========================
# SEND SMS
# =========================
def send_sms(numbers, message):

    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = {
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "route": "q",
        "numbers": ",".join(numbers)
    }

    headers = {
        "authorization": "YOUR_API_KEY",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)


# =========================
# AUDIO UPLOAD
# =========================
@login_required
def upload_audio(request):

    if request.method == "POST":

        audio_file = request.FILES.get("audio")

        if audio_file:
            AudioRecord.objects.create(
                user=request.user,
                audio=audio_file
            )

    return redirect("/features/")


# =========================
# FAKE CALL PAGE
# =========================
@login_required
def fake_call_page(request):
    return render(request, "fake_call.html")


# =========================
# SAVE CALL RECORDING
# =========================
@login_required
def upload_call_recording(request):

    if request.method == "POST":

        audio = request.FILES.get("audio")

        if audio:
            CallRecording.objects.create(
                user=request.user,
                audio=audio
            )
            return JsonResponse({"status": "saved"})

    return JsonResponse({"status": "failed"})


# =========================
# LIVE LOCATION SAVE
# =========================
@csrf_exempt
@login_required
def live_location(request):

    if request.method == "POST":

        data = json.loads(request.body)

        LiveLocation.objects.update_or_create(
            user=request.user,
            defaults={
                "latitude": data.get("lat"),
                "longitude": data.get("lon")
            }
        )

        return JsonResponse({"status": "updated"})

    return JsonResponse({"error": "Invalid request"})


# =========================
# TRACK USER PAGE
# =========================
def track_user(request, user_id):
    return render(request, "track.html", {"user_id": user_id})


# =========================
# GET LIVE LOCATION
# =========================
def get_live_location(request, user_id):

    try:
        loc = LiveLocation.objects.get(user_id=user_id)

        return JsonResponse({
            "lat": loc.latitude,
            "lon": loc.longitude
        })

    except:
        return JsonResponse({"error": "No data"})


# =========================
# DANGER LOCATIONS
# =========================
@login_required
def danger_locations(request):

    data = [
        {"lat": d.latitude, "lon": d.longitude}
        for d in DangerLocation.objects.all()
    ]

    return JsonResponse({"points": data})


# =========================
# AI CHATBOT
# =========================
@csrf_exempt
@login_required
def chatbot(request):

    if request.method == "POST":

        data = json.loads(request.body)
        message = data.get("message", "").lower()

        if "help" in message:
            reply = "Stay calm. Press SOS and move to a safe place."

        elif "follow" in message or "stalker" in message:
            reply = "Go to a crowded area immediately and call someone you trust."

        elif "kidnap" in message:
            reply = "Create noise, drop belongings, and alert people nearby."

        elif "night" in message:
            reply = "Avoid dark roads. Share live location with trusted contacts."

        elif "police" in message:
            reply = "Dial 112 (India Emergency Helpline)."

        elif "unsafe" in message or "danger" in message:
            reply = "Trust your instincts. Leave the place immediately."

        elif "travel" in message:
            reply = "Always inform someone before traveling."

        else:
            reply = "I am your safety assistant."

        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Invalid request"})