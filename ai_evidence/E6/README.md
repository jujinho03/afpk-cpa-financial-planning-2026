# E6 — 공부시간·취업 지연 민감도

상태: **IMPORTED_UNREVIEWED** / 책임: 설경민

초기에는 NOT_EXECUTED 양식이었으며, 이번 데모 업로드로 과거 실행을 주장하는 제공 기록을 인수했습니다. 이번 통합에서 외부 AI를 재호출하지 않았고, 원본 제공자 호출·사람 최종 판정을 독립 확인한 상태도 아닙니다.

**번호 충돌:** 바이블 E6는 「공부시간·취업 지연 민감도」, 데모 E6는 「장기 가치만 보고 중간 부족 무시」입니다. 아래 파일을 같은 ID라는 이유로 원래 실험의 완료 증거로 처리하지 않습니다.

## 제공된 기록

- [원출력 JSON](../../apps/demo/ai/evaluations/cpa_experiment_runs.json)의 `srv-E6-1`.
- [프롬프트 정의](../../apps/demo/ai/prompts/verification/cpa_experiments.json)의 `E6`.
- 제공된 tool: `FINOVA 서버 → Gemini API` / provider: `gemini`.
- 제공된 model: `gemini-flash-lite-latest` / ranAt: `2026-11-11T04:51:39.836887+00:00`.
- systemPrompt·prompt·output 전문과 주장(claims)·규칙 힌트(flags)·AI 1차 검토 의견(aiReview)이 포함됩니다.
- `aiReview`는 사람의 최종 승인·기각·권고 수정 기록이 아닙니다.

## 남은 검증

1. 작성자와 실행 경위·원본 로그 등 제공자 실행 증거 확인.
2. 원래 질문의 범위·가정·공식 근거와 응답을 대조.
3. 주장별 동일 입력 독립 계산 및 판정 사유 기록.
4. 검토자·검토 시각·수정 전후 고객 권고를 기록한 뒤 완료 상태 결정.

[전체 증거 인수 상태와 E7·E8](../README.md) / [보안·증거 검토](../../docs/demo/SECURITY_AND_EVIDENCE_REVIEW.md)
