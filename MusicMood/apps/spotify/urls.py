from django.urls import path
from .views import mood_spotify_widget

urlpatterns = [
    path("widget/<slug:mood_key>/", mood_spotify_widget, name="spotify_widget"),
]
