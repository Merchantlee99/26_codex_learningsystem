from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_REPOSITORY = "https://github.com/ChathurangaVKD/AWS-Certified-Solutions-Architect-Associate-SAA-C03"
EXAM_ID = "AWS_SOLUTIONS_ARCHITECT_ASSOCIATE"


@dataclass(frozen=True)
class Domain:
    id: str
    name: str
    weight: float
    official_question_count: int


DOMAINS = (
    Domain("AWS-SAA-D1", "Design Secure Architectures", 30.0, 20),
    Domain("AWS-SAA-D2", "Design Resilient Architectures", 26.0, 17),
    Domain("AWS-SAA-D3", "Design High-Performing Architectures", 24.0, 16),
    Domain("AWS-SAA-D4", "Design Cost-Optimized Architectures", 20.0, 12),
)

DOMAIN_BY_ID = {domain.id: domain for domain in DOMAINS}

PATH_DOMAIN_HINTS = {
    "02-IAM": "AWS-SAA-D1",
    "07-Security": "AWS-SAA-D1",
    "03-Compute": "AWS-SAA-D3",
    "04-Storage": "AWS-SAA-D3",
    "05-Database": "AWS-SAA-D3",
    "06-Networking": "AWS-SAA-D3",
    "08-Application-Integration": "AWS-SAA-D2",
    "09-Monitoring": "AWS-SAA-D2",
    "10-Migration": "AWS-SAA-D2",
    "11-Analytics": "AWS-SAA-D3",
    "12-Architecture-Patterns": "AWS-SAA-D2",
    "13-Cost-Optimization": "AWS-SAA-D4",
}

KEYWORD_DOMAIN_HINTS = (
    ("AWS-SAA-D4", ("cost", "pricing", "savings plan", "reserved", "spot", "budget", "rightsize", "trusted advisor")),
    ("AWS-SAA-D1", ("security", "iam", "kms", "encrypt", "waf", "shield", "guardduty", "macie", "secret", "cognito", "policy")),
    ("AWS-SAA-D2", ("availability", "failover", "multi-az", "disaster", "rto", "rpo", "resilien", "sqs", "sns", "decoupl", "auto scaling")),
    ("AWS-SAA-D3", ("performance", "latency", "throughput", "cache", "cloudfront", "elasticache", "read replica", "kinesis", "athena")),
)


