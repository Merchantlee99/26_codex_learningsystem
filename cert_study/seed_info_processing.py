from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass


EXAM = {
    "id": "KR_INFO_PROCESSING_ENGINEER",
    "name": "정보처리기사",
    "official_question_count": 100,
    "official_duration_minutes": 150,
    "pass_score": 60.0,
    "domain_min_score": 40.0,
    "notes": "Q-Net 2026 information-processing-engineer scope aligned synthetic training profile: 100 written questions, 150 minutes, 60+ average pass line, 40% subject minimum reference.",
}

DOMAINS = [
    ("IPE-D1", "KR_INFO_PROCESSING_ENGINEER", "소프트웨어 설계", 20.0, 20),
    ("IPE-D2", "KR_INFO_PROCESSING_ENGINEER", "소프트웨어 개발", 20.0, 20),
    ("IPE-D3", "KR_INFO_PROCESSING_ENGINEER", "데이터베이스 구축", 20.0, 20),
    ("IPE-D4", "KR_INFO_PROCESSING_ENGINEER", "프로그래밍 언어 활용", 20.0, 20),
    ("IPE-D5", "KR_INFO_PROCESSING_ENGINEER", "정보시스템 구축관리", 20.0, 20),
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
    ConceptSpec("IPE-C-REQ", "IPE-D1", "요구사항 분석", "요구사항 분석은 사용자의 문제와 제약을 명확히 도출하고 기능/비기능 요구사항으로 정리한다.", "사용자 요구와 제약을 기능/비기능 요구사항으로 명확히 정리하는 활동", ("코드 난독화만 수행하는 활동", "운영 서버 CPU 사용률만 측정하는 활동", "DB 백업 파일만 압축하는 활동"), "신규 시스템의 응답시간, 권한, 업무 흐름을 이해관계자와 확인한다."),
    ConceptSpec("IPE-C-UML", "IPE-D1", "UML", "UML은 시스템 구조와 행위를 표준 다이어그램으로 표현하는 모델링 언어다.", "시스템 구조와 행위를 시각적으로 모델링하는 표준 표현", ("SQL 튜닝 전용 명령어", "네트워크 패킷 암호화 방식", "운영체제 스케줄링 알고리즘"), "사용 사례와 클래스 관계를 다이어그램으로 표현한다."),
    ConceptSpec("IPE-C-ARCH", "IPE-D1", "소프트웨어 아키텍처", "아키텍처는 시스템 주요 구성요소와 관계, 품질 속성을 만족시키는 큰 구조를 정한다.", "시스템 구성요소와 관계를 정하고 품질 속성을 반영하는 상위 설계", ("소스 파일명만 일괄 변경하는 작업", "테스트 데이터만 삭제하는 작업", "권한 없는 사용자의 로그인 시도"), "확장성과 장애 격리를 위해 계층형 구조를 검토한다."),
    ConceptSpec("IPE-C-PATTERN", "IPE-D1", "디자인 패턴", "디자인 패턴은 반복되는 설계 문제에 대한 재사용 가능한 해결 구조다.", "반복되는 설계 문제를 해결하는 재사용 가능한 설계 템플릿", ("실제 시험문제를 암기하는 목록", "DB 테이블 데이터를 백업하는 명령", "하드웨어 장비 목록"), "객체 생성 책임을 분리하려고 Factory Method를 검토한다."),
    ConceptSpec("IPE-C-UI", "IPE-D1", "UI/UX 설계", "UI/UX 설계는 사용자의 목적 달성을 쉽게 하는 화면 흐름과 상호작용을 설계한다.", "사용자가 업무를 쉽게 수행하도록 화면과 상호작용을 설계하는 활동", ("서버 로그만 암호화하는 활동", "데이터베이스 정규화만 수행하는 활동", "컴파일러 최적화 옵션만 조정하는 활동"), "반복 입력을 줄이고 오류 메시지를 명확히 보여준다."),
    ConceptSpec("IPE-C-MODULE", "IPE-D2", "모듈화", "모듈화는 응집도는 높이고 결합도는 낮추어 변경과 재사용을 쉽게 한다.", "응집도를 높이고 결합도를 낮추어 프로그램을 독립 단위로 나누는 것", ("모든 기능을 하나의 거대한 함수에 넣는 것", "테이블의 모든 컬럼을 문자열로 바꾸는 것", "테스트 없이 배포하는 것"), "결제, 회원, 알림 기능을 독립 모듈로 분리한다."),
    ConceptSpec("IPE-C-TEST", "IPE-D2", "소프트웨어 테스트", "테스트는 결함을 발견하고 요구사항 충족 여부를 확인하는 활동이다.", "결함을 발견하고 요구사항 충족 여부를 검증하는 활동", ("운영 DB를 무조건 삭제하는 활동", "소스코드 주석만 제거하는 활동", "프로젝트명을 변경하는 활동"), "경계값 입력에서 회원 가입 로직이 올바르게 동작하는지 확인한다."),
    ConceptSpec("IPE-C-INTEGRATION", "IPE-D2", "통합 구현", "통합 구현은 모듈과 외부 시스템 간 인터페이스, 메시지, 오류 처리를 설계하고 검증한다.", "모듈과 외부 시스템 사이의 인터페이스와 데이터 교환을 구현하는 것", ("단일 변수명을 바꾸는 리팩터링만 의미", "개발자 PC 배경화면을 통일하는 것", "사용자 비밀번호를 평문 저장하는 것"), "주문 시스템과 결제 API 사이의 요청/응답 규격을 맞춘다."),
    ConceptSpec("IPE-C-VCS", "IPE-D2", "형상관리", "형상관리는 소스, 문서, 설정의 변경 이력을 통제하고 추적한다.", "소스와 산출물의 버전, 변경 이력, 기준선을 관리하는 활동", ("운영 로그를 삭제하는 활동", "테스트 케이스를 무작위로 실행하는 활동", "사용자 화면 색상만 고르는 활동"), "릴리스 기준선을 태그로 남기고 변경 이력을 추적한다."),
    ConceptSpec("IPE-C-SECURECODING", "IPE-D2", "보안 코딩", "보안 코딩은 입력 검증, 인증/인가, 오류 처리 등을 통해 취약점을 줄인다.", "입력 검증과 권한 확인 등으로 취약점을 줄이는 구현 방식", ("SQL 문자열을 사용자 입력으로 그대로 붙이는 방식", "예외 내용을 사용자에게 모두 노출하는 방식", "비밀번호를 평문 로그에 남기는 방식"), "사용자 입력을 검증하고 Prepared Statement를 사용한다."),
    ConceptSpec("IPE-C-ERD", "IPE-D3", "데이터 모델링", "데이터 모델링은 업무 데이터를 엔터티, 속성, 관계로 구조화한다.", "업무 데이터를 엔터티, 속성, 관계로 표현하는 설계 활동", ("화면 색상표만 정의하는 활동", "프로그램 실행 파일만 압축하는 활동", "네트워크 케이블 종류만 고르는 활동"), "고객, 주문, 상품의 관계를 ERD로 정리한다."),
    ConceptSpec("IPE-C-NORMAL", "IPE-D3", "정규화", "정규화는 함수 종속을 바탕으로 중복과 이상 현상을 줄이는 설계 과정이다.", "중복과 삽입/갱신/삭제 이상을 줄이기 위해 릴레이션을 분해하는 과정", ("조회 성능을 위해 항상 모든 테이블을 합치는 과정", "서버 계정을 생성하는 과정", "프로그램을 컴파일하는 과정"), "주문 테이블에서 고객 속성 반복 저장을 분리한다."),
    ConceptSpec("IPE-C-SQL", "IPE-D3", "SQL", "SQL은 데이터 정의, 조작, 제어, 트랜잭션 처리를 위한 데이터베이스 언어다.", "데이터 정의와 조작, 제어를 수행하는 관계형 데이터베이스 언어", ("운영체제 커널을 컴파일하는 언어", "이미지를 압축하는 전용 포맷", "네트워크 라우팅 프로토콜"), "조건에 맞는 주문 데이터를 조회하고 집계한다."),
    ConceptSpec("IPE-C-TRANSACTION", "IPE-D3", "트랜잭션", "트랜잭션은 ACID 특성을 만족해야 하는 논리적 작업 단위다.", "원자성, 일관성, 고립성, 지속성을 고려하는 작업 단위", ("화면 배색을 정하는 디자인 단위", "소스 파일명 규칙", "로그 파일 압축 단위"), "계좌 이체에서 출금과 입금이 모두 성공하거나 모두 취소되도록 한다."),
    ConceptSpec("IPE-C-INDEX", "IPE-D3", "인덱스", "인덱스는 검색 성능을 높일 수 있지만 저장공간과 갱신 비용이 든다.", "검색 속도 향상을 위해 별도 탐색 구조를 두는 것", ("모든 데이터를 무조건 암호화하는 것", "테이블을 삭제하는 것", "컴파일 경고를 숨기는 것"), "자주 조회하는 고객 ID 컬럼에 인덱스를 검토한다."),
    ConceptSpec("IPE-C-DATATYPE", "IPE-D4", "자료형", "자료형은 값의 종류와 연산 가능 범위를 정한다.", "값의 종류와 저장 방식, 가능한 연산을 정하는 분류", ("네트워크 주소 변환 장비", "데이터베이스 백업 정책", "화면 전환 애니메이션"), "정수 계산에는 integer 계열, 참/거짓에는 boolean 계열을 사용한다."),
    ConceptSpec("IPE-C-CONTROL", "IPE-D4", "제어문", "제어문은 조건과 반복을 통해 프로그램 실행 흐름을 제어한다.", "조건 분기와 반복으로 실행 흐름을 제어하는 문장", ("테이블 권한을 부여하는 SQL 명령", "운영 서버를 재시작하는 절차", "네트워크 포트를 물리적으로 연결하는 작업"), "조건에 따라 할인율을 다르게 적용한다."),
    ConceptSpec("IPE-C-OOP", "IPE-D4", "객체지향", "객체지향은 캡슐화, 상속, 다형성 등을 통해 변경에 강한 구조를 만든다.", "객체의 상태와 행위를 묶고 캡슐화, 상속, 다형성을 활용하는 방식", ("모든 코드를 전역 변수로만 작성하는 방식", "DB 인덱스를 무조건 삭제하는 방식", "네트워크 패킷을 암호화하지 않는 방식"), "공통 결제 인터페이스를 두고 카드/간편결제 구현을 분리한다."),
    ConceptSpec("IPE-C-OS", "IPE-D4", "운영체제", "운영체제는 프로세스, 메모리, 파일, 입출력 자원을 관리한다.", "컴퓨터 자원을 관리하고 사용자와 하드웨어 사이를 중재하는 시스템 소프트웨어", ("관계형 데이터베이스의 테이블 설계도", "웹 화면 스타일시트", "비즈니스 요구사항 명세서만 의미"), "여러 프로세스가 CPU와 메모리를 효율적으로 사용하게 한다."),
    ConceptSpec("IPE-C-NETWORK", "IPE-D4", "네트워크 기초", "네트워크는 계층, 주소, 프로토콜, 라우팅을 통해 데이터를 교환한다.", "프로토콜과 주소 체계를 통해 시스템 간 데이터를 교환하는 구조", ("소스코드 버전만 관리하는 체계", "데이터베이스 정규화 단계", "객체 생성 전용 디자인 패턴"), "클라이언트가 TCP/IP를 통해 서버 API와 통신한다."),
    ConceptSpec("IPE-C-SECURITY", "IPE-D5", "정보보안", "정보보안은 기밀성, 무결성, 가용성을 중심으로 위험을 줄인다.", "기밀성, 무결성, 가용성을 보호하는 관리와 기술 조치", ("화면 레이아웃만 개선하는 활동", "코드 줄 수를 늘리는 활동", "DB 컬럼명을 길게 만드는 활동"), "중요 데이터에 접근 제어와 암호화를 적용한다."),
    ConceptSpec("IPE-C-AUTH", "IPE-D5", "인증과 인가", "인증은 신원 확인, 인가는 확인된 주체에게 허용 범위를 부여하는 것이다.", "인증은 누구인지 확인하고 인가는 무엇을 할 수 있는지 결정하는 것", ("인증은 권한 부여, 인가는 신원 확인으로 완전히 반대", "둘 다 데이터 압축 방식", "둘 다 화면 디자인 원칙"), "로그인 후 관리자 메뉴 접근 권한을 검사한다."),
    ConceptSpec("IPE-C-DEPLOY", "IPE-D5", "배포와 운영", "배포와 운영은 릴리스, 모니터링, 장애 대응, 롤백 계획을 포함한다.", "서비스 변경을 안전하게 반영하고 모니터링/롤백을 준비하는 활동", ("개발 완료 후 아무 검증 없이 수동 복사하는 것", "테이블명을 줄이는 작업만 의미", "사용자 요구사항을 삭제하는 활동"), "새 버전을 배포하기 전 헬스체크와 롤백 절차를 준비한다."),
    ConceptSpec("IPE-C-CLOUD", "IPE-D5", "클라우드와 가상화", "클라우드는 필요한 IT 자원을 네트워크를 통해 탄력적으로 제공하는 모델이다.", "컴퓨팅 자원을 필요한 만큼 탄력적으로 제공받는 방식", ("물리 서버만 직접 구매해야 하는 방식", "소스코드를 한 파일에 합치는 방식", "테이블 정규화 단계"), "사용량에 따라 서버 자원을 늘리거나 줄인다."),
    ConceptSpec("IPE-C-PROJECT", "IPE-D5", "프로젝트 관리", "프로젝트 관리는 범위, 일정, 비용, 품질, 위험을 균형 있게 관리한다.", "일정, 범위, 비용, 품질, 위험을 통합적으로 관리하는 활동", ("코드 주석을 모두 제거하는 활동", "암호를 평문으로 공유하는 활동", "DB 백업을 하지 않는 운영 방식"), "릴리스 범위와 일정, 위험 대응 계획을 관리한다."),
]


