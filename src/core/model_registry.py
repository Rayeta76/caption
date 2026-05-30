"""Central registry for StockPrep vision models and processing modes."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "config" / "model_profiles.json"


@dataclass(frozen=True)
class ModelProfile:
    id: str
    label: str
    model_id: str
    manager: str
    status: str
    min_vram_gb: float
    description: str

    @property
    def selectable(self) -> bool:
        return self.manager == "qwen2_vl" and self.status in {"ready", "experimental"}

    @property
    def ui_label(self) -> str:
        suffix = "" if self.status == "ready" else f" ({self.status})"
        return f"{self.label}{suffix}"


@dataclass(frozen=True)
class ProcessingMode:
    id: str
    label: str
    detail_level: str
    verify_attributes: bool
    description: str
    prompt_suffix: str


def load_registry(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def get_model_profiles() -> list[ModelProfile]:
    data = load_registry()
    return [ModelProfile(**item) for item in data.get("models", [])]


def get_processing_modes() -> list[ProcessingMode]:
    data = load_registry()
    return [ProcessingMode(**item) for item in data.get("modes", [])]


def get_default_model_id() -> str:
    return str(load_registry().get("default_model") or "qwen2_vl_7b")


def get_default_mode_id() -> str:
    return str(load_registry().get("default_mode") or "stock_precise")


def find_model_profile(profile_id: str) -> ModelProfile:
    profiles = get_model_profiles()
    for profile in profiles:
        if profile.id == profile_id:
            return profile
    return profiles[0]


def find_processing_mode(mode_id: str) -> ProcessingMode:
    modes = get_processing_modes()
    for mode in modes:
        if mode.id == mode_id:
            return mode
    return modes[0]
