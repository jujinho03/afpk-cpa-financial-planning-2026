# 프런트엔드 인수 검증

기준일: 2026-11-12 KST. 원본 커밋: `bd5a62518f07f4f738a1c1ec69d4c697d7345ccb`.

## 확인한 구현

- React 18·TypeScript·Vite 6·Tailwind 4, React Router·Zustand·Zod·Recharts·React Flow·Motion을 사용하는 SPA입니다.
- 실제 CPA 화면은 `/`, `/client`, `/canvas`, `/copilot`, `/simulator`, `/verification`, `/plan`, `/report`의 8개입니다. `/ai`는 검증 화면으로 이동하고 나머지 미등록 경로는 홈으로 이동합니다. 이전 원본 문서의 `/studio`·`/actions`·`/scenarios` 안내와 구분합니다.
- 브라우저는 `/api/cpa/*`로 Rust API를 호출합니다. 입력값·AI 검토 기록은 브라우저 저장소에 저장하며, 금융 계산은 서버 응답을 표시합니다.
- 정적 코드 대조에서 `defaults`, `analyze`, `explore`, `checkin`, `experiments`, `ai/run`, `ai/screen`, `ask`, `icl`, `runs` 요청의 경로·HTTP 메서드는 백엔드 라우트와 연결됩니다. 실제 응답·렌더링 검증과는 별도입니다.
- `/copilot`의 기본 답변은 규칙 기반입니다. 생성형 AI 옵션은 서버 구성 상태를 확인하고 사용자가 요청할 때만 사용합니다. 이번 인수 과정에서 외부 LLM을 호출하지 않았습니다.

## 수행한 검사

환경: 검증 기준은 Node.js `v22.23.5`(CI는 22), 초기 설치는 npm `11.6.1`입니다. lockfile을 유지한 `npm ci`를 사용했습니다. `.nvmrc`는 22를 지정합니다.

| 검사 | 실제 결과 |
|---|---|
| `npm ci` | 성공, 원본 lockfile 변경 없음 |
| `npm run lint` | 통과 |
| `npm run typecheck` | 통과 |
| 최종 타입·Vite production 빌드 | Node 22에서 통과, 2,495개 모듈 변환·청크 출력 완료 |
| `npm audit --json` | 공식 레지스트리 재조회에서 알려진 취약점 0건. 첫 sandbox 조회는 DNS 제한으로 실패했으며 그 실패를 0건으로 계산하지 않음 |
| `npm test` | 증거 문맥 동일성·입력/출력/허용오차/계산 변경·기존 판정 무효화의 3개 테스트 통과 |
| 브라우저 → API → Rust → 화면 | 8개 라우트의 렌더링, 생활비 변경·재계산·복원, 규칙 상담, 장기 가치, 키 미구성, 인수 기록·사람 판정 0/8, 계획·보고서 표시 확인 |

Windows Node 24.10.0에서는 모듈 변환 이후 네이티브 비정상 종료 코드 `-1073740791`을 확인했습니다. 공식 Node 22를 분석 폴더에 격리 설치하고 SHA-256을 검증한 뒤 동일 소스 빌드에 성공했습니다. 시스템 Node·의존성 버전은 변경하지 않았습니다. Vite의 Zod 주석 annotation 경고는 빌드를 차단하지 않았습니다. 취약점 0건은 보안 전체 검증을 뜻하지 않습니다.

## 원본을 보존한 최소 수정

| 파일 | 변경 이유 |
|---|---|
| `frontend/src/components/cpa/Shell.tsx` | 모든 CPA 화면에 Rust 확장 모형과 루트 Python v4의 가정·기준이 다름을 표시하고 모형 차이 문서로 연결 |
| `frontend/src/pages/cpa/Report.tsx` | 서버 파일에서 불러온 역사적 기록을 이번 세션의 Gemini 호출로 오인하지 않도록 수정 |
| `frontend/src/pages/cpa/Verification.tsx` | 화면·JSON 내보내기에서 인수 기록과 현재 세션 재실행을 구분 |
| `frontend/src/pages/cpa/Copilot.tsx` | API 실패를 ‘호출하지 않음’으로 단정하지 않고 답변 제공 실패로 표시. 대조한 숫자가 0개이면 숫자 일치로 과장하지 않음 |

금융 입력·수식·기본값·차트 값은 변경하지 않았습니다. 추가로 `review-context.ts`, `store.ts`, `verify.ts`와 검증·보고서 화면에서 사람 판정의 적용 문맥을 보존합니다. 원출력·주장·허용오차·실제 엔진 입력/결과가 달라지면 이전 판정은 보존하되 현 증거의 최종 판정으로 세지 않습니다. 새 판정 저장 시 이전 판정은 `reviewHistory`에 남습니다. 기존 문맥 없는 기록도 재검토 대상으로 표시합니다. 이 문맥은 암호학적 출처 증명이 아닙니다.

React 체크리스트에서 조건부 Hook 추가 없음, 파생 상태의 불필요한 Effect 없음, 판정 UI는 문맥별 key로 재초기화, 근거 로딩 중 저장 비활성, JSON 내보내기·보고서의 유효 판정 집계 일치를 확인했습니다. 인수 기록 계산은 고객 편집값이 아닌 기록용 기준 입력으로 고정돼 있음을 화면에 명시합니다.

## 로컬 확인 순서

Rust 서버를 루프백 `127.0.0.1:8080`에 준비한 뒤 프런트 디렉터리에서 실행합니다.

```powershell
$env:FINOVA_API = 'http://127.0.0.1:8080'
npm run dev -- --host 127.0.0.1 --strictPort
```

서버가 준비되기 전에는 연결 실패 안내만 확인할 수 있습니다. 8개 경로의 HTML 반환은 SPA fallback 확인이며 React 렌더링·API 스키마·금융 동작 확인과 구분합니다. 실제 브라우저 검수에서는 기본 계산 로드, 고객 입력 변경·재계산, AI 미구성 안내, 인수 기록/사람 판정 구분, 시뮬레이터·계획·보고서 이동을 확인합니다.
