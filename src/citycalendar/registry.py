"""Dynamically instantiates a source class from config/sources.yaml."""
from __future__ import annotations

import importlib
from typing import Any


def load_source(module_name: str, class_name: str, source_id: str, params: dict[str, Any]):
    module = importlib.import_module(module_name)
    cls = getattr(module, class_name)
    return cls(source_id=source_id, **params)
