# 기존 데모 기능 인벤토리

기준일: 2026-11-12 KST. 인수 원본: 설경민, `import/afpk-demo` / `bd5a62518f07f4f738a1c1ec69d4c697d7345ccb`.

소스 업로드 대기 상태를 종료하고 실제 코드를 조사했습니다. 아래 `SOURCE_CHECKED`는 소스 구현 확인이며 실행 검증 완료를 뜻하지 않습니다. 설치·빌드·API·브라우저의 최신 결과는 [인수 보고](../demo/DEMO_INTAKE_REPORT.md)에 기록합니다.

## 페이지와 구현 근거

라우터: [cpa.tsx](../../apps/demo/frontend/src/app/router/cpa.tsx). 프런트는 React 18·TypeScript·Vite, 서버는 Rust·Axum·Tokio·SQLx/SQLite입니다.

| 경로 | 확인한 구현 | 주요 근거 | 남은 확인 / 책임 |
|---|---|---|---|
| `/` | 18개월·60개월·전환 신호의 요약 | `frontend/src/pages/cpa/Home.tsx` | API 입력·표시·프로필 안내 / 박동찬·주진호 |
| `/client` | 고객 입력, 수정 전후 미리보기, ICL 보조 계산 | `Client.tsx`, `/api/cpa/defaults`, `/api/cpa/icl` | 저장·초기화·미확인 연도 flag·ICL 적용 범위 / 박동찬·주진호 |
| `/canvas` | React Flow로 고객→분석→제안 근거 표시 | `Canvas.tsx` | 규칙 결과와 LLM 출처 라벨 구분 / 설경민·박동찬 |
| `/copilot` | 규칙 답변, 선택적 서버 Gemini 호출 | `Copilot.tsx`, `/api/cpa/ask` | 키 없음 경로·실패 안내·수치 대조 / 설경민·박동찬 |
| `/simulator` | 18개월·장기 가치·지연 팬·탐색 분석 | `Simulator.tsx`, `/api/cpa/analyze`, `/api/cpa/explore` | 입력 변경·차트·미완비 입력·별도 Rust 가정 표시 / 주진호·박동찬 |
| `/verification` | 수입 원출력·주장 대조·AI 의견·사람 판정 | `Verification.tsx`, `features/cpa/verify.ts`, `/api/cpa/runs` | 인간 판정·E5/E6 의미 매핑 / 설경민·주진호 |
| `/plan` | 전환 규칙·월별 점검·재계산 | `Plan.tsx`, `/api/cpa/checkin` | 브라우저 기록 유지·재계산의 가정 / 박동찬·주진호 |
| `/report` | 입력·엔진·AI 검증·실행 계획 템플릿과 인쇄 | `Report.tsx` | 실제 인쇄 출력·상태·출처 일치. 공식 참가작 대체 아님 / 주진호·박동찬 |

`/ai`는 검증 페이지로, 미등록 경로는 홈으로 이동합니다. 원본 README의 이전 범용 화면 `/scenarios`, `/actions`, `/studio` 등은 현재 8개 라우트의 구현 근거로 사용하지 않습니다.

## 기능·데이터 출처

| ID | 기능 | 확인 상태 | 데이터 출처와 한계 |
|---|---|---|---|
| DEMO-01 | 화면·라우팅 | `SOURCE_CHECKED` | 위 8개 React 페이지. 스크린샷은 과거 자료일 수 있음 |
| DEMO-02 | 고객 입력·가정 | `SOURCE_CHECKED` | Rust `CpaInputs` 기본값·검증, 브라우저 입력 localStorage |
| DEMO-03 | 자산·부채·보증금·ICL | `SOURCE_CHECKED` | Rust 계산. ICL의 실제 통지·잔액·이자 전체 검증은 아님 |
| DEMO-04 | A/B/C/D·결과 상태 | `DIFF_FOUND` | Rust `Unresolved`, `PassPlaced`, `PassUnplaced`, `Fail`; Python과 경로 정의가 다름 |
| DEMO-05 | 18개월 현금흐름 | `DIFF_FOUND` | Rust 원 단위 API 결과. 고정 360 하한·월중 최저를 사용 |
| DEMO-06 | 60개월 가치·민감도 | `DIFF_FOUND` | Rust는 초기 현금 제외·월 r/12; Python 지표와 직접 비교 불가 |
| DEMO-07 | Python 연결 | `NOT_IMPLEMENTED` | 현재 데모는 Rust 계산 API. Python 자동 호출·동일 입력 대조 구현을 발견하지 못함 |
| DEMO-08 | AI 상담·실행 | `SOURCE_CHECKED` | 서버 Gemini 선택 호출. 키 없는 실행과 기록 파일 열람은 구분. 이번 통합에서 외부 호출 0 |
| DEMO-09 | AI 원출력 증거 | `IMPORTED_UNREVIEWED` | E1~E8 8개 run·23개 주장 인수. AI 1차 의견과 인간 최종 판정 구분 |
| DEMO-10 | 보고서 | `SOURCE_CHECKED` | 입력·Rust·템플릿·검증 상태 조립, 브라우저 인쇄. 최종 DOCX/HWP 미작성 |
| DEMO-11 | 저장·환경 | `SOURCE_CHECKED` | SQLite·localStorage·환경변수, 값은 `.env`에만. 실제 비밀값을 올리지 않음 |
| DEMO-12 | 실행·테스트 | `RUNTIME_CHECK` | [인수 보고](../demo/DEMO_INTAKE_REPORT.md)의 실제 명령·결과 참조 |

## 기존 자산을 활용하는 작업 분류

- **재사용:** 고객·시뮬레이션·검증·계획·보고서의 화면과 Rust 엔진, 잠금파일·테스트·실험 원출력 구조.
- **보완:** 현재/과거 문서 구분, 실행환경, 모형 프로필·숫자 출처 안내, 인간 판정과 공식 근거, 실제 실행·회귀 검사.
- **별도 결정:** 두 모형의 단일화나 Python 어댑터. 수치 하드코딩으로 정렬하지 않으며 금융 변경 승인 전 구현하지 않음.
- **후순위:** 선택 UI·영상·추가 AI 기능. P0 본문과 실제 검증을 지연시키면 제외.

상세 계산 차이는 [바이블 차이 분석](../demo/DEMO_BIBLE_GAP_ANALYSIS.md)을, 작업 담당·난이도·대체안은 [우선순위](DEVELOPMENT_PRIORITIES.md)를 참조합니다.
