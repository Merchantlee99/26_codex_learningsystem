from __future__ import annotations

import json
import re
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .engine import domain_score_rows, repeated_wrong_rows, wrong_attempt_rows
from .paths import obsidian_cert_dir, obsidian_vault_dir


def safe_filename(value: str) -> str:
    normalized = []
    for char in value.strip().lower():
        if char.isalnum():
            normalized.append(char)
        elif char in {" ", "-", "_", "/", "."}:
            normalized.append("-")
    slug = re.sub(r"-+", "-", "".join(normalized)).strip("-")
    return slug or "note"


def write_obsidian_notes(conn: sqlite3.Connection, session_id: str) -> dict[str, Any]:
    session = get_finished_session(conn, session_id)
    exam_id = session["exam_id"]
    cert_dir = obsidian_cert_dir(exam_id)
    sessions_dir = cert_dir / "sessions"
    concepts_dir = cert_dir / "concepts"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    concepts_dir.mkdir(parents=True, exist_ok=True)

    session_note = sessions_dir / session_filename(session)
    session_note.write_text(render_session_note(conn, session_id), encoding="utf-8")

    concept_notes: list[Path] = []
    seen: set[str] = set()
    for row in wrong_attempt_rows(conn, session_id):
        concept = row["concept"]
        if concept in seen:
            continue
        seen.add(concept)
        concept_path = concepts_dir / f"{safe_filename(concept)}.md"
        concept_path.write_text(render_concept_note(conn, session, concept, session_note), encoding="utf-8")
        concept_notes.append(concept_path)

    review_queue = cert_dir / "review-queue.md"
    review_queue.write_text(render_review_queue(conn, exam_id), encoding="utf-8")

    return {
        "vault_root": str(obsidian_vault_dir()),
        "session_note": str(session_note),
        "concept_notes": [str(path) for path in concept_notes],
        "review_queue": str(review_queue),
    }


def get_finished_session(conn: sqlite3.Connection, session_id: str) -> sqlite3.Row:
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
    if session["finished_at"] is None:
        raise ValueError("finish the session before writing Obsidian notes")
    return session


def session_filename(session: sqlite3.Row) -> str:
    finished_on = session["finished_at"][:10]
    score = f"{float(session['score']):g}".replace(".", "-")
    exam = safe_filename(session["exam_id"])
    return f"{finished_on}_{exam}_{score}p_{safe_filename(session['id'])}.md"


def render_session_note(conn: sqlite3.Connection, session_id: str) -> str:
    session = get_finished_session(conn, session_id)
    total = conn.execute("SELECT COUNT(*) AS n FROM session_questions WHERE session_id = ?", (session_id,)).fetchone()["n"]
    wrongs = wrong_attempt_rows(conn, session_id)
    domain_rows = domain_score_rows(conn, session_id)
    repeated_rows = repeated_wrong_rows(conn, session["exam_id"])
    next_review = (date.today() + timedelta(days=3)).isoformat()
    weak_domains = [row["domain"] for row in domain_rows if row["correct"] < row["total"]]
    wrong_concepts = unique_values(row["concept"] for row in wrongs)

    lines = [
        "---",
        "type: study-session",
        f"exam: {session['exam_id']}",
        f"exam_name: {session['exam_name']}",
        f"session_id: {session_id}",
        f"date: {session['finished_at'][:10]}",
        f"score: {session['score']}",
        f"correct: {session['correct_count']}",
        f"total: {total}",
        f"pass_score: {session['pass_score']}",
        f"judgement: {session['pass_judgement']}",
        f"next_review: {next_review}",
        "weak_areas:",
        *yaml_list(weak_domains),
        "wrong_concepts:",
        *yaml_list(wrong_concepts),
        "---",
        "",
        f"# {session['exam_name']} 오답노트 - {session['finished_at'][:10]}",
        "",
        "## 결과",
        f"- 점수: {session['correct_count']}/{total} ({session['score']}점)",
        f"- 합격선: {session['pass_score']}점 이상",
        f"- 판정: {session['pass_judgement']}",
        f"- 다음 복습 예정: {next_review}",
    ]
    if total != session["official_question_count"]:
        lines.append("- 참고: 커스텀 문제 수 세트이므로 과락 판정은 정규 문항 수 모드에서만 정확합니다.")

    lines.extend(["", "## 취약 영역"])
    if weak_domains:
        for domain in weak_domains:
            lines.append(f"- {domain}")
    else:
        lines.append("- 이번 세션 기준 취약 영역 없음")

    lines.extend(["", "## 영역별 결과"])
    for row in domain_rows:
        lines.append(f"- {row['domain']}: {row['correct']}/{row['total']} ({row['score']}점)")

    lines.extend(["", "## 틀린 문제"])
    if not wrongs:
        lines.append("- 틀린 문제가 없습니다.")
    for row in wrongs:
        choices = json.loads(row["choices_json"])
        user_choice = choices[row["user_answer"] - 1]
        correct_choice = choices[row["correct_answer"] - 1]
        lines.extend(
            [
                "",
                f"### {row['position']}번. {row['concept']}",
                f"- 개념: {concept_link(session['exam_id'], row['concept'])}",
                f"- 영역: {row['domain']}",
                f"- 문제: {row['question_text']}",
                f"- 내 답: {row['user_answer']}번. {user_choice}",
                f"- 정답: {row['correct_answer']}번. {correct_choice}",
                f"- 해설: {row['explanation']}",
                f"- 내가 틀린 이유: {row['mistake_reason']}",
                f"- 다음 복습: {next_review}",
            ]
        )

    lines.extend(["", "## 반복 오답"])
    if not repeated_rows:
        lines.append("- 반복 오답 데이터가 아직 없습니다.")
    for row in repeated_rows:
        lines.append(f"- {concept_link(session['exam_id'], row['concept'])}: 누적 오답 {row['wrong_count']}회")

    lines.extend(["", "## 오늘 복습할 개념"])
    if not wrongs:
        lines.append("- 오늘 세션의 오답 기반 복습 개념은 없습니다.")
    for concept in wrong_concepts:
        concept_row = next(row for row in wrongs if row["concept"] == concept)
        lines.extend(["", f"### {concept}", concept_row["review_note"]])

    lines.extend(
        [
            "",
            "## 다음 액션",
            f"- {next_review}: 오늘 틀린 문제 재시험",
            "- 이후: 반복 오답 개념 중심으로 10문제 약점 세트 실행",
        ]
    )
    return "\n".join(lines) + "\n"


