# 과목 확장 계획

이 공개 레포는 기본 과목을 `SQLD` 하나로 둡니다.

이 레포는 문제은행 마켓플레이스가 아니라 학습 하네스를 보여주는 포트폴리오 코드베이스입니다. 과목을 늘릴 때는 조심해야 합니다. 시험 메타데이터는 바뀔 수 있고, 문제집 원문이나 시험 덤프를 그대로 넣으면 저작권과 신뢰성 문제가 생깁니다.

## 권장 흐름

과목이 하나이거나 두 개 정도라면 지금처럼 Python seed 패턴을 써도 됩니다.

```text
cert_study/seed_sqld.py
cert_study/seed_adsp.py
```

실제 과목이 2~3개 이상이 되면 `seed_*.py` 파일을 계속 늘리지 말고 데이터팩 가져오기 도구로 바꾸는 게 낫습니다.

```text
question_banks/
  sqld.yaml
  adsp.yaml
  kr-info-processing-engineer.yaml
  aws-ai-practitioner.yaml
  aws-cloud-practitioner.yaml
  aws-solutions-architect-associate.yaml
  gcp-generative-ai-leader.yaml
```

나중에 가져오기 도구를 만든다면 이런 명령을 생각하면 됩니다.

```bash
python3 -m cert_study bank validate question_banks/adsp.yaml
python3 -m cert_study bank import question_banks/adsp.yaml
```

처음부터 가져오기 도구를 만들 필요는 없습니다. 두 번째나 세 번째 과목에서 Python seed 방식이 불편해질 때 바꾸면 충분합니다. 공개 레포는 작게 유지하는 편이 낫습니다.

## 추가하려는 과목

개인 학습 목록은 아래처럼 잡습니다.

| 내부 ID | 표시 이름 | 그룹 | 메모 |
| --- | --- | --- | --- |
| `SQLD` | SQLD | 국내 데이터/IT | 현재 기본 합성 문제은행 |
| `ADSP` | ADsP | 국내 데이터/IT | SQLD 다음으로 추가해서 두 번째 문제은행 패턴 검증 |
| `KR_INFO_PROCESSING_ENGINEER` | 정보처리기사 | 국내 데이터/IT | 범위가 크므로 ADsP 이후라면 가져오기 도구 형식 권장 |
| `AWS_AI_PRACTITIONER` | AWS Certified AI Practitioner | 클라우드/AI | 추가 전 AWS 공식 exam guide 확인 필요 |
| `AWS_CLOUD_PRACTITIONER` | AWS Certified Cloud Practitioner | 클라우드 기본 | 추가 전 AWS 공식 exam guide 확인 필요 |
| `AWS_SOLUTIONS_ARCHITECT_ASSOCIATE` | AWS Certified Solutions Architect Associate | 클라우드 아키텍처 | 추가 전 AWS 공식 exam guide 확인 필요 |
| `GCP_GENERATIVE_AI_LEADER` | Google Cloud Generative AI Leader | 클라우드/AI | 추가 전 Google Cloud 공식 exam guide 확인 필요 |

공식 시험 코드가 바뀌더라도 내부 ID는 안정적으로 유지합니다. 공식 코드, 버전, 가이드 URL, 확인 날짜는 문제은행 파일의 메타데이터로 따로 저장합니다.

## 데이터팩 형태

나중에 YAML/JSON 문제은행을 만들면 기존 SQLite 테이블과 바로 매핑되도록 잡습니다.

```yaml
exam:
  id: ADSP
  name: ADsP
  official_question_count: 50
  official_duration_minutes: 90
  pass_score: 60
  domain_min_score: 0
  source_policy: synthetic_or_user_owned_only
  official_guide_url: ""
  verified_at: "YYYY-MM-DD"

domains:
  - id: ADSP-D1
    name: 데이터 이해
    official_weight: 20
    official_question_count: 10

concepts:
  - id: ADSP-C001
    domain_id: ADSP-D1
    name: 데이터의 유형
    review_note: "정형, 반정형, 비정형 데이터의 차이를 구분한다."

questions:
  - id: ADSP-Q001
    domain_id: ADSP-D1
    concept_id: ADSP-C001
    question_text: "Synthetic practice question text."
    choices:
      - "Choice 1"
      - "Choice 2"
      - "Choice 3"
      - "Choice 4"
    answer: 1
    explanation: "Why the answer is correct."
    difficulty: easy
    source_type: synthetic
    source_ref: "Original practice question; not copied from a paid workbook or exam dump."
```

YAML 예시는 구조 설명용이라 일부 값은 영어 식별자를 그대로 둡니다. 실제 문제 문장과 해설은 한국어로 써도 됩니다.

## 가져오기 도구 검증 규칙

문제은행을 가져오기 전에 최소한 아래를 확인합니다.

- exam ID가 중복되지 않고 안정적인지
- 공식 메타데이터에 `verified_at` 날짜와 가이드 URL이 있는지
- 시험이 공개 가중치를 제공한다면 domain weight 합이 100인지
- 모든 문제가 존재하는 domain과 concept을 참조하는지
- 정답이 1~4 사이인지
- 엔진을 확장하지 않았다면 모든 문제가 보기 4개인지
- 정규 모드나 커스텀 모드에 필요한 문항 수가 충분한지
- `source_type`이 `synthetic`, `user_owned_note`, `official_sample_allowed` 중 하나인지
- 유료 문제집 스캔, 복사한 기출, braindump, 상업 문제은행 원문이 들어가지 않았는지

## 추천 순서

1. `SQLD`는 공개 repo demo로 유지합니다.
2. `ADSP`는 두 번째 과목으로 추가해서 현재 Python seed 패턴을 한 번 더 검증합니다.
3. `정보처리기사`를 그다음에 추가한다면 먼저 YAML/JSON 가져오기 도구를 만듭니다.
4. AWS와 GCP 문제은행은 Python 소스가 아니라 데이터팩으로 추가합니다.
5. 모든 문제은행을 가져온 뒤 작은 CBT 세션을 돌리는 공통 하네스 테스트를 추가합니다.

## 공개 repo 경계

공개 repo에 들어가도 되는 것:

- 학습 엔진
- 작은 기본 합성 문제은행 하나
- 가져오기 schema 또는 예시
- 하네스가 동작함을 보여주는 테스트
- private 문제은행을 어떻게 추가할지 설명하는 문서

공개 repo에 넣지 않는 것:

- 개인 학습 기록
- Obsidian 생성 노트
- 유료 문제집 내용
- 복사한 기출 또는 시험 덤프
- 개인 Notion DB ID

개인 학습용 실제 문제은행은 로컬이나 private repo에 두는 편이 맞습니다.
