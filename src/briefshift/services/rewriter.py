from __future__ import annotations

from briefshift.core.prompts import build_rewrite_prompt
from briefshift.schemas.rewrite import RewriteResponse
from briefshift.services.ollama_client import OllamaClient


class RewriteService:
    def __init__(
        self,
        *,
        ollama_client: OllamaClient,
        temperature: float,
        top_p: float,
        top_k: int,
        keep_alive: str,
    ) -> None:
        self.ollama_client = ollama_client
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.keep_alive = keep_alive

    def rewrite(
        self,
        *,
        model: str,
        raw_message: str,
        audience: str,
        tone: str,
        length: str,
        include_subject: bool,
    ) -> RewriteResponse:
        prompt = build_rewrite_prompt(
            raw_message=raw_message,
            audience=audience,
            tone=tone,
            length=length,
            include_subject=include_subject,
        )
        structured = self.ollama_client.generate_json(
            model=model,
            prompt=prompt,
            temperature=self.temperature,
            top_p=self.top_p,
            top_k=self.top_k,
            keep_alive=self.keep_alive,
        )
        return RewriteResponse.model_validate(structured)
