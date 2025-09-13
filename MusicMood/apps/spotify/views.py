from django.shortcuts import render
from .spotify_client import recs_by_mood

def mood_spotify_widget(request, mood_key: str):
    try:
        tracks = recs_by_mood(mood_key, limit=12)
        return render(request, "components/spotify_widget.html", {"tracks": tracks})
    except Exception as e:
        # Show the error in the widget so you can fix creds/seeds quickly
        return render(request, "components/spotify_widget.html", {"tracks": [], "error": str(e)})