def convert_chathuranga_saa_markdown(
    source: Path,
    output: Path,
    *,
    mark_active: bool = False,
    checked_at: str = "",
    source_ref: str = SOURCE_REPOSITORY,
) -> dict[str, Any]:
    payload, report = build_chathuranga_saa_payload(
        source,
        mark_active=mark_active,
        checked_at=checked_at,
        source_ref=source_ref,
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report["output"] = str(output)
    return report


def build_chathuranga_saa_payload(
    source: Path,
    *,
    mark_active: bool = False,
    checked_at: str = "",
    source_ref: str = SOURCE_REPOSITORY,
) -> tuple[dict[str, Any], dict[str, Any]]:
    questions: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    files = markdown_sources(source)
    for path in files:
        parsed = parse_markdown_file(path, source_root=source if source.is_dir() else source.parent)
        for question in parsed["questions"]:
            questions.append(
                question_payload(
                    question,
                    source_ref=source_ref,
                    mark_active=mark_active,
                    checked_at=checked_at,
                )
            )
        skipped.extend(parsed["skipped"])

    payload = {
        "exam": {
            "id": EXAM_ID,
            "name": "AWS Certified Solutions Architect Associate",
            "official_question_count": 65,
            "official_duration_minutes": 130,
            "pass_score": 72,
            "domain_min_score": 0,
            "notes": "MIT 라이선스 SAA-C03 커뮤니티 연습문항 변환본입니다. 실제 시험 대비 전 AWS 공식 시험 가이드와 함께 검토합니다.",
        },
        "domains": [
            {
                "id": domain.id,
                "name": domain.name,
                "official_weight": domain.weight,
                "official_question_count": domain.official_question_count,
            }
            for domain in DOMAINS
        ],
        "concepts": [
            {
                "id": concept_id_for_domain(domain.id),
                "domain_id": domain.id,
                "name": f"{domain.name} community practice",
                "review_note": f"{domain.name} 영역의 SAA-C03 커뮤니티 연습문항 오답을 공식 가이드와 함께 복습한다.",
            }
            for domain in DOMAINS
        ],
        "questions": questions,
    }
    return payload, {"source": str(source), "files": len(files), "converted_questions": len(questions), "skipped": skipped}


def inspect_chathuranga_saa_markdown(source: Path) -> dict[str, Any]:
    files = markdown_sources(source)
    items = []
    for path in files:
        parsed = parse_markdown_file(path, source_root=source if source.is_dir() else source.parent)
        items.append(
            {
                "path": str(path),
                "questions": len(parsed["questions"]),
                "skipped": len(parsed["skipped"]),
            }
        )
    return {
        "source": str(source),
        "files": len(files),
        "convertible_questions": sum(row["questions"] for row in items),
        "skipped": sum(row["skipped"] for row in items),
        "items": items,
    }


def markdown_sources(source: Path) -> list[Path]:
    if not source.exists():
        raise ValueError(f"경로가 없습니다: {source}")
    if source.is_file():
        if source.suffix.lower() != ".md":
            raise ValueError(f"Markdown 파일만 변환할 수 있습니다: {source}")
        return [source]
    candidates = []
    for path in sorted(source.rglob("*.md")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if "### Question" in text and ("**Answer:" in text or "Correct Answer" in text or "✓" in text):
            candidates.append(path)
    return candidates


def parse_markdown_file(path: Path, *, source_root: Path) -> dict[str, Any]:
    relative_path = str(path.relative_to(source_root)) if path.is_relative_to(source_root) else str(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    chunks = question_chunks(text)
    questions = []
    skipped = []
    for index, chunk in enumerate(chunks, start=1):
        parsed = parse_question_chunk(chunk)
        if parsed is None:
            skipped.append({"path": relative_path, "position": index, "reason": "single-choice 문항으로 파싱되지 않음"})
            continue
        parsed["path"] = relative_path
        parsed["position"] = index
        parsed["domain_id"] = infer_domain_id(relative_path, parsed)
        questions.append(parsed)
    return {"questions": questions, "skipped": skipped}


def question_chunks(text: str) -> list[str]:
    matches = list(re.finditer(r"(?m)^### Question\b.*$", text))
    chunks = []
    for idx, match in enumerate(matches):
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        chunks.append(text[match.start() : end].strip())
    return chunks


def parse_question_chunk(chunk: str) -> dict[str, Any] | None:
    heading_match = re.match(r"(?m)^### Question\s+\d+(?::\s*(.*))?", chunk)
    if heading_match is None:
        return None
    option_matches = list(re.finditer(r"(?m)^\s*(?:\*\*)?([A-D])(?:\.\*\*|\.)\s+(.+?)\s*$", chunk))
    if len(option_matches) != 4:
        return None

    answer_letter = answer_from_options(chunk, option_matches) or answer_from_details(chunk)
    if answer_letter is None:
        return None

    prompt_start = heading_match.end()
    prompt_end = option_matches[0].start()
    prompt = clean_markdown(chunk[prompt_start:prompt_end])
    if heading_match.group(1):
        prompt = clean_markdown(f"{heading_match.group(1)}\n{prompt}")
    prompt = re.sub(r"\bOptions:\s*", "", prompt, flags=re.I).strip()

    choices = []
    for idx, match in enumerate(option_matches):
        start = match.start(2)
        end = option_matches[idx + 1].start() if idx + 1 < len(option_matches) else option_block_end(chunk, match.end())
        option_text = chunk[start:end]
        option_text = re.sub(r"\s*✓\s*$", "", option_text.strip())
        choices.append(clean_markdown(option_text))

    if not prompt or any(not choice for choice in choices) or len(set(choices)) != 4:
        return None

    answer = "ABCD".index(answer_letter) + 1
    return {
        "question_text": prompt,
        "choices": choices,
        "answer": answer,
        "explanation": explanation_from_chunk(chunk),
    }


def option_block_end(chunk: str, start: int) -> int:
    details = chunk.find("<details>", start)
    explanation = chunk.find("**Explanation", start)
    separator = chunk.find("\n---", start)
    candidates = [idx for idx in (details, explanation, separator) if idx != -1]
    return min(candidates) if candidates else len(chunk)


def answer_from_options(chunk: str, option_matches: list[re.Match[str]]) -> str | None:
    marked = [match.group(1) for match in option_matches if "✓" in chunk[match.start() : option_block_end(chunk, match.end())]]
    return marked[0] if len(marked) == 1 else None


def answer_from_details(chunk: str) -> str | None:
    match = re.search(r"\*\*(?:Correct\s+Answer|Answer):\s*([A-D](?:\s*,\s*[A-D])*)\*\*", chunk, re.I)
    if match is None:
        return None
    letters = [letter.strip().upper() for letter in match.group(1).split(",")]
    return letters[0] if len(letters) == 1 else None


def explanation_from_chunk(chunk: str) -> str:
    match = re.search(r"\*\*Explanation:\*\*(.*?)(?:</details>|^---|\Z)", chunk, re.S | re.M)
    if match:
        return clean_markdown(match.group(1))
    answer = re.search(r"\*\*(?:Correct\s+Answer|Answer):\s*[A-D]\*\*(.*?)(?:</details>|^---|\Z)", chunk, re.S | re.M)
    if answer:
        return clean_markdown(answer.group(1))
    return "MIT 라이선스 SAA-C03 커뮤니티 연습문항의 정답 기준입니다. 세부 근거는 AWS 공식 문서와 함께 복습합니다."


def clean_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"!\[[^\]]*]\([^)]*\)", " ", text)
    text = re.sub(r"\[([^\]]+)]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_`>#|]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def infer_domain_id(relative_path: str, parsed: dict[str, Any]) -> str:
    for hint, domain_id in PATH_DOMAIN_HINTS.items():
        if hint in relative_path:
            return domain_id
    haystack = f"{parsed['question_text']} {' '.join(parsed['choices'])} {parsed['explanation']}".lower()
    scores = {domain.id: 0 for domain in DOMAINS}
    for domain_id, keywords in KEYWORD_DOMAIN_HINTS:
        scores[domain_id] += sum(1 for keyword in keywords if keyword in haystack)
    return max(scores, key=lambda domain_id: (scores[domain_id], DOMAIN_BY_ID[domain_id].weight))


def question_payload(
    parsed: dict[str, Any],
    *,
    source_ref: str,
    mark_active: bool,
    checked_at: str,
) -> dict[str, Any]:
    domain_id = parsed["domain_id"]
    question_id = stable_question_id(parsed)
    return {
        "id": question_id,
        "domain_id": domain_id,
        "concept_id": concept_id_for_domain(domain_id),
        "question_type": "single_choice",
        "question_text": parsed["question_text"],
        "choices": parsed["choices"],
        "answer": parsed["answer"],
        "answer_json": {"choices": [parsed["answer"]]},
        "explanation": parsed["explanation"],
        "difficulty": "medium",
        "source_type": "public_license",
        "source_ref": source_ref,
        "source_license": "MIT",
        "source_tier": "open_license",
        "storage_policy": "raw_allowed",
        "validity_status": "current" if mark_active else "needs_official_check",
        "quality_status": "active" if mark_active else "needs_review",
        "scope_version": "SAA-C03",
        "official_checked_at": checked_at if mark_active else "",
        "quality_notes": "MIT 라이선스 SAA-C03 커뮤니티 연습문항입니다. AWS 공식 시험 가이드와 대조해 사용합니다.",
        "provenance": {
            "repository": source_ref,
            "path": parsed["path"],
            "position": parsed["position"],
            "notice": "원천 repo가 실제 AWS 시험 문제가 아니라고 명시한 커뮤니티 연습문항입니다.",
        },
    }


def stable_question_id(parsed: dict[str, Any]) -> str:
    raw = f"{parsed['path']}:{parsed['position']}:{parsed['question_text']}"
    return f"AWS_SAA_CHATH_{hashlib.sha1(raw.encode('utf-8')).hexdigest()[:16]}"


def concept_id_for_domain(domain_id: str) -> str:
    return domain_id.replace("AWS-SAA-D", "AWS-SAA-CHATH-C-D")


def render_chathuranga_inspect_report(report: dict[str, Any]) -> str:
    lines = [
        "# AWS SAA-C03 Chathuranga Markdown 점검",
        "",
        f"- 파일: {report['files']}개",
        f"- 변환 가능 문항: {report['convertible_questions']}개",
        f"- 제외 후보: {report['skipped']}개",
        "",
        "## 파일별 후보",
    ]
    for row in report["items"]:
        lines.append(f"- {row['path']}: questions {row['questions']}, skipped {row['skipped']}")
    return "\n".join(lines)


def render_chathuranga_convert_report(report: dict[str, Any]) -> str:
    lines = [
        "# AWS SAA-C03 Chathuranga Markdown 변환",
        "",
        f"- 파일: {report['files']}개",
        f"- 변환 문항: {report['converted_questions']}개",
    ]
    if report.get("output"):
        lines.append(f"- 출력: {report['output']}")
    if report["skipped"]:
        lines.extend(["", "## 제외"])
        for row in report["skipped"][:30]:
            lines.append(f"- {row['path']} #{row['position']}: {row['reason']}")
        if len(report["skipped"]) > 30:
            lines.append(f"- ... {len(report['skipped']) - 30}개 추가 제외")
    return "\n".join(lines)
