from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from hydra import compose, initialize_config_dir
from omegaconf import DictConfig


@dataclass(slots=True)
class AppSettings:
    name: str
    tagline: str
    purpose: str
    default_model: str
    default_audience: str
    default_tone: str
    default_length: str
    max_input_chars: int
    request_timeout_seconds: int
    ollama_base_url: str
    temperature: float
    top_p: float
    top_k: int
    keep_alive: str
    audiences: List[str]
    tones: List[str]
    lengths: List[str]
    variation_modes: List[str]


def load_settings() -> AppSettings:
    config_dir = Path(__file__).resolve().parents[3] / "configs"
    with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
        cfg: DictConfig = compose(config_name="app")

    return AppSettings(
        name=cfg.app.name,
        tagline=cfg.app.tagline,
        purpose=cfg.app.purpose,
        default_model=cfg.app.default_model,
        default_audience=cfg.app.default_audience,
        default_tone=cfg.app.default_tone,
        default_length=cfg.app.default_length,
        max_input_chars=cfg.app.max_input_chars,
        request_timeout_seconds=cfg.app.request_timeout_seconds,
        ollama_base_url=cfg.app.ollama_base_url,
        temperature=float(cfg.app.temperature),
        top_p=float(cfg.app.top_p),
        top_k=int(cfg.app.top_k),
        keep_alive=cfg.app.keep_alive,
        audiences=list(cfg.options.audiences),
        tones=list(cfg.options.tones),
        lengths=list(cfg.options.lengths),
        variation_modes=list(cfg.options.variation_modes),
    )
