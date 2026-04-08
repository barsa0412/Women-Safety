from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail

from .models import EmergencyContact, SOSAlert, AudioRecord, LiveLocation, DangerLocation
from .models import EmergencyContact, SOSAlert, AudioRecord, LiveLocation
import json


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
            return redirect("/dashboard/")
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
# DASHBOARD
# =========================
@login_required
def dashboard(request):

    contacts = EmergencyContact.objects.filter(user=request.user)
    recordings = AudioRecord.objects.filter(user=request.user).order_by('-created_at')

    return render(request, "dashboard.html", {
        "contacts": contacts,
        "recordings": recordings
    })


# =========================
# ADD CONTACT
# =========================
@login_required
def add_contact(request):

    if request.method == "POST":

        name = request.POST.get("name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")

        EmergencyContact.objects.create(
            user=request.user,
            name=name,
            phone=phone,
            email=email
        )

        return redirect("/dashboard/")

    return render(request, "add_contact.html")


# =========================
# SAFETY MAP
# =========================
@login_required
def safety_map(request):
    return render(request, "map.html")


# =========================
# SOS ALERT (WITH AUDIO + EMAIL)
# =========================
@csrf_exempt
@login_required
def sos_alert(request):

    if request.method == "POST":

        data = json.loads(request.body)

        latitude = data.get("lat")
        longitude = data.get("lon")

        location_link = f"https://www.google.com/maps?q={latitude},{longitude}"

        # Get latest audio
        latest_audio = AudioRecord.objects.filter(user=request.user).last()

        audio_url = ""
        if latest_audio:
            audio_url = request.build_absolute_uri(latest_audio.audio.url)

        # Save SOS
        SOSAlert.objects.create(
            user=request.user,
            latitude=latitude,
            longitude=longitude,
            location_link=location_link
        )

        # =========================
        # SEND EMAIL TO CONTACTS
        # =========================
        contacts = EmergencyContact.objects.filter(user=request.user)
        emails = [c.email for c in contacts if c.email]

        if emails:
            send_mail(
                "🚨 Emergency Alert",
                f"I am in danger!\nMy location: {location_link}\nAudio: {audio_url}",
                settings.EMAIL_HOST_USER,
                emails,
                fail_silently=True
            )

        return JsonResponse({
            "status": "SOS Sent",
            "location": location_link,
            "audio": audio_url
        })

    return JsonResponse({"error": "Invalid request"})


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

    return redirect("/dashboard/")
# =========================
# SAVE LIVE LOCATION
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
# TRACK PAGE (FOR FRIEND)
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
# DANGER HEATMAP DATA (NEW)
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
            reply = "Always inform someone before traveling and keep emergency contacts ready."

        else:
            reply = "I am your safety assistant. Ask about danger, travel safety, SOS, or emergency help."

        return JsonResponse({"reply": reply})

    return JsonResponse({"error": "Invalid request"})