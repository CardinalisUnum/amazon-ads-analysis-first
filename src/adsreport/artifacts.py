"""Publish complete deterministic bundles without replacing different content."""

from collections.abc import Mapping
from pathlib import Path
from tempfile import TemporaryDirectory


def publish_bundle(destination: Path, files: Mapping[str, bytes]) -> Path:
    if destination.is_symlink():
        raise ValueError("Output must be a directory, not a symbolic link.")
    if destination.exists():
        if destination.is_dir() and {p.name for p in destination.iterdir()} == set(
            files
        ):
            if all(
                (destination / name).is_file()
                and (destination / name).read_bytes() == content
                for name, content in files.items()
            ):
                return destination
        raise FileExistsError(
            "Output already exists with different content. Choose a new --out path."
        )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=destination.parent, prefix="report-stage-") as staging:
        for name, content in files.items():
            (Path(staging) / name).write_bytes(content)
        Path(staging).rename(destination)
    return destination
