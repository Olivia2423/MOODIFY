import numpy as np
from django.db.models import Q
from .models import Track, Mood

def cos(a, b):
    a, b = np.array(a), np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def recommend_by_mood(mood_key: str, limit: int = 20):
    mood = Mood.objects.filter(key=mood_key).first()
    if not mood:
        return Track.objects.none()
    qs = Track.objects.filter(Q(mood_tags=mood))[:limit]
    if qs.count() < limit:
        more = Track.objects.exclude(id__in=qs.values_list("id", flat=True)).order_by("-id")[: (limit - qs.count())]
        return list(qs) + list(more)
    return list(qs)

def rerank_with_embeddings(candidates, query_vec):
    scored = []
    for t in candidates:
        if t.vector:
            scored.append((cos(t.vector, query_vec), t))
        else:
            scored.append((0.0, t))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored]
