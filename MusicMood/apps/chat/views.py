from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpRequest
from django.conf import settings
from .llm import LLMClient
import json, asyncio

@csrf_exempt
def chat_api(request: HttpRequest):
    body = json.loads(request.body or "{}")
    user_msg = body.get("message", "")
    system = {"role": "system", "content": "You are a helpful music concierge that suggests tracks and merch."}
    user = {"role": "user", "content": user_msg}
    client = LLMClient(settings.LLM["PROVIDER"], settings.LLM["API_KEY"], settings.LLM["MODEL"])
    content = asyncio.run(client.chat([system, user]))
    return JsonResponse({"reply": content})
