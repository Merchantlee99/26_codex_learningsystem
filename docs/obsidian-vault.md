# Obsidian Vault

Obsidian은 이 플러그인의 기본 오답노트입니다.

채점, 풀이 기록, 복습 일정의 원장은 SQLite에 둡니다. Markdown 파일은 사람이 읽기 위한 출력물입니다. 이렇게 해두면 Notion MCP 연결이 불안정해도 학습 루프가 끊기지 않습니다.

## 기본 위치

세션을 끝내면 기본적으로 아래 위치에 노트가 생성됩니다.

```text
obsidian_vault/
  certifications/
    SQLD/
      sessions/
      concepts/
      review-queue.md
```

이미 쓰고 있는 Obsidian vault에 바로 저장하고 싶으면 아래 환경변수를 설정합니다.

```bash
export CERT_STUDY_OBSIDIAN_VAULT="/absolute/path/to/your/Obsidian Vault"
```

## 생성되는 노트

| 경로 | 역할 |
| --- | --- |
| `certifications/<EXAM>/sessions/*.md` | 세션별 CBT 결과. 점수, 합격선, 취약 영역, 틀린 문제, 해설, 다음 복습일 포함 |
| `certifications/<EXAM>/concepts/*.md` | 개념별 누적 오답 노트. 최근 오답 기록 포함 |
| `certifications/<EXAM>/review-queue.md` | 로컬 SQLite 복습 큐에서 만든 복습 일정 |

## 개인 기록 경계

생성된 vault Markdown 파일은 git에 올라가지 않습니다.

```text
obsidian_vault/**/*.md
```

공개 repo에는 코드와 빈 `.gitkeep`만 남깁니다. 실제 학습 기록은 로컬에만 두는 게 맞습니다.

## Notion과의 관계

Notion은 선택 기능입니다. 사용자가 대상 DB를 직접 고른 뒤, 보조 DB 뷰가 필요할 때만 씁니다.

기본 학습 루프에는 Notion이 필요 없습니다.

```text
Codex 대화창 -> MCP 도구 -> SQLite -> Markdown -> Obsidian
```
