from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass


EXAM = {
    "id": "ADSP",
    "name": "ADsP",
    "official_question_count": 50,
    "official_duration_minutes": 90,
    "pass_score": 60.0,
    "domain_min_score": 40.0,
    "notes": "ADsP recent-scope synthetic training profile: 50 questions, 90 minutes, 60+ pass line, 40% domain minimum reference.",
}

DOMAINS = [
    ("ADSP-D1", "ADSP", "데이터 이해", 20.0, 10),
    ("ADSP-D2", "ADSP", "데이터 분석 기획", 20.0, 10),
    ("ADSP-D3", "ADSP", "데이터 분석", 60.0, 30),
]


@dataclass(frozen=True)
class ConceptSpec:
    id: str
    domain_id: str
    name: str
    review_note: str
    correct_focus: str
    distractors: tuple[str, str, str]
    scenario: str


CONCEPT_SPECS = [
    ConceptSpec("ADSP-C-DATA", "ADSP-D1", "데이터와 정보", "데이터는 관찰이나 측정의 원천 값이고, 정보는 의사결정에 쓸 수 있게 처리된 의미 있는 결과다.", "데이터를 목적에 맞게 가공해 의사결정에 쓸 수 있는 상태", ("가공되지 않은 센서 원시값 그 자체", "항상 정형 테이블에만 저장되는 값", "분석가의 주관적 의견만 모은 문장"), "고객 로그를 요약해 이탈 위험 고객 목록을 만든다."),
    ConceptSpec("ADSP-C-DB", "ADSP-D1", "데이터베이스", "데이터베이스는 통합, 저장, 운영, 공용 데이터를 체계적으로 관리하는 구조다.", "여러 사용자가 공유할 수 있게 체계적으로 저장된 데이터 집합", ("개인 메모장에만 저장된 임시 기록", "분석 결과를 발표하는 슬라이드", "운영 규칙 없이 흩어진 파일 묶음"), "부서별 고객 파일을 하나의 관리 체계로 통합한다."),
    ConceptSpec("ADSP-C-BIGDATA", "ADSP-D1", "빅데이터 특성", "빅데이터는 규모, 다양성, 속도, 가치, 진실성 같은 특성을 함께 고려한다.", "대용량, 다양성, 빠른 생성 속도 등으로 기존 방식만으로 처리하기 어려운 데이터", ("항상 행과 열만 있는 작은 표본 데이터", "정확성이 검증된 통계표만 의미", "저장 비용이 낮은 모든 파일"), "실시간 클릭 로그와 이미지, 텍스트 리뷰를 함께 분석한다."),
    ConceptSpec("ADSP-C-DATASCIENCE", "ADSP-D1", "데이터 사이언스", "데이터 사이언스는 통계, 도메인 지식, 컴퓨팅을 결합해 문제를 해결한다.", "통계적 사고와 도메인 이해, 기술 구현을 결합하는 문제 해결 접근", ("시각화 도구 사용법만 익히는 활동", "데이터 저장소를 백업하는 운영 업무", "정답이 정해진 계산만 반복하는 절차"), "매출 감소 원인을 데이터, 비즈니스 맥락, 모델링으로 함께 분석한다."),
    ConceptSpec("ADSP-C-ETHICS", "ADSP-D1", "데이터 윤리", "데이터 활용은 개인정보 보호, 목적 제한, 편향 완화, 설명 가능성을 고려해야 한다.", "개인정보 보호와 편향 위험을 고려해 책임 있게 데이터를 활용하는 것", ("동의 없이 모든 데이터를 수집하는 것", "정확도만 높으면 모든 활용이 정당하다는 판단", "모델 결과를 절대적 사실로 간주하는 것"), "민감 정보가 포함된 고객 데이터를 분석 전에 익명화한다."),
    ConceptSpec("ADSP-C-PROBLEM", "ADSP-D2", "분석 문제 정의", "좋은 분석 과제는 비즈니스 문제, 의사결정, 데이터 가능성을 함께 명확히 한다.", "비즈니스 의사결정과 연결된 분석 질문을 명확히 하는 것", ("도구를 먼저 정하고 데이터를 억지로 맞추는 것", "모든 데이터를 수집한 뒤 목적을 나중에 정하는 것", "분석 결과를 사용할 사람을 고려하지 않는 것"), "프로모션 효과를 판단하기 위해 어떤 지표를 비교할지 정한다."),
    ConceptSpec("ADSP-C-CRISP", "ADSP-D2", "CRISP-DM", "CRISP-DM은 비즈니스 이해, 데이터 이해, 준비, 모델링, 평가, 전개를 반복하는 분석 방법론이다.", "비즈니스 이해에서 전개까지 반복적으로 수행하는 데이터 마이닝 방법론", ("소프트웨어 배포만 위한 형상관리 절차", "데이터베이스 정규화 전용 절차", "보안 로그 수집만을 위한 운영 규칙"), "분석 목적을 정한 뒤 데이터 이해와 모델 평가를 반복한다."),
    ConceptSpec("ADSP-C-MASTERPLAN", "ADSP-D2", "분석 마스터 플랜", "분석 마스터 플랜은 우선순위, 실행 가능성, 기대 효과, 추진 체계를 고려한다.", "분석 과제의 우선순위와 실행 로드맵을 정하는 계획", ("무작위로 모델을 많이 만드는 목록", "DB 테이블명만 정리한 산출물", "개별 SQL 튜닝 기록만 모은 문서"), "여러 분석 후보 중 효과와 난이도를 기준으로 추진 순서를 정한다."),
    ConceptSpec("ADSP-C-GOV", "ADSP-D2", "분석 거버넌스", "분석 거버넌스는 조직, 프로세스, 데이터 품질, 역할과 책임을 관리한다.", "분석 활동의 기준, 역할, 품질 관리를 체계화하는 운영 체계", ("분석가 개인 취향대로 도구를 고르는 방식", "모델 정확도만 기록하는 엑셀 파일", "서버 성능 모니터링만 담당하는 체계"), "분석 과제 승인 절차와 데이터 품질 책임자를 정한다."),
    ConceptSpec("ADSP-C-METRIC", "ADSP-D2", "성과 지표 설계", "분석 성과 지표는 목표와 연결되어야 하고 측정 가능해야 한다.", "분석 목적과 연결된 측정 가능한 판단 기준", ("보기 좋은 그래프 색상 목록", "모든 숫자를 무조건 평균으로 요약하는 기준", "수집하기 어려운 막연한 만족감만 쓰는 지표"), "이탈 예측 모델 도입 후 재방문율과 캠페인 전환율을 추적한다."),
    ConceptSpec("ADSP-C-DESCRIPTIVE", "ADSP-D3", "기술통계", "기술통계는 평균, 중앙값, 분산, 표준편차 등으로 데이터의 분포를 요약한다.", "데이터의 중심과 산포를 요약해 현재 상태를 파악하는 방법", ("미래 값을 반드시 정확히 맞히는 방법", "데이터를 암호화하는 보안 절차", "모든 이상치를 자동 삭제하는 규칙"), "구매 금액의 평균과 중앙값 차이를 비교한다."),
    ConceptSpec("ADSP-C-PROB", "ADSP-D3", "확률과 분포", "확률분포는 확률변수가 취할 수 있는 값과 가능성을 표현한다.", "불확실한 사건의 발생 가능성을 수치로 다루는 틀", ("데이터베이스 접근 권한 목록", "모델 배포 서버의 CPU 사용률만 의미", "시각화 차트 색상 팔레트"), "불량률이 일정할 때 표본에서 불량품 수의 가능성을 계산한다."),
    ConceptSpec("ADSP-C-INFER", "ADSP-D3", "추정과 검정", "추정과 가설검정은 표본으로 모집단 특성을 판단할 때 쓴다.", "표본 데이터로 모집단에 대한 주장이나 차이를 판단하는 절차", ("이미 알고 있는 전체 모집단을 단순 정렬하는 절차", "컬럼명을 영문으로 바꾸는 전처리", "이미지 파일을 압축하는 작업"), "A/B 테스트에서 두 집단 전환율 차이가 우연인지 판단한다."),
    ConceptSpec("ADSP-C-REG", "ADSP-D3", "회귀분석", "회귀분석은 종속변수와 독립변수 사이의 관계를 설명하거나 예측한다.", "연속형 결과값과 설명 변수 사이의 관계를 모델링하는 방법", ("범주형 라벨만 무조건 군집화하는 방법", "테이블 권한을 부여하는 명령", "데이터를 물리적으로 백업하는 절차"), "광고비와 할인율로 매출액을 예측한다."),
    ConceptSpec("ADSP-C-CLASS", "ADSP-D3", "분류분석", "분류는 입력 특성을 바탕으로 사전에 정해진 범주를 예측한다.", "정해진 클래스나 라벨을 예측하는 지도학습 문제", ("연속형 매출액만 예측하는 선형 모델", "비슷한 데이터를 라벨 없이 묶는 작업", "인덱스를 생성해 검색 속도를 높이는 작업"), "고객이 이탈할지 유지될지 예측한다."),
    ConceptSpec("ADSP-C-CLUSTER", "ADSP-D3", "군집분석", "군집분석은 정답 라벨 없이 유사한 관측치를 묶는 비지도학습이다.", "라벨 없이 유사한 데이터끼리 그룹을 찾는 방법", ("정답 라벨을 반드시 주고 학습하는 분류", "종속변수의 연속값을 예측하는 회귀", "트랜잭션을 확정하는 명령"), "구매 패턴이 비슷한 고객군을 찾는다."),
    ConceptSpec("ADSP-C-ASSOC", "ADSP-D3", "연관분석", "연관분석은 항목 간 동시 발생 패턴을 지지도, 신뢰도, 향상도 등으로 본다.", "장바구니 항목처럼 함께 발생하는 규칙을 찾는 방법", ("시계열의 추세선만 추정하는 방법", "데이터베이스 스키마를 변경하는 명령", "모든 변수를 표준화하는 지표"), "기저귀를 산 고객이 물티슈도 함께 사는 패턴을 찾는다."),
    ConceptSpec("ADSP-C-TREE", "ADSP-D3", "의사결정나무", "의사결정나무는 변수 조건에 따라 데이터를 분할해 예측 규칙을 만든다.", "조건 분기를 통해 해석 가능한 예측 규칙을 만드는 모델", ("항상 거리 기반으로 군집 수를 정하는 모델", "테이블을 제3정규형으로 분해하는 기법", "문자열만 정렬하는 알고리즘"), "나이, 이용 빈도, 결제 금액 기준으로 이탈 여부 규칙을 만든다."),
    ConceptSpec("ADSP-C-EVAL", "ADSP-D3", "모델 평가", "분류 모델은 정확도, 정밀도, 재현율, F1, ROC-AUC 등 목적에 맞는 지표를 본다.", "문제 목적에 맞는 성능 지표로 모델을 검증하는 것", ("학습 데이터 정확도만 높으면 무조건 배포하는 것", "모델 파일명을 짧게 바꾸는 것", "분석 전 모든 결측치를 평균으로만 대체하는 것"), "사기 탐지에서는 정확도보다 재현율과 정밀도를 함께 확인한다."),
    ConceptSpec("ADSP-C-PREPROCESS", "ADSP-D3", "데이터 전처리", "전처리는 결측, 이상치, 스케일, 범주 인코딩 등을 분석 목적에 맞게 다룬다.", "모델링 전에 데이터 품질과 형태를 분석 가능하게 정리하는 과정", ("모델 결과를 발표자료로만 꾸미는 과정", "데이터를 무조건 삭제하는 과정", "DB 계정을 발급하는 과정"), "결측치와 이상치를 확인하고 변수 스케일을 조정한다."),
]


