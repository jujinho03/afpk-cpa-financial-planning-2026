# 재현 가능한 시각 자료

| 파일 | 내용 | 데이터 |
|---|---|---|
| `decision-overview.svg` | 18개월 유동성·60개월 비교·재현 근거 | `model_summary.json`, CSV 행 수 |
| `liquidity-paths.svg` | A/U·B/U·C/U·D/U 월말 잔액과 안전자금 하한 | `monthly_cashflows.csv` |
| `financial-value.svg` | 네 전략의 기본 가중 현금흐름 현가 | `model_summary.json` |

`python scripts/render_figures.py`로 표준 라이브러리만 사용해 생성합니다. 반응형 SVG에 제목·설명과 가상 조건을 포함했습니다. 음수 잔액은 미충당액으로 표시하며 0에서 자르지 않습니다. 금융 계산은 그림 코드에서 중복 구현하지 않습니다.

이 시각 자료는 심사위원용 공개 README를 위한 새 산출물입니다. 기존 바이블 PDF를 다시 생성한 결과는 아닙니다. `vendor/v4/build_v4.py`는 이전 버전 PDF 생성기이므로 현재 바이블 PDF 재현 완료로 취급하지 않습니다.
