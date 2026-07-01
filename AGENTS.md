# 코덱스 학습 시스템 작업 규칙

이 repo는 Codex 기반 CBT 학습 플러그인입니다. 구현 범위는 아래 학습 루프에 맞춥니다.

```text
세션 시작 -> 문제 하나 제시 -> 답변 기록 -> 세션 종료 -> 채점/리포트 -> 복습 일정 생성
```

## 운영 규칙

- 플러그인 동작이 바뀌면 `.codex-plugin/plugin.json`과 `.mcp.json`이 유효한지 확인합니다.
- 로컬 학습 작업은 `python3 -m cert_study ...` 명령을 기준으로 실행합니다.
- Codex-facing 흐름은 MCP 도구를 우선 사용하고, CLI는 수동 스모크 테스트와 디버깅 표면으로 둡니다.
- `data/study.sqlite`는 로컬 변경 상태입니다. 커밋하지 않습니다.
- `reports/sessions/*.md`와 `obsidian_vault/**/*.md`는 사용자 학습 기록입니다. 커밋하지 않습니다.
- 유료 문제집 내용, 복사한 기출, 실제 시험 덤프를 추가하지 않습니다.
- 문제를 생성할 때는 합성 문항임을 표시하고 시험 개념에 근거를 둡니다.
- 원장은 SQLite입니다. 사람이 읽는 기본 노트는 Obsidian Markdown입니다.
- Notion 동기화도 SQLite/session report를 원장으로 사용합니다. 공개 기본값은 사용자가 Notion 대상을 명시하기 전까지 비활성/계획 생성 상태로 유지합니다.
- 사용자가 명시적으로 요청하지 않는 한 앱 UI는 범위 밖입니다.

## 검증

코드 변경이 동작한다고 말하기 전 아래를 실행합니다.

```bash
python3 -m unittest discover -s tests
python3 /Users/isanginn/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py .
```

CLI 동작을 바꿨다면 작은 세션 스모크 테스트도 실행합니다.

```bash
python3 -m cert_study init --reset
python3 -m cert_study session start --exam SQLD --count 5 --seed 1
```