def rotate_choices(correct: str, distractors: tuple[str, str, str], idx: int) -> tuple[list[str], int]:
    choices = [correct, *distractors]
    shift = idx % 4
    rotated = choices[shift:] + choices[:shift]
    return rotated, rotated.index(correct) + 1


def build_questions() -> list[dict[str, object]]:
    questions: list[dict[str, object]] = []
    idx = 1
    for spec in CONCEPT_SPECS:
        templates = [
            f"{spec.name}에 대한 설명으로 가장 적절한 것은?",
            f"다음 상황에서 가장 직접적으로 확인해야 할 개념은? {spec.scenario}",
            f"다음 중 {spec.name} 설명으로 옳은 것은?",
            f"{spec.name} 적용에 가장 적절한 접근은?",
        ]
        for n, text in enumerate(templates, start=1):
            choices, answer = rotate_choices(spec.correct_focus, spec.distractors, idx)
            questions.append(
                {
                    "id": f"IPE-Q{idx:03d}",
                    "exam_id": "KR_INFO_PROCESSING_ENGINEER",
                    "domain_id": spec.domain_id,
                    "concept_id": spec.id,
                    "question_text": text,
                    "choices_json": json.dumps(choices, ensure_ascii=False),
                    "answer": answer,
                    "explanation": spec.review_note,
                    "difficulty": "medium" if n in {2, 3} else "easy",
                    "source_type": "synthetic_recent_scope",
                    "source_ref": "Q-Net 2026 출제기준 안내 범위에 맞춘 공개 포트폴리오용 합성 훈련 문항입니다. 실제 시험 덤프나 상업 문제집 원문을 복제하지 않았습니다.",
                }
            )
            idx += 1
    return questions


CONCEPTS = [
    (spec.id, "KR_INFO_PROCESSING_ENGINEER", spec.domain_id, spec.name, spec.review_note)
    for spec in CONCEPT_SPECS
]
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
