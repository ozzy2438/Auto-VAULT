"""Repository path helpers."""

from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    candidate = (start or Path.cwd()).resolve()
    for path in (candidate, *candidate.parents):
        if (path / ".git").exists() or (path / "pyproject.toml").exists():
            return path
    return candidate


def data_dir(start: Path | None = None) -> Path:
    return find_repo_root(start) / "data"


def sources_dir(start: Path | None = None) -> Path:
    return data_dir(start) / "sources"


def curated_dir(start: Path | None = None) -> Path:
    return data_dir(start) / "curated"