QUESTION_PLAN = {
    "ADSP-D1": 2,
    "ADSP-D2": 2,
    "ADSP-D3": 3,
}


def rotate_choices(correct: str, distractors: tuple[str, str, str], idx: int) -> tuple[list[str], int]:
    choices = [correct, *distractors]
    shift = idx % 4
    rotated = choices[shift:] + choices[:shift]
    return rotated, rotated.index(correct) + 1


def build_questions() -> list[dict[str, object]]:
    questions: list[dict[str, object]] = []
    idx = 1
    for spec in CONCEPT_SPECS:
        repeat = QUESTION_PLAN[spec.domain_id]
        templates = [
            f"{spec.name}에 대한 설명으로 가장 적절한 것은?",
            f"다음 상황에 가장 잘 맞는 ADsP 개념은? {spec.scenario}",
            f"{spec.name}를 학습할 때 피해야 할 판단으로 가장 거리가 먼 것은?",
        ]
        for n in range(repeat):
            choices, answer = rotate_choices(spec.correct_focus, spec.distractors, idx)
            questions.append(
                {
                    "id": f"ADSP-Q{idx:03d}",
                    "exam_id": "ADSP",
                    "domain_id": spec.domain_id,
                    "concept_id": spec.id,
                    "question_text": templates[n],
                    "choices_json": json.dumps(choices, ensure_ascii=False),
                    "answer": answer,
                    "explanation": spec.review_note,
                    "difficulty": "medium" if n else "easy",
                    "source_type": "synthetic_recent_scope",
                    "source_ref": "ADsP 공개 포트폴리오용 합성 훈련 문항입니다. 실제 시험 덤프나 상업 문제집 원문을 복제하지 않았습니다.",
                }
            )
            idx += 1
    return questions


