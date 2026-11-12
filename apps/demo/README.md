# CPA 소득 공백 재무설계 데모

**합격해도 끝나지 않는다** — AFPK 영 플래너 챌린지 2026, B안 가상 고객, 3인 팀의 로컬 데모입니다. 설경민(`k0ng-min`)이 제공한 `import/afpk-demo` 커밋 `bd5a62518f07f4f738a1c1ec69d4c697d7345ccb`를 원본 구조로 인수했습니다.

> **모형 구분:** 이 앱은 별도 가정을 사용하는 **Rust 확장 모형**입니다. 저장소 루트의 Python v4와 동일 수식·동일 결과라고 주장하지 않습니다. 모든 고객·소득·확률·채용 일정은 합성 가정이며, 실제 취업·수익·법정 상환을 보장하지 않습니다.
>
> **검증 상태:** Python 17개, Rust 78개(단위56+API22), 로컬 HTTP 11개 그룹, 프런트 판정 문맥 테스트 3개 및 lint·typecheck가 통과했습니다. **최종 수정본 Vite 빌드도 Node.js 22.23.5에서 통과**했습니다. 외부 AI 호출·배포·영상 렌더는 이번 통합에서 실행하지 않았습니다.

[인수 보고](../../docs/demo/DEMO_INTAKE_REPORT.md) · [Python/바이블 차이](../../docs/demo/DEMO_BIBLE_GAP_ANALYSIS.md) · [보안·증거 검토](../../docs/demo/SECURITY_AND_EVIDENCE_REVIEW.md) · [원본 README](../../docs/demo/original/README.bd5a625.txt)

## 화면과 구현

| 경로 | 기능 |
|---|---|
| `/` | CPA 고객과 소득 공백의 기본 분석 |
| `/client` | 가상 고객·생활비·지원·임금·일정·가정 입력 |
| `/canvas` | 재무 판단의 흐름과 근거 표시 |
| `/copilot` | 계산 근거의 규칙 답변, 선택적 서버 Gemini 응답 |
| `/simulator` | A/B/C/D 경로·민감도·조건 변화 재계산 |
| `/verification` | 제공 AI 원출력·수치 대조·사람 판단 구분 |
| `/plan` | 잔액 점검·전환 규칙·실행 계획 |
| `/report` | 현재 입력·Rust 계산·검토 상태를 정리하는 보고서 |

`/ai`는 `/verification`으로 이동합니다. 원본 일반 FINOVA 문서의 `/scenarios`, `/actions`, `/studio`는 현재 CPA UI의 실제 경로가 아닙니다. 아래 구조·API와 화면 목록은 실제 소스를 기준으로 기록했습니다. 개별 화면의 브라우저 검수·최종 빌드는 [프런트 검증 기록](../../docs/demo/FRONTEND_VERIFICATION.md)을 확인합니다.

## 기술 스택

- 프런트: React 18 · TypeScript · Vite 6 · Tailwind 4 · React Router · Zustand · Zod · Recharts · React Flow · Motion.
- 백엔드: Rust · Axum · Tokio · SQLx(SQLite) · rust_decimal. `/api/cpa/*`에서 계산합니다.
- 입력·사람 검토는 브라우저 저장소, 기존 범용 고객·주제 기능은 SQLite 저장을 사용합니다.
- Gemini는 키가 구성된 경우 서버에서만 호출할 수 있습니다. 분석·캔버스·템플릿 보고서가 모두 생성형 AI 결과인 것은 아닙니다.
- `video/`는 별도 Remotion 프로젝트이며 이번 통합의 필수 웹앱 실행에 필요하지 않습니다.

## 로컬 실행

권장 실행환경은 **Node.js 22 LTS**입니다. 최종 수정본은 Windows의 공식 Node.js 22.23.5 격리 환경에서 typecheck·Vite 빌드를 확인했습니다. Windows Node.js 24.10.0에서는 네이티브 비정상 종료(`-1073740791`)가 있었으므로 Node 24 이상을 검증된 환경으로 일반화하지 않습니다. Windows에서는 Rust stable MSVC와 Visual Studio C++ Build Tools가 필요합니다. 다음 명령은 저장소 루트에서 시작합니다.

```powershell
cd apps/demo/frontend
npm ci
npm run lint
npm run typecheck
npm test
cd ..
```

서버는 **키 없는 합성 데이터 로컬 환경**에서 시작합니다. `.env`는 기본 실행에 필요하지 않습니다. 기존 환경변수·`.env`의 Gemini 키를 의도 없이 사용하지 않도록 확인하고, 이번처럼 외부 AI 없이 검사할 때는 키가 구성되지 않은 별도 환경을 사용합니다.

첫 터미널(현재 위치 `apps/demo`):

```powershell
scripts\development\cargo-msvc.cmd run --locked
```

다른 터미널(저장소 루트):

```powershell
cd apps/demo/frontend
$env:FINOVA_API = 'http://127.0.0.1:8080'
npm run dev -- --host 127.0.0.1 --strictPort
```

브라우저: `http://127.0.0.1:5173`. API: `http://127.0.0.1:8080/api/health`. 개발 프런트가 `/api`를 Rust로 프록시합니다. 백엔드는 통합 시 loopback으로 제한했습니다. 초기 SQLite 파일은 합성 데이터를 담고 Git에서 제외합니다. 외부 배포·터널을 열지 않습니다.

