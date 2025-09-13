import base64, time, httpx
from django.conf import settings

# -------------------------
# Auth & helpers
# -------------------------
_TOKEN = {"value": None, "exp": 0}

def _get_token():
    now = time.time()
    if _TOKEN["value"] and now < _TOKEN["exp"] - 30:
        return _TOKEN["value"]

    cid = settings.SPOTIFY.get("CLIENT_ID", "")
    secret = settings.SPOTIFY.get("CLIENT_SECRET", "")
    if not cid or not secret:
        raise RuntimeError("Missing SPOTIFY_CLIENT_ID/SECRET in .env")

    auth = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}

    with httpx.Client(timeout=15) as s:
        r = s.post("https://accounts.spotify.com/api/token", data=data, headers=headers)
        r.raise_for_status()
        j = r.json()

    _TOKEN["value"] = j["access_token"]
    _TOKEN["exp"] = now + j["expires_in"]
    return _TOKEN["value"]

def _authed_get(session, url, params=None):
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = session.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

# -------------------------
# Mood config
# -------------------------
CANON_MOODS = {"happy", "sad", "chill", "focus", "party"}
MOOD_ALIAS = {
    "melancholy": "sad", "calm": "chill", "relax": "chill",
    "study": "focus", "work": "focus", "workout": "party",
    "energetic": "party", "energy": "party",
}
def normalize_mood(mood_key: str) -> str:
    k = (mood_key or "chill").strip().lower()
    k = MOOD_ALIAS.get(k, k)
    return k if k in CANON_MOODS else "chill"

# Safer seed sets (<=5) for /recommendations
MOOD_SEEDS = {
    "happy": ["pop", "dance", "edm"],
    "sad":   ["acoustic", "indie", "chill"],
    "chill": ["chill", "ambient", "acoustic"],
    "focus": ["ambient", "chill", "acoustic"],
    "party": ["dance", "edm", "house", "pop"],
}
MOOD_TARGETS = {
    "happy": {"target_valence": 0.9, "target_energy": 0.8, "target_danceability": 0.8},
    "sad":   {"target_valence": 0.2, "target_energy": 0.25},
    "chill": {"target_valence": 0.6, "target_energy": 0.3, "target_instrumentalness": 0.2},
    "focus": {"target_valence": 0.5, "target_energy": 0.25, "target_instrumentalness": 0.7},
    "party": {"target_valence": 0.8, "target_energy": 0.95, "target_danceability": 0.95},
}

# Multiple fallback playlist queries per mood (tried in order)
PLAYLIST_QS = {
    "happy": ["happy hits", "feel good", "good vibes"],
    "sad":   ["sad acoustic", "sad songs", "mellow songs"],
    "chill": ["lofi chill", "chill hits", "evening chill"],
    "focus": ["deep focus", "lofi beats", "instrumental study"],
    "party": ["dance party", "party hits", "dance hits"],
}

# -------------------------
# Public APIs
# -------------------------
def recs_by_mood(mood_key: str, limit: int = 12, market: str = "US"):
    """
    1) Try /recommendations (seed_genres + audio targets).
    2) If empty/error, try several playlist queries until we get tracks.
    3) If still empty, fall back to a broad track search for the mood.
    Always returns a list of normalized track dicts.
    """
    mood = normalize_mood(mood_key)
    seeds = MOOD_SEEDS[mood]

    # --- Try recommendations ---
    params = {
        "limit": limit,
        "market": market,
        "seed_genres": ",".join(seeds[:5]),
        **MOOD_TARGETS[mood],
    }
    try:
        with httpx.Client(timeout=20) as s:
            data = _authed_get(s, "https://api.spotify.com/v1/recommendations", params=params)
        items = [_normalize_track(tr) for tr in data.get("tracks", []) if tr]
        if items:
            return items
    except httpx.HTTPStatusError:
        # ignore and go to playlist fallback
        pass

    # --- Playlist fallbacks (multiple queries) ---
    pl_tracks = _fallback_from_playlists(mood, limit=limit, market=market)
    if pl_tracks:
        return pl_tracks

    # --- Last resort: broad track search ---
    return search_tracks(mood, limit=limit, market=market)

def search_tracks(query: str, limit: int = 12, market: str = "US"):
    q = (query or "").strip()
    if not q:
        return []
    with httpx.Client(timeout=20) as s:
        # NOTE: do NOT force market here; Spotify sometimes returns more results without it.
        data = _authed_get(
            s, "https://api.spotify.com/v1/search",
            params={"q": q, "type": "track", "limit": limit}
        )
    out = [_normalize_track(tr) for tr in (data.get("tracks") or {}).get("items", [])]
    return out

# -------------------------
# Internal fallbacks
# -------------------------
def _fallback_from_playlists(mood: str, limit: int = 12, market: str = "US"):
    # Try multiple queries in order, pick the first playlist that yields tracks
    with httpx.Client(timeout=20) as s:
        for q in PLAYLIST_QS.get(mood, [mood]):
            try:
                search = _authed_get(
                    s, "https://api.spotify.com/v1/search",
                    params={"q": q, "type": "playlist", "limit": 5}  # no market here
                )
            except httpx.HTTPStatusError:
                continue

            playlists = (search.get("playlists") or {}).get("items") or []
            for pl in playlists:
                pid = (pl or {}).get("id")
                if not pid:
                    continue
                try:
                    tracks = _authed_get(
                        s, f"https://api.spotify.com/v1/playlists/{pid}/tracks",
                        params={"limit": limit, "market": market}
                    )
                except httpx.HTTPStatusError:
                    continue

                out = []
                for it in tracks.get("items", []):
                    tr = (it or {}).get("track") or {}
                    if not tr or tr.get("is_local"):
                        continue
                    out.append(_normalize_track(tr))
                if out:
                    return out[:limit]
    return []

def _normalize_track(tr):
    return {
        "name": tr.get("name", ""),
        "artists": ", ".join(a.get("name","") for a in (tr.get("artists") or [])),
        "url": (tr.get("external_urls") or {}).get("spotify", ""),
        "preview_url": tr.get("preview_url") or "",
        "image": ((tr.get("album") or {}).get("images") or [{}])[0].get("url", ""),
        "explicit": tr.get("explicit", False),
    }
