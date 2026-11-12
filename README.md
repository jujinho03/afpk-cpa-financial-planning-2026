# 합격해도 끝나지 않는다

**합격 발표와 첫 급여 사이, 고객의 현금은 버틸 수 있을까?**

CPA 2차 유예생의 소득 공백을 **18개월 유동성 → 60개월 조건부 가치 → 고객의 선택**으로 연결하는 AI 보조 재무설계 연구입니다.

[![검증 워크플로](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/actions/workflows/ci.yml/badge.svg?branch=main&event=push)](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/actions/workflows/ci.yml)
![Python 3.10 이상](https://img.shields.io/badge/Python-3.10%2B-356D94)
![가상 고객 사례](https://img.shields.io/badge/Case-Synthetic-197A72)

![18개월 안전자금 검사와 60개월 조건부 가치 비교의 의사결정 구조](outputs/figures/decision-overview.svg)

**[심사위원용 3분 안내](docs/JUDGES_GUIDE.md) · [분석 결과 JSON](outputs/tables/model_summary.json) · [프로젝트 기획서 PDF](docs/bible/AFPK_CPA_아이디어_기획서.pdf) · [재현·기여 안내](CONTRIBUTING.md)**

> AFPK 영 플래너 챌린지 2026 · B안 가상 고객 사례. 현재 공개본은 **계산을 재현할 수 있는 연구·협업 저장소**입니다. 외부 AI 검증 실험은 준비 중이며, 기존 데모는 원본 업로드 대기입니다. 이 저장소는 공식 DOCX/HWP 참가작을 대체하지 않습니다.

## 왜 이 문제인가

가상 고객 김유예는 현금 **1,400만 원**, 월 필수생활비 **120만 원**, 학자금대출 **1,600만 원**을 보유한 CPA 2차 유예생입니다. 가족 지원은 단계적으로 종료됩니다. 현재 1차 합격에 따른 마지막 유예 응시 기회를 활용하려면 시험 전 생활비뿐 아니라 **합격 이후 수습·채용·첫 지급까지의 대기기간**도 감당해야 합니다.

이 프로젝트는 세 질문에 답합니다.

1. **언제 위험해지는가?** 월별 안전자금 하한과 실제 미충당액 발생을 따로 찾습니다.
2. **어떤 대안이 있는가?** 전업·근로 병행·취업 전환·조건부 전환을 같은 기간과 단위로 비교합니다.
3. **무엇이 바뀌면 권고도 바뀌는가?** 급여 지연과 공부시간 손실을 드러내고, 최종 선택은 고객의 선호와 실행 가능성에 연결합니다.

## 먼저 확인한 결과

**아래 숫자는 가상 임금·일정·가중치를 넣어 실제 코드로 계산한 값입니다. 개인의 합격·취업 가능성을 추정한 결과가 아닙니다.**

| 전략 | 행동 | 18개월 안전자금 검사 | 60개월 가중 현금흐름 현가 |
|---|---|---|---:|
| **A · 전업 수험** | 소득 없이 시험 준비 후 결과별 구직 | 세 결과 상태 모두 2027.10 하한 위반 | 5,259.2만 원 |
| **B · 근로 병행** | 시간제 근로 후 결과별 정규직 전환 | 기본 가정의 세 상태에서 통과 | 6,062.2만 원 |
| **C · 취업 전환** | 2027.04 첫 일반직 급여 가정 | 기본 가정에서 통과 | **6,716.7만 원** |
| **D · 조건부 전환** | 시험 후 시간제 → 정규직 | 기본 가정에서 통과, 지연에 취약 | 5,853.5만 원 |

**해석:** 현재 가정에서는 C의 장기 지표가 가장 높습니다. B는 약 **654.5만 원의 지표 차이**와 공부시간 감소를 설명한 뒤, 고객이 유예 응시 기회를 중시할 때 검토할 대안입니다. A는 안전자금 기준에서 제외하며, D는 실제 급여 일정이 지켜지는지 확인해야 합니다.

![가상 가중치를 적용한 전략별 60개월 현금흐름 현재가치 비교](outputs/figures/financial-value.svg)

지표는 **초기 현금 + 60개월 순현금흐름의 현재가치**입니다. 순자산·투자수익·확정 급여가 아닙니다. p=0.60, q=0.70, B의 Δp=0.10은 예시 가중치이며 집단 합격률에서 개인화하지 않았습니다. [가정 전체 보기](docs/assumptions/BASELINE.md)

## 잔액이 회복돼도, 중간의 위험은 사라지지 않는다

![합격·수습 미확보 U 경로의 18개월 잔액과 최소 안전자금 하한](outputs/figures/liquidity-paths.svg)

- **A/U:** 2027.10 잔액 285만 원으로 안전자금 360만 원을 밑돕니다. 미충당액이 처음 생기는 시점은 그보다 늦은 **2028.01**입니다.
- **D/U:** 정규직 첫 급여가 1개월 늦으면 하한 위 여유가 **5만 원**, 2개월 늦으면 2028.03에 하한을 **35만 원** 밑돕니다.
- **C:** 첫 급여를 3개월 늦추면 장기 지표가 **5,968.6만 원**으로 낮아져 B의 기본값 아래로 내려갑니다.

이는 **현재 가정을 유지한 시나리오 비교**입니다. 채용 보장이나 안전 확률이 아닙니다. 월말 계산은 월중의 월세·급여 지급 순서까지 확인하지 않습니다. [수치와 한계 읽기](docs/JUDGES_GUIDE.md)

## AI의 가치는 ‘답변’보다 ‘검증 가능한 수정’에 있다

AI는 정보 누락·실패 시나리오·권고의 반례·고객 설명을 제안하고, 인간은 공식 자료와 독립 계산으로 판단합니다. 목표는 **AI 원출력 → 근거 대조 → 재계산 → 고객 권고 변경**을 추적하는 것입니다.

| 현재 확보한 것 | 아직 확보하지 않은 것 |
|---|---|
| 12개 경로·720행 계산 결과와 회귀·경계조건 테스트 | E1~E6 실제 외부 AI 원출력·판정·수정 이력 |
| 원본 파일 해시, 가정 원장, 알려진 결함 기록 | 법정 ICL 상환·실제 급여·채용기간의 현실성 검증 |
| Linux·Windows CI와 재현 가능한 그림 | 기존 데모 소스·실행·빌드·AI 연결 검수 |

[AI 실험 증거 구조](ai_evidence/README.md) · [알려진 모형 한계](docs/decisions/KNOWN_LIMITATIONS.md) · [데모 인수 상태](docs/demo/DEMO_INTAKE_REPORT.md)

## 직접 재현하기

참조 모형·테스트·SVG 생성은 **Python 표준 라이브러리만** 사용합니다. Python 3.10 이상에서 다음 순서로 실행합니다.

```sh
git clone https://github.com/jujinho03/afpk-cpa-financial-planning-2026.git
cd afpk-cpa-financial-planning-2026
python scripts/reproduce.py
python scripts/render_figures.py
python -m unittest discover -s tests -v
python scripts/check_repository.py
```

`outputs/tables/`의 JSON·CSV에서 그림을 생성합니다. CI는 테스트와 원본 해시를 검사하고 표·그림 재생성 후 Git diff가 없는지도 확인합니다. 알려진 결함을 재현하는 테스트는 **결함 해결 또는 금융 타당성 승인**을 의미하지 않습니다.

## 근거를 따라가는 저장소

| 확인할 것 | 위치 |
|---|---|
| 문제·고객·재무설계 6단계 | [기획서 Markdown](docs/bible/AFPK_CPA_아이디어_기획서.md) / [PDF](docs/bible/AFPK_CPA_아이디어_기획서.pdf) |
| 가정·공식 출처·원본 동일성 | [가정 원장](docs/assumptions/BASELINE.md) / [출처](docs/references/README.md) / [SHA-256](docs/references/SOURCE_MANIFEST.json) |
| 계산 코드·월별 근거 | [참조 구현](src/afpk_cpa/financial/model_v4.py) / [720행 CSV](outputs/tables/monthly_cashflows.csv) |
| 한계·남은 작업 | [한계 원장](docs/decisions/KNOWN_LIMITATIONS.md) / [Issues](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/issues) |
| 실행·개발·데모 업로드 | [기여 안내](CONTRIBUTING.md) / [데모 인수 안내](apps/demo/README.md) |

## 팀

| 담당 | 책임 |
|---|---|
| [주진호 · jujinho03](https://github.com/jujinho03) | 팀장·데이터사이언티스트 / 고객 가정·재무분석·본문·최종 권고 |
| [설경민 · k0ng-min](https://github.com/k0ng-min) | AI 전문가·테크 리더 / 기존 데모·AI 검증·기술서 |
| [박동찬 · feeljis131](https://github.com/feeljis131) | 풀스택 / 데모 통합·환경·테스트·CI·문서 빌드 |

**제출 기준:** 2026-11-16 23:59 KST. 공식 참가작은 재무설계 본문+AI 기술서 DOCX/HWP 1개이며, 서명 확인서는 별도입니다. 공개 저장소와 제출용 익명 참가작은 구분합니다. [공개 범위·검토 기록](docs/decisions/PUBLIC_RELEASE.md)
