from __future__ import annotations

import json
from typing import Any, Dict, List

import requests


class OllamaClient:
    def __init__(self, base_url: str, timeout_seconds: int) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def health_check(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def list_models(self) -> List[str]:
        response = requests.get(f"{self.base_url}/api/tags", timeout=self.timeout_seconds)
        response.raise_for_status()
        payload = response.json()
        models = payload.get("models", [])
        names = [model.get("name", "") for model in models if model.get("name")]
        return sorted(names)

    def pull_model(self, model_name: str) -> List[str]:
        events: List[str] = []
        response = requests.post(
            f"{self.base_url}/api/pull",
            json={"name": model_name, "stream": True},
            stream=True,
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()

        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                events.append(str(line))
                continue

            status = chunk.get("status")
            completed = chunk.get("completed")
            total = chunk.get("total")
            if status and completed is not None and total:
                events.append(f"{status} ({completed}/{total})")
            elif status:
                events.append(status)

        return events

    def generate_json(
        self,
        *,
        model: str,
        prompt: str,
        temperature: float,
        top_p: float,
        top_k: int,
        keep_alive: str,
    ) -> Dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "keep_alive": keep_alive,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "top_k": top_k,
                },
            },
            timeout=self.timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        raw_response = payload.get("response", "{}")
        return json.loads(raw_response)
