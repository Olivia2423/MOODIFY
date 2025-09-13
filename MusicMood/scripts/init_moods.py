from apps.music.models import Mood
MOODS = [("chill","Chill"),("happy","Happy"),("focus","Focus"),("sad","Melancholy"),("party","Party")]
for k,n in MOODS:
    Mood.objects.get_or_create(key=k, defaults={"name": n})
print("Moods ready")
