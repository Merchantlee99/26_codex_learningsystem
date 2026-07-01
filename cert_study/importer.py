from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


PUBLIC_SOURCE_TYPES = {"synthetic", "synthetic_recent_scope", "official_sample_link", "public_license"}
PRIVATE_SOURCE_TYPES = {"user_owned_summary", "personal_wrong_note", "restored_summary"}
FORBIDDEN_SOURCE_TYPES = {
    "actual_exam_dump",
    "credential_assessment_material",
    "commercial_book_verbatim",
    "web_scraped_verbatim",
}


def import_bank_file(conn: sqlite3.Connection, path: Path, *, private: bool = False) -> dict[str, int | str]:
    payload = load_payload(path)
    exam = require_dict(payload, "exam")
    domains = require_list(payload, "domains")
    concepts = require_list(payload, "concepts")
    questions = require_list(payload, "questions")

    exam_id = require_text(exam, "id")
    validate_question_sources(questions, private=private)

    conn.execute(
        """
        INSERT OR REPLACE INTO exams
        (id, name, official_question_count, official_duration_minutes, pass_score, domain_min_score, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            exam_id,
            require_text(exam, "name"),
            int(exam.get("official_question_count", len(questions))),
            int(exam.get("official_duration_minutes", 90)),
            float(exam.get("pass_score", 60.0)),
            float(exam.get("domain_min_score", 0.0)),
            str(exam.get("notes", "")),
        ),
    )

    conn.executemany(
        "INSERT OR REPLACE INTO domains (id, exam_id, name, official_weight, official_question_count) VALUES (?, ?, ?, ?, ?)",
        [
            (
                require_text(row, "id"),
                exam_id,
                require_text(row, "name"),
                float(row.get("official_weight", 0.0)),
                int(row.get("official_question_count", 0)),
            )
            for row in domains
        ],
    )
    conn.executemany(
        "INSERT OR REPLACE INTO concepts (id, exam_id, domain_id, name, review_note) VALUES (?, ?, ?, ?, ?)",
        [
            (
                require_text(row, "id"),
                exam_id,
                require_text(row, "domain_id"),
                require_text(row, "name"),
                require_text(row, "review_note"),
            )
            for row in concepts
        ],
    )
    conn.executemany(
        """
        INSERT OR REPLACE INTO questions
        (id, exam_id, domain_id, concept_id, question_text, choices_json, answer, explanation, difficulty, source_type, source_ref)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [normalize_question(row, exam_id) for row in questions],
    )
    conn.commit()
    return {"exam_id": exam_id, "domains": len(domains), "concepts": len(concepts), "questions": len(questions)}


def load_payload(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8")
    if suffix == ".json":
        payload = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ValueError("YAML import는 PyYAML이 설치되어 있어야 합니다. JSON importer는 기본 지원합니다.") from exc
        payload = yaml.safe_load(text)
    else:
        raise ValueError("지원하는 importer 확장자는 .json, .yaml, .yml 입니다.")
    if not isinstance(payload, dict):
        raise ValueError("문제은행 파일 최상위는 object여야 합니다.")
    return payload


def validate_question_sources(questions: list[Any], *, private: bool) -> None:
    for row in questions:
        if not isinstance(row, dict):
            raise ValueError("questions 항목은 object 목록이어야 합니다.")
        source_type = require_text(row, "source_type")
        if source_type in FORBIDDEN_SOURCE_TYPES:
            raise ValueError(f"가져올 수 없는 source_type입니다: {source_type}")
        if source_type in PRIVATE_SOURCE_TYPES and not private:
            raise ValueError(f"{source_type} 문제는 --private 옵션으로만 로컬 import할 수 있습니다.")
        if source_type not in PUBLIC_SOURCE_TYPES and source_type not in PRIVATE_SOURCE_TYPES:
            raise ValueError(f"알 수 없는 source_type입니다: {source_type}")


def normalize_question(row: dict[str, Any], exam_id: str) -> tuple[Any, ...]:
    choices = row.get("choices")
    if not isinstance(choices, list) or len(choices) != 4 or not all(isinstance(item, str) for item in choices):
        raise ValueError(f"{row.get('id', '<unknown>')} choices는 문자열 4개여야 합니다.")
    answer = int(row.get("answer", 0))
    if answer < 1 or answer > 4:
        raise ValueError(f"{row.get('id', '<unknown>')} answer는 1~4여야 합니다.")
    return (
        require_text(row, "id"),
        exam_id,
        require_text(row, "domain_id"),
        require_text(row, "concept_id"),
        require_text(row, "question_text"),
        json.dumps(choices, ensure_ascii=False),
        answer,
        require_text(row, "explanation"),
        str(row.get("difficulty", "medium")),
        require_text(row, "source_type"),
        require_text(row, "source_ref"),
    )


def require_dict(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key}는 object여야 합니다.")
    return value


def require_list(payload: dict[str, Any], key: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key}는 list여야 합니다.")
    return value


def require_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key}는 비어 있지 않은 문자열이어야 합니다.")
    return value

