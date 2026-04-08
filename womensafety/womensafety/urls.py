from django.contrib import admin
from django.urls import path
from accounts import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Admin
    path('admin/', admin.site.urls),

    
path('home/', views.home, name='home'),
path('features/', views.features, name='features'),
path('contact/', views.contact, name='contact'),
    # Auth
    path('', views.register, name="register"),
    path('register/', views.register, name="register"),
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="logout"),

    

    # Map
    path('map/', views.safety_map, name="map"),

    # Features
    path('chatbot/', views.chatbot, name="chatbot"),
    path('sos/', views.sos_alert, name="sos"),

    # ✅ AUDIO UPLOAD (IMPORTANT)
    path('upload_audio/', views.upload_audio, name='upload_audio'),
    # live locations
    # LIVE TRACKING
path('live-location/', views.live_location),
path('track/<int:user_id>/', views.track_user),
path('get-location/<int:user_id>/', views.get_live_location),
]

# MEDIA FILES
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)