백엔드 Rust 실행환경이 이미 구성됐다면 `backend`에서 `cargo run --locked`도 사용할 수 있습니다. Windows 래퍼는 MSVC linker 환경을 잡고 backend 폴더로 이동합니다. 이번 검증에서 사용한 개인 도구 경로·임시 DB·키는 저장소에 포함하지 않습니다.

## 검사 명령

저장소 루트:

```powershell
python -m unittest discover -s tests -v
python scripts/reproduce.py
python scripts/render_figures.py
python scripts/check_repository.py
python scripts/smoke_demo.py --base-url http://127.0.0.1:8080
```

Rust(위치 `apps/demo`):

```powershell
scripts\development\cargo-msvc.cmd test --locked
```

프런트(위치 `apps/demo/frontend`):

```powershell
npm run lint
npm run typecheck
npm test
npm run build
```

최종 수정본의 typecheck와 Vite 빌드는 Node.js 22.23.5에서 통과했습니다(2,495개 모듈). 소스·의존성을 바꾸지 않고 Node 실행환경을 분리해 확인했습니다. 브라우저에서는 생활비 120→150 변경에 따라 홈 A 경로의 하한 위반 월 10월→8월·말잔액 -595→-1,135가 바뀌고 기본값이 복원되는 것을 확인했습니다. 전체 화면 검수 결과는 별도 검증 기록을 확인합니다. `smoke_demo.py`는 loopback 주소만 받고 활성 AI 키가 없음을 먼저 검사합니다. 테스트 통과는 금융 현실 타당성이나 독립 인간 승인이 아닙니다.

## AI 기록의 출처

[제공 JSON](ai/evaluations/cpa_experiment_runs.json)에 E1~E8 **8개 run·23개 주장**과 시스템 프롬프트·입력·원출력·모델·시각·AI 1차 의견이 들어 있습니다. 이번에 이 자료를 받은 상태는 **IMPORTED_UNREVIEWED**입니다. 실제 제공자 호출 이력을 독립 확인하거나 외부 API를 재호출한 것이 아니며, AI 1차 의견은 사람의 최종 판정이 아닙니다.

바이블과 데모의 E5/E6 질문은 다릅니다. [루트 AI 증거 인덱스](../../ai_evidence/README.md)에 대응 관계와 남은 사람 검토·권고 수정 기준을 기록했습니다. 입력·출력 문맥이 바뀌면 과거 판단을 현재 검증 결과로 그대로 재사용하지 않도록 판정 문맥 검사도 추가했습니다.

## 금융 모형의 차이

루트 Python은 시점별 안전자금 420→375→360, 일반직/CPA 첫 급여 230/290, 임금 성장과 초기 현금을 포함한 할인 순현금흐름을 사용합니다. Rust 데모는 고정 안전자금 360, 임금 270/320/410, 다른 취업 시점과 잔액 기반 D 전환, 초기 현금을 제외한 할인 지표를 사용합니다. 기본 가중치도 다릅니다.

단위는 앱/Rust가 **원**, 루트 Python 표는 **만원**입니다. 두 결과를 숫자만 직접 비교하지 않습니다. 상세 입력·수식 차이는 [차이 분석](../../docs/demo/DEMO_BIBLE_GAP_ANALYSIS.md)을 참조합니다. 이번 통합에서 수치를 맞추기 위해 금융 계산을 변경하지 않았습니다. ICL 보조 계산은 실제 통지·이자·기납부를 모두 반영한 확정 의무상환 계산이 아닙니다.

## 원본 보존과 알려진 경계

- [원본 매니페스트](../../docs/references/DEMO_IMPORT_MANIFEST.json) 242개 경로·해시와 업로드 커밋을 보존합니다. 옛 README는 별도 보관했습니다.
- 필수 프롬프트 3개는 ignore로 업로드에서 빠졌으므로 통합 자료로 새로 보완했습니다. 원저작자 파일과 동일한 바이트라고 주장하지 않습니다.
- 개발용 기본 관리자 토큰·인증 없는 편집/API 경로가 있으므로 합성 데이터 loopback 데모 범위를 유지합니다. 운영 공개에 필요한 인증·비용 통제는 별도 설계가 필요합니다.
- 실제 키·토큰·고객 개인정보·서명 서류를 올리지 않습니다. `.env.example`에는 변수 이름과 빈/예제 값만 둡니다.
- 기존 PNG는 이전 FINOVA 화면이고, 영상 스냅샷·내레이션도 현재 Python 결과의 독립 증거가 아닙니다. 새 화면 검수와 구분합니다.
- Pretendard·Outfit의 OFL 고지는 [글꼴 안내](video/public/fonts/FONTS.md)에 연결했습니다. 프로젝트 전체에 새 오픈소스 라이선스를 임의 부여하지 않았습니다.
- 외부 유료 호출, 음성 재생성, 영상 렌더, 서비스 배포, 공식 참가작 자동 완성은 이번 인수에서 수행하지 않았습니다.

## 팀과 후속 검토

주진호(`jujinho03`)는 고객 가정·재무 판단·본문, 설경민(`k0ng-min`)은 원본 데모·AI 증거·기술서, 박동찬(`feeljis131`)은 통합·실행환경·테스트·CI를 담당합니다. 자동 검사와 코드 검토를 팀원의 독립 인간 승인으로 표기하지 않습니다. 통합 PR은 실제 필수 CI와 검수 기록을 제공하며, 최종 모형 기준 결정과 AI 기록의 인간 판정은 후속 과제입니다.
