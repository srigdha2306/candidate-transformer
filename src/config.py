from __future__ import annotations
import json
from pathlib import Path
from src.models import OutputConfig, MissingValueStrategy


def load_config(path: str | Path) -> OutputConfig:
    path = Path(path)
    if not path.exists():
        return OutputConfig()

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    fields = data.get("fields")
    field_rename = data.get("field_rename", {})
    include_confidence = data.get("include_confidence", True)
    missing_raw = data.get("missing_value", "null")

    try:
        missing = MissingValueStrategy(missing_raw)
    except ValueError:
        missing = MissingValueStrategy.NULL

    return OutputConfig(
        fields=fields,
        field_rename=field_rename,
        include_confidence=include_confidence,
        missing_value=missing,
    )
