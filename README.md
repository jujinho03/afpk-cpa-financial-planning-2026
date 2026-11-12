# 합격해도 끝나지 않는다

CPA 2차 유예생의 합격·수습·첫 급여 사이 소득 공백을 다루는 조건부 재무설계 프로젝트입니다. AFPK 영 플래너 챌린지 2026 B안 가상 고객 사례이며, 재무설계 60점·AI 활용 및 비판적 검증 40점에 대응합니다. 제출 마감은 **2026-11-16 23:59 KST**입니다.

## 현재 상태

- 사용자 제공 바이블 PDF/Markdown과 v4 원본 소스 인수 완료.
- Python 참조 구현, 12개 경로·720행 재현 표, 회귀·경계조건 테스트 준비.
- **설경민의 기존 데모는 저장소 생성 후 업로드 예정입니다. 현재 소스·기술 스택·기능·실행 명령은 미확인입니다.**
- 웹앱·API·AI 실험·배포가 완료됐다는 의미가 아닙니다. 가상 수치는 실제 급여·개인 합격확률 예측이 아닙니다.
- 원격 구축·초대·CI 상태는 [GitHub 인수 기록](docs/decisions/GITHUB_HANDOFF.md)을 확인합니다.

## 팀과 책임

| 담당 | 역할 | GitHub |
|---|---|---|
| 주진호 | 팀장·데이터사이언티스트 / 가정·분석·본문·최종 권고 | `jujinho03` |
| 설경민 | AI 전문가·테크 리더 / 기존 데모 작성·AI 실험·기술서 | `k0ng-min` (Verimod 출처 확인) |
| 박동찬 | 풀스택 / 원본 데모 통합·모형 연결·테스트·CI·문서 | `feeljis131` |

## 문제와 기준 자료

고객은 가용현금 1,400만 원, 보증금 1,000만 원, ICL 1,600만 원, 월 필수생활비 120만 원의 **가상 고객**입니다. 18개월 안전자금·미충당액을 먼저 검사하고 60개월 할인 순현금흐름을 비교합니다.

- [프로젝트 바이블](docs/bible/AFPK_CPA_아이디어_기획서.md) / [PDF](docs/bible/AFPK_CPA_아이디어_기획서.pdf)
- [가정 원장](docs/assumptions/BASELINE.md) / [원본 SHA-256](docs/references/SOURCE_MANIFEST.json)
- [모형의 알려진 한계](docs/decisions/KNOWN_LIMITATIONS.md)
- [공식 출처](docs/references/README.md): 본 저장소의 가정·코드는 공식 자료를 대체하지 않습니다.

## 구조

```text
.github/                 CI, Issue·PR 템플릿
apps/demo/               기존 데모 업로드 대기 및 인수 안내
docs/bible/              사용자 제공 바이블 원본
docs/assumptions/        가정 원장
docs/references/         출처·원본 해시
docs/decisions/          변경 결정·모형 한계·GitHub 인수 상태
docs/demo/               데모 인수 보고·바이블 차이 분석
docs/sprint/             3인·3일 계획의 입력자료 (최종 PDF 아님)
src/afpk_cpa/financial/  수식·가정을 유지한 Python 참조 모형
src/afpk_cpa/scenarios/  별도 시나리오 엔진 없음
src/afpk_cpa/evaluation/ E1~E6 판정 설계 연결 위치
tests/                  재현·회귀·경계조건 검증
vendor/v4/              ZIP에서 가져온 원본 3개 파일
ai_evidence/E1~E6/      실험별 기록 양식, 실제 실행 전
reports/                초안·제출물 인수 안내
outputs/                재현 표·그림 위치
scripts/                재현·저장소 검사
```

## 로컬 실행: 확인한 Python 경로

Python 3.10 이상이 필요합니다. 참조 모형 실행·테스트에는 외부 패키지가 필요하지 않습니다.

```powershell
git clone https://github.com/jujinho03/afpk-cpa-financial-planning-2026.git
cd afpk-cpa-financial-planning-2026
python scripts/reproduce.py
python -m unittest discover -s tests -v
python scripts/check_repository.py
```

