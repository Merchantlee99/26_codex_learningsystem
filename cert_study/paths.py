from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    return Path(os.environ.get("CERT_STUDY_HOME", Path(__file__).resolve().parents[1]))


def data_dir() -> Path:
    path = project_root() / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return data_dir() / "study.sqlite"


def reports_dir() -> Path:
    path = project_root() / "reports" / "sessions"
    path.mkdir(parents=True, exist_ok=True)
    return path


def obsidian_vault_dir() -> Path:
    path = Path(os.environ.get("CERT_STUDY_OBSIDIAN_VAULT", project_root() / "obsidian_vault"))
    path.mkdir(parents=True, exist_ok=True)
    return path


def obsidian_cert_dir(exam_id: str) -> Path:
    path = obsidian_vault_dir() / "certifications" / exam_id.upper()
    path.mkdir(parents=True, exist_ok=True)
    return path
