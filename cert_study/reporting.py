from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .engine import domain_score_rows, repeated_wrong_rows, wrong_attempt_rows
from .obsidian import write_obsidian_notes
from .paths import reports_dir


def render_question(view) -> str:
    lines = [
        f"[{view.position}/{view.total}] {view.domain} / {view.concept}",
        "",
        view.question_text,
        "",
    ]
    for idx, choice in enumerate(view.choices, start=1):
        lines.append(f"{idx}. {choice}")
    lines.append("")
    if view.question_type == "multiple_response":
        lines.append("답변 형식: 정답 번호를 쉼표로 입력하세요. 예: 1,3")
    else:
        lines.append("답변 형식: 번호만 입력하세요. 예: 3")
    return "\n".join(lines)


def write_study_outputs(conn: sqlite3.Connection, session_id: str) -> dict[str, Any]:
    content = render_session_report(conn, session_id)
    path = reports_dir() / f"{session_id}.md"
    path.write_text(content, encoding="utf-8")
    obsidian = write_obsidian_notes(conn, session_id)
    return {"report_path": path, "obsidian": obsidian}


def write_session_report(conn: sqlite3.Connection, session_id: str) -> Path:
    return write_study_outputs(conn, session_id)["report_path"]


def render_session_report(conn: sqlite3.Connection, session_id: str) -> str:
    session = conn.execute(
        """
        SELECT s.*, e.name AS exam_name, e.pass_score, e.official_question_count
        FROM sessions s
        JOIN exams e ON e.id = s.exam_id
        WHERE s.id = ?
        """,
        (session_id,),
    ).fetchone()
    if session is None:
        raise ValueError(f"unknown session: {session_id}")
    total = conn.execute("SELECT COUNT(*) AS n FROM session_questions WHERE session_id = ?", (session_id,)).fetchone()["n"]
    correct = session["correct_count"]
    wrongs = wrong_attempt_rows(conn, session_id)
    domain_rows = domain_score_rows(conn, session_id)
    repeated_rows = repeated_wrong_rows(conn, session["exam_id"])
    next_review = (date.today() + timedelta(days=3)).isoformat()

    lines = [
        f"# {session['exam_name']} CBT 결과 - {session_id}",
        "",
        "## 점수",
        f"- 정답: {correct}/{total}",
        f"- 환산 점수: {session['score']}점",
        f"- 합격선: {session['pass_score']}점 이상",
        f"- 판정: {session['pass_judgement']}",
    ]
    if total != session["official_question_count"]:
        lines.append(
            f"- 참고: 커스텀 문제 수 세트이므로 과락 판정은 정규 {session['official_question_count']}문항 모드에서만 정확합니다."
        )
    lines.extend(["", "## 영역별 결과"])
    for row in domain_rows:
        lines.append(f"- {row['domain']}: {row['correct']}/{row['total']} ({row['score']}점)")

    lines.extend(["", "## 틀린 문제"])
    if not wrongs:
        lines.append("- 틀린 문제가 없습니다.")
    for row in wrongs:
        choices = json.loads(row["choices_json"])
        user_choices = answer_choices_from_json(row["user_answer_json"], fallback=row["user_answer"])
        correct_choices = answer_choices_from_json(row["correct_answer_json"], fallback=row["correct_answer"])
        lines.extend(
            [
                "",
                f"### {row['position']}번. {row['concept']}",
                f"- 문제: {row['question_text']}",
                f"- 내 답: {format_answer_choices(user_choices, choices)}",
                f"- 정답: {format_answer_choices(correct_choices, choices)}",
                f"- 영역: {row['domain']}",
                f"- 해설: {row['explanation']}",
                f"- 내가 틀린 이유: {row['mistake_reason']}",
                f"- 다음 복습: {next_review}",
            ]
        )

    lines.extend(["", "## 반복 오답"])
    if not repeated_rows:
        lines.append("- 반복 오답 데이터가 아직 없습니다.")
    for row in repeated_rows:
        lines.append(f"- {row['concept']}: 누적 오답 {row['wrong_count']}회")

    lines.extend(["", "## 오늘 복습할 개념"])
    seen: set[str] = set()
    if not wrongs:
        lines.append("- 오늘 세션의 오답 기반 복습 개념은 없습니다.")
    for row in wrongs:
        if row["concept"] in seen:
            continue
        seen.add(row["concept"])
        lines.extend(["", f"### {row['concept']}", row["review_note"]])

    lines.extend(
        [
            "",
            "## 다음 액션",
            f"- {next_review}: 오늘 틀린 문제 재시험",
            "- 이후: 반복 오답 개념 중심으로 10문제 약점 세트 실행",
        ]
    )
    return "\n".join(lines) + "\n"


def answer_choices_from_json(value: str, *, fallback: int) -> list[int]:
    try:
        payload = json.loads(value)
    except (TypeError, ValueError):
        payload = {}
    choices = payload.get("choices") if isinstance(payload, dict) else None
    if not isinstance(choices, list) or not choices:
        choices = [fallback]
    return sorted({int(choice) for choice in choices})


def format_answer_choices(answer_choices: list[int], choices: list[str]) -> str:
    label = ", ".join(str(choice) for choice in answer_choices) + "번"
    parts = []
    for choice in answer_choices:
        if 1 <= choice <= len(choices):
            parts.append(f"{choice}번. {choices[choice - 1]}")
        else:
            parts.append(f"{choice}번")
    if len(parts) == 1:
        return parts[0]
    return f"{label}. " + " / ".join(parts)