클론 명령은 저장소 접근 권한이 있는 계정으로 사용합니다. 이 작업에서는 로컬 재현·테스트 명령을 실제 실행했습니다. `outputs/tables/model_summary.json`, `monthly_cashflows.csv`가 생성됩니다. 월 단위 현금흐름이며 월중 지급일까지 검증한 결과는 아닙니다.

기본 가중 지표(단위 만원)는 A 5,259.216 / B 6,062.210 / C 6,716.700 / D 5,853.492입니다. 초기 현금을 포함한 60개월 현금흐름 현가이며 순자산·확정 수익이 아닙니다. 실제 ICL 법정 의무상환액도 아직 구현하지 않았습니다.

## 기존 데모 업로드와 실행

새 데모를 만들지 않습니다. 설경민이 아래 순서로 기존 소스를 제공합니다.

1. 저장소 초대를 수락하고 `feature/demo-import`를 체크아웃합니다.
2. [인수 안내](apps/demo/README.md)에 따라 기존 프로젝트를 `apps/demo/` 하위에 보존합니다. `.env`, 키, 개인정보, `node_modules`, 가상환경은 제외합니다.
3. 원본 저장소가 있으면 Git 이력 보존 방식을 먼저 협의합니다. 원저작자·원본 커밋·실행 방법을 기록합니다.
4. 실제 소스가 올라온 후 PR을 만들고 설경민·박동찬이 원본 보존·실행·빌드·AI 연결을 확인합니다.
5. 확인한 패키지 관리자·설치·실행·빌드 명령을 여기에 추가합니다.

**데모의 실행 명령은 아직 알 수 없습니다.** 기술 스택을 추측해 `npm run dev` 등을 정상 명령처럼 제시하지 않습니다. [인수 보고](docs/demo/DEMO_INTAKE_REPORT.md), [차이 분석](docs/demo/DEMO_BIBLE_GAP_ANALYSIS.md), [기능 목록](docs/sprint/DEMO_FEATURE_INVENTORY.md)을 소스 인수 후 갱신합니다.

## AI 검증

E1 집단률 / E2 합격과 급여 / E3 면제 규정 / E4 ICL / E5 첫 지급일 / E6 공부시간·구직 지연을 점검합니다. `ai_evidence/`에는 기록 구조만 있습니다. 프롬프트·모델·시각·실제 원출력·독립 검산·권고 전후를 확보해야 실적으로 인정합니다. Python 테스트는 외부 AI 실험을 대체하지 않습니다.

## 협업

| 브랜치 | 사용 목적 | 책임 |
|---|---|---|
| `main` | 검증된 공통 기준 | 주진호 최종 승인 |
| `feature/financial-model` | 재무모형·가정 | 주진호 |
| `feature/ai-evaluation` | AI 실험·부록 | 설경민 |
| `feature/demo-integration` | 데모 연동·환경 | 박동찬 |
| `feature/demo-import` | 기존 데모 원본 인수 | 설경민 제공 / 박동찬 검수 |

모든 변경은 Issue → 작업 브랜치 → PR → 담당 리뷰 → 병합 순서로 진행합니다. 본 초기 구축의 최초 커밋은 공통 기반을 위한 예외입니다. `.github/pull_request_template.md`를 사용하고 가정 변경·AI 영향·실행 결과를 기록합니다. 원격 보호 규칙의 실제 강제 여부는 인수 기록을 확인합니다. 새 기능이 없는 빈 PR은 만들지 않습니다.

## 제출물과 남은 작업

필수 참가작은 본문+AI 기술서가 합쳐진 DOCX/HWP 1개, 전원 서명 확인서는 별도입니다. 내부 바이블 PDF는 공식 참가작이 아닙니다. 서명 서류는 이 저장소에 업로드하지 않습니다.

다음 작업은 기존 데모 인수, 실제 스택·기능·보안·계산 출처 조사, 정합성 검증, ICL·급여 근거 확보, 실제 E1~E6 실행입니다. 우선순위는 **P0 본문·AI 부록 → P1 정확성·검증·연동 → P2 UI**입니다. 이번 단계에서는 배포나 최종 3일 실행계획 PDF를 만들지 않습니다.
