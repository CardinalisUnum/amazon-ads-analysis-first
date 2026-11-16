"""Read only explicitly allowed settings, without evaluating environment files."""

import os
from collections.abc import Iterable
from pathlib import Path


def read_environment(names: Iterable[str], path: Path = Path(".env")) -> dict[str, str]:
    allowed = set(names)
    values = {name: os.environ[name] for name in allowed if name in os.environ}
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            name, separator, value = line.partition("=")
            if separator and name.strip() in allowed:
                values.setdefault(name.strip(), value.strip().strip("\"'"))
    return values