CONCEPTS = [(spec.id, "ADSP", spec.domain_id, spec.name, spec.review_note) for spec in CONCEPT_SPECS]
QUESTIONS = build_questions()


def seed(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO exams
        (id, name, official_question_count, official_duration_minutes, pass_score, domain_min_score, notes)
        VALUES (:id, :name, :official_question_count, :official_duration_minutes, :pass_score, :domain_min_score, :notes)
        """,
        EXAM,
    )
    conn.executemany(
        "INSERT OR REPLACE INTO domains (id, exam_id, name, official_weight, official_question_count) VALUES (?, ?, ?, ?, ?)",
        DOMAINS,
    )
    conn.executemany(
        "INSERT OR REPLACE INTO concepts (id, exam_id, domain_id, name, review_note) VALUES (?, ?, ?, ?, ?)",
        CONCEPTS,
    )
    conn.executemany(
        """
        INSERT OR REPLACE INTO questions
        (id, exam_id, domain_id, concept_id, question_text, choices_json, answer, explanation, difficulty, source_type, source_ref)
        VALUES (:id, :exam_id, :domain_id, :concept_id, :question_text, :choices_json, :answer, :explanation, :difficulty, :source_type, :source_ref)
        """,
        QUESTIONS,
    )
    conn.commit()

