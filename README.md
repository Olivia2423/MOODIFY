# MusicMood 🎵
**AI-powered mood music discovery (Django + HTMX + Spotify + OpenAI)**

MusicMood recommends tracks based on your **mood** and optional **refine** text. It fetches live Spotify picks (with robust fallbacks), updates instantly with HTMX, plays audio previews, and includes an AI concierge that reads your current mood/refine context to suggest a crisp mini-mix.

---

## ✨ Features
- **Mood-based discovery**: Chill / Focus / Happy / Sad / Party (with smart aliasing).
- **Live Spotify picks**: Recommendations first; automatic fallback to playlists/track search.
- **Fast UX**: HTMX partial updates, responsive cards, sticky control panel, loader spinner.
- **Audio previews**: “Previews only” filter to show playable clips.
- **AI Concierge**: OpenAI-powered replies that use your selected mood and refine text.
- **Rock solid**: Token caching, safe error handling, and graceful UI fallbacks.

---

## 🧱 Tech Stack
**Backend:** Python, Django 5, Django REST Framework  
**Frontend:** HTMX, vanilla JS, CSS  
**APIs:** Spotify Web API (Client Credentials), OpenAI (Chat Completions)  
**Libs:** `httpx`, `python-dotenv`  
**DB:** SQLite (dev)  
**Dev:** VS Code, Git

---

## 🚀 Getting Started (Local Dev)

> **Prereqs:** Python 3.11+, pip, a Spotify app (Client ID/Secret), and an OpenAI API key (optional, for AI chat).

### 1) Create & activate a virtualenv (Windows/PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Configure environment
Copy the example and fill in secrets:
```powershell
Copy-Item .env.example .env
```

Edit `.env`:
```env
DJANGO_SECRET_KEY=change-this            # generate: python -c "import secrets;print(secrets.token_urlsafe(64))"
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=127.0.0.1,localhost

# Spotify (required for recommendations)
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# OpenAI (optional; enables AI Companion)
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

### 4) Migrate DB
```powershell
python manage.py migrate
```

> The app **auto-seeds** the 5 canonical moods on first load.  
> Manual seed (optional):
> ```powershell
> python manage.py shell -c "from apps.music.models import Mood; defaults=[('chill','Chill'),('happy','Happy'),('focus','Focus'),('sad','Melancholy'),('party','Party')]; [Mood.objects.update_or_create(key=k, defaults={'name': n}) for k,n in defaults]; print('Moods ready')"
> ```

### 5) Run
```powershell
python manage.py runserver
```
Open http://127.0.0.1:8000

- Change **Mood** → Spotify cards update.  
- Type in **Refine** (e.g., “lofi beats”) → switches to a Spotify track search.  
- Toggle **Previews only** → hides non-playable tracks.  
- Use **AI Companion** (if OpenAI key configured) → curated list based on your context.

---

## 🔌 Endpoints (dev)
- `GET /` — Homepage (HTMX-driven)
- `GET /_recs/?mood=<key>&q=<text>&previews=1` — Returns `spotify_cards.html` partial
- `GET /api/recs/?mood=<key>&q=<text>` — JSON list of tracks (simple API)
- `POST /chat/api/` — `{ message, mood, q, previews } → { reply }` (AI concierge)

---

## 🧠 How It Works (high level)
- **HTMX flow:** The mood/refine controls issue `hx-get` to `/_recs/`, which renders `templates/components/spotify_cards.html`.
- **Spotify client:**  
  1) `/v1/recommendations` with safe seed genres + audio targets  
  2) Fallback to **multiple playlist queries** (e.g., “deep focus”, “lofi chill”)  
  3) Final fallback to **track search**  
- **AI:** `/chat/api/` fetches current candidates (respecting mood/refine/previews), then asks OpenAI to curate a short, linked list.

---

## 🧪 Troubleshooting
- **Empty results for some moods:** The client auto-fallbacks to playlists/search; ensure `SPOTIFY_CLIENT_ID/SECRET` are correct.
- **Spotify 401/403:** Re-enter credentials; verify app in the Spotify Dashboard.
- **No audio controls:** Many tracks lack `preview_url`. Use **Previews only** to filter to playable tracks.
- **“Broken pipe” in dev server:** Harmless; happens when the browser aborts a request.
- **Static files warning:** Create `static/` or ignore in dev. For prod, run `collectstatic` and serve via Whitenoise/CDN.

---

## 📤 Deploy Notes (brief)
- Set `DEBUG=False`, a strong `DJANGO_SECRET_KEY`, and proper `ALLOWED_HOSTS`.
- Provide `SPOTIFY_CLIENT_ID/SECRET`, `LLM_API_KEY` as environment variables.
- Use a production WSGI/ASGI server (gunicorn/uvicorn) and serve static files (Whitenoise/CDN).
- Run: `python manage.py migrate` and `python manage.py collectstatic`.

---

## 🔮 Roadmap
- Save/favorite tracks + auth
- “Load more” / infinite scroll
- Export to Spotify playlist (OAuth)
- Shareable mood/refine links
- Light/dark theme toggle
- Keyboard shortcuts & mini player

---

## ✅ `.gitignore`
```gitignore
.env
.env.*
*.log
__pycache__/
*.pyc
db.sqlite3
/staticfiles/
/media/
/.venv/
/venv/
/node_modules/
.DS_Store
```

---

## 🙏 Credits
- **Spotify** for the Web API  
- **OpenAI** for the LLM APIs  
- **HTMX** for dynamic UX
