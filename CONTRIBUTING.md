# 재현과 협업 안내

준비팩·점검 보고·실제 제출 파일의 차이와 commit/push/pull/merge 순서는 [제출 자료와 Git 관리 방법](docs/SUBMISSION_WORKFLOW.md)을 참고합니다. 비공개 원고와 서명은 Git 동기화 대상이 아닙니다.

## 실행 환경

Python 3.10 이상이 필요합니다. 참조 계산·테스트·그림 생성에는 외부 패키지가 필요하지 않습니다. 기존 PDF 생성기 `vendor/v4/build_v4.py`는 이전 버전의 Linux 폰트·경로를 사용하므로 기본 실행 대상이 아닙니다.

```sh
python scripts/reproduce.py
python scripts/audit_ai_claims.py --check
python scripts/render_figures.py
python -m unittest discover -s tests -v
python scripts/check_repository.py
```

계산 수식·가정을 바꾸지 않았다면 JSON·CSV·SVG를 다시 생성해도 diff가 없어야 합니다. Git index에 올린 내용은 `python scripts/check_repository.py --staged`로 검사합니다. 패턴 검사는 완전한 보안 감사가 아닙니다.

인수한 AI 주장 대조는 [별도 검산 안내](ai_evidence/CLAIM_AUDIT.md)를 따릅니다. 원출력 해시를 고정하고 같은 입력의10개월만 CSV와 비교합니다. 검토 주석과 계산 결과를 수정했다면 `python scripts/audit_ai_claims.py --write` 후 변경 근거를 검토합니다. 결과 재현은 사람의 금융판정·최종 승인과 구분합니다.

## 폴더 안내

```text
.github/               CI·Issue·PR 양식
apps/demo/             React/Rust 기존 데모와 별도 모형
docs/bible/            제공받은 기획서 원본
docs/assumptions/      가정 원장
docs/references/       공식 출처·원본 해시
docs/decisions/        모형 한계·공개 범위 기록
docs/demo/             소스 인수·정합성 검토
docs/archive/          지난 일정 입력자료·저장소 초기 설정 기록(현재 기준 아님)
src/afpk_cpa/financial/ v4 참조 계산
tests/                 회귀·경계조건·재현 검사
ai_evidence/           E1~E6 실제 실험 기록 위치
outputs/tables/        모형에서 생성한 JSON·CSV
outputs/figures/       JSON·CSV에서 생성한 SVG
vendor/v4/             사용자 제공 ZIP 원본 3개
reports/               본문·AI 부록의 초안·제출 관리
scripts/               재현·그림 생성·저장소 검사
```

## 작업 브랜치

| 브랜치 | 목적 | 담당 |
|---|---|---|
| `main` | 검증된 공통 기준 | 주진호 |
| `feature/financial-model` | 가정·재무모형 | 주진호 |
| `feature/ai-evaluation` | 실제 E1~E6 증거·AI 부록 | 설경민 |
| `feature/demo-integration` | 실행환경·모형 연결 | 박동찬 |
| `import/afpk-demo` | 실제 원본 데모 업로드·보존 | 설경민 제공 / 박동찬 검수 |
| `integration/demo-verified` | 원본 위의 실행·증거·문서 보완 | 공동 인수 검수 |

작업 전에 origin/main을 확인하고, 팀원이 올린 변경을 덮어쓰지 않습니다. Issue → 브랜치 → PR → 담당 리뷰 → 병합으로 진행합니다. PR에는 목적·기능 전후·검증 결과·가정 변경·AI 영향·검토자를 적습니다. Force push·기존 브랜치 삭제는 별도 승인 없이 하지 않습니다.

## 기존 데모 인수

원본 `import/afpk-demo`의 `bd5a625`를 이력과 함께 인수했습니다. 기술 스택은 React·TypeScript·Vite 및 Rust·Axum·SQLite입니다. 원본 README는 `docs/demo/original/README.bd5a625.txt`, 원본 해시는 `docs/references/DEMO_IMPORT_MANIFEST.json`에 보존합니다. [실행 안내](apps/demo/README.md)와 [정합성 차이](docs/demo/DEMO_BIBLE_GAP_ANALYSIS.md)를 먼저 확인합니다.

소스 동작을 수정할 때 원저작자의 화면·기능·금융 가정을 보존합니다. 새로운 금융 기준을 합의하지 않은 상태에서 Python 수치에 맞추지 않습니다. 외부 AI 호출과 영상·음성 생성은 이번 병합 검증에 포함하지 않습니다. CI는 frontend 린트·타입·빌드, Rust 단위/API·HTTP smoke, 루트 참조 검사를 모두 실행합니다. 기존 필수 검사 두 개는 데모 검사에도 의존하므로 데모 실패를 통과시키지 않습니다.

## 공개 저장소에 올리지 않는 자료

실제 API 키·토큰·`.env`·고객 금융정보·서명 서류는 제외합니다. 현재 고객 금액은 합성 가정입니다. 공모전 제출용 익명 본문은 공개 협업 기록과 분리합니다. [팀 공통 규칙](AGENTS.md)과 [공개 기록](docs/decisions/PUBLIC_RELEASE.md)을 따릅니다.