def render_concept_note(
    conn: sqlite3.Connection,
    session: sqlite3.Row,
    concept: str,
    latest_session_note: Path,
) -> str:
    row = conn.execute(
        """
        SELECT c.name, c.review_note, d.name AS domain
        FROM concepts c
        JOIN domains d ON d.id = c.domain_id
        WHERE c.exam_id = ? AND c.name = ?
        """,
        (session["exam_id"], concept),
    ).fetchone()
    history = conn.execute(
        """
        SELECT
          a.session_id,
          s.finished_at,
          sq.position,
          q.question_text,
          q.explanation,
          a.user_answer,
          a.correct_answer
        FROM attempts a
        JOIN sessions s ON s.id = a.session_id
        JOIN session_questions sq ON sq.session_id = a.session_id AND sq.question_id = a.question_id
        JOIN questions q ON q.id = a.question_id
        JOIN concepts c ON c.id = q.concept_id
        WHERE q.exam_id = ? AND c.name = ? AND a.is_correct = 0
        ORDER BY COALESCE(s.finished_at, s.started_at) DESC, sq.position ASC
        LIMIT 10
        """,
        (session["exam_id"], concept),
    ).fetchall()
    latest_link = session_link(session["exam_id"], latest_session_note)
    wrong_count = len(history)

    lines = [
        "---",
        "type: concept-review",
        f"exam: {session['exam_id']}",
        f"concept: {concept}",
        f"domain: {row['domain'] if row else ''}",
        f"wrong_count: {wrong_count}",
        f"latest_session: {session['id']}",
        "---",
        "",
        f"# {concept}",
        "",
        "## 핵심 정리",
        row["review_note"] if row else "개념 정리가 필요합니다.",
        "",
        "## 최근 연결 세션",
        f"- {latest_link}",
        "",
        "## 누적 오답",
    ]
    if not history:
        lines.append("- 아직 누적 오답이 없습니다.")
    for item in history:
        finished_on = item["finished_at"][:10] if item["finished_at"] else "unfinished"
        lines.extend(
            [
                f"- {finished_on} / {item['session_id']} / {item['position']}번",
                f"  - 문제: {item['question_text']}",
                f"  - 내 답: {item['user_answer']}번, 정답: {item['correct_answer']}번",
                f"  - 해설: {item['explanation']}",
            ]
        )
    return "\n".join(lines) + "\n"


def render_review_queue(conn: sqlite3.Connection, exam_id: str) -> str:
    rows = conn.execute(
        """
        SELECT
          rq.next_review_at,
          rq.review_stage,
          rq.last_result,
          c.name AS concept,
          d.name AS domain,
          q.id AS question_id
        FROM review_queue rq
        JOIN questions q ON q.id = rq.question_id
        JOIN concepts c ON c.id = rq.concept_id
        JOIN domains d ON d.id = c.domain_id
        WHERE q.exam_id = ?
        ORDER BY rq.next_review_at ASC, rq.review_stage DESC, c.name ASC
        """,
        (exam_id,),
    ).fetchall()
    lines = [
        "---",
        "type: review-queue",
        f"exam: {exam_id}",
        "---",
        "",
        f"# {exam_id} 복습 큐",
        "",
    ]
    if not rows:
        lines.append("- 예정된 복습이 없습니다.")
    for row in rows:
        lines.append(
            f"- {row['next_review_at']} / {concept_link(exam_id, row['concept'])} / "
            f"{row['domain']} / stage {row['review_stage']} / {row['last_result']} / {row['question_id']}"
        )
    return "\n".join(lines) + "\n"


def concept_link(exam_id: str, concept: str) -> str:
    return f"[[certifications/{exam_id.upper()}/concepts/{safe_filename(concept)}|{concept}]]"


def session_link(exam_id: str, session_note: Path) -> str:
    stem = session_note.stem
    return f"[[certifications/{exam_id.upper()}/sessions/{stem}|{stem}]]"


def unique_values(values) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def yaml_list(values: list[str]) -> list[str]:
    if not values:
        return ["  - none"]
    return [f"  - {value}" for value in values]
