# Notion 스키마

Notion은 선택 기능입니다. 원장은 Notion이 아니라 SQLite입니다. 사람이 읽는 기본 노트도 Obsidian Markdown입니다.

공개 플러그인 기본값에서는 Notion 쓰기가 꺼져 있습니다. 사용자가 대상 DB를 고르고 아래 환경변수를 켜기 전까지는 동기화 계획만 만듭니다.

```bash
export CERT_STUDY_ENABLE_NOTION_SYNC=1
```

## DB 1: 학습 세션

CBT 세션 하나를 row 하나로 저장합니다.

권장 속성:

```text
이름                 title
시험                 select
모드                 select
날짜                 date
전체 문항            number
정답 수              number
점수                 number
합격선               number
판정                 select
취약 개념            multi_select
다음 복습            date
로컬 세션 ID         rich_text
리포트 경로          rich_text
```

권장 페이지 제목:

```text
YYYY-MM-DD SQLD 20문제 CBT
YYYY-MM-DD SQLD 정규 모의고사
```

권장 페이지 본문:

```markdown
## 결과 요약
- 점수: 14/20
- 환산 점수: 70점
- 합격선: 60점 이상
- 판정: 합격권
- 취약 영역: OUTER JOIN, HAVING, NULL 처리

## 틀린 문제

### 5번. OUTER JOIN
- 문제: ...
- 내 답: 2번. ...
- 정답: 4번. ...
- 영역: SQL 기본 및 활용
- 해설: ...
- 내가 틀린 이유: ...
- 다음 복습: 2026-07-04

## 반복 오답
- NULL 처리: 누적 오답 2회

## 오늘 복습할 개념
### OUTER JOIN
...

## 다음 액션
- 2026-07-04: 오늘 틀린 문제 재시험
```

## DB 2: 틀린 문제

틀린 시도 하나를 row 하나로 저장합니다.

권장 속성:

```text
이름                 title
시험                 select
세션                 relation -> 학습 세션
영역                 select
개념                 select or multi_select
풀이 날짜            date
문제 ID              rich_text
문항 번호            number
내 답                rich_text
정답                 rich_text
실수 유형            select
복습 상태            select
다음 복습            date
로컬 세션 ID         rich_text
```

권장 `복습 상태` 값:

```text
예정
복습 완료
재오답
해결
```

## DB 3: 개념 복습

복습이 필요한 개념 하나를 row 하나로 저장합니다.

권장 속성:

```text
이름                 title
시험                 select
영역                 select
누적 오답 수         number
최근 오답일          date
다음 복습            date
상태                 select
복습 메모            rich_text
```

권장 `상태` 값:

```text
대기
복습 예정
복습 완료
강화 필요
```

## 동기화 규칙

세션 종료 후 흐름은 아래처럼 둡니다.

1. `prepare_notion_sync` 또는 `python3 -m cert_study notion plan <session_id>`로 동기화 계획을 생성합니다.
2. 계획 상태가 `disabled_public_default`라면 사용자에게 보여주기만 하고 Notion에는 쓰지 않습니다.
3. 사용자가 DB를 고르고 동기화를 켠 뒤에만 `학습 세션` 페이지 하나를 만듭니다.
4. Markdown 리포트를 페이지 본문에 붙입니다.
5. 틀린 문제마다 `틀린 문제` row를 하나씩 만듭니다.
6. 반복 취약 개념은 `개념 복습` row를 만들거나 갱신합니다.

Notion이 점수를 계산하게 만들지 않습니다. 채점은 SQLite에서 끝내고, 최종 값만 Notion에 내보냅니다.
