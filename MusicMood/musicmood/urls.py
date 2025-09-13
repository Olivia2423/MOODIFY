from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.music.urls")),
    path("spotify/", include("apps.spotify.urls")),
    path("chat/", include("apps.chat.urls")),
]
