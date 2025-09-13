import httpx
from django.conf import settings

class LLMClient:
    def __init__(self, provider: str, api_key: str, model: str):
        self.provider = provider
        self.api_key = api_key
        self.model = model

    async def chat(self, messages: list[dict]):
        if self.provider == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {"model": self.model, "messages": messages, "temperature": 0.5}
        else:
            raise NotImplementedError("Provider not configured")
        async with httpx.AsyncClient(timeout=60) as s:
            r = await s.post(url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"].strip()
