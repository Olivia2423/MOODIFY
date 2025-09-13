# apps/music/views.py
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Mood
from .serializers import TrackSerializer
from apps.spotify.spotify_client import recs_by_mood, search_tracks

def home(request):
    # Ensure the 5 Spotify-friendly moods always exist.
    canonical = [
        ("chill", "Chill"),
        ("focus", "Focus"),
        ("happy", "Happy"),
        ("party", "Party"),
        ("sad", "Melancholy"),
    ]
    existing = {m.key for m in Mood.objects.all()}
    for key, name in canonical:
        if key not in existing:
            Mood.objects.update_or_create(key=key, defaults={"name": name})

    moods = Mood.objects.all().order_by("name")
    return render(request, "home.html", {"moods": moods})

def htmx_recs(request, mood_key: str = None):
    selected_key = (mood_key or request.GET.get("mood") or "chill")
    q = (request.GET.get("q") or "").strip()
    previews_only = str(request.GET.get("previews")).lower() in {"1","true","on"}

    items = []
    error = None
    try:
        items = search_tracks(q, limit=12) if q else recs_by_mood(selected_key, limit=12)
    except Exception as e:
        error = str(e)

    if previews_only:
        items = [t for t in items if t.get("preview_url")]

    return render(request, "components/spotify_cards.html", {"tracks": items, "error": error})

@api_view(["GET"])
def api_recs(request):
    mood_key = request.GET.get("mood", "chill")
    q = request.GET.get("q")
    try:
        items = search_tracks(q, 12) if q else recs_by_mood(mood_key, 12)
    except Exception:
        items = []
    return Response(items)
