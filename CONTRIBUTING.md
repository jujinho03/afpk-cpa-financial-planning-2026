# 재현과 협업 안내

## 실행 환경

Python 3.10 이상이 필요합니다. 참조 계산·테스트·그림 생성에는 외부 패키지가 필요하지 않습니다. 기존 PDF 생성기 `vendor/v4/build_v4.py`는 이전 버전의 Linux 폰트·경로를 사용하므로 기본 실행 대상이 아닙니다.

```sh
python scripts/reproduce.py
python scripts/render_figures.py
python -m unittest discover -s tests -v
python scripts/check_repository.py
```

계산 수식·가정을 바꾸지 않았다면 JSON·CSV·SVG를 다시 생성해도 diff가 없어야 합니다. Git index에 올린 내용은 `python scripts/check_repository.py --staged`로 검사합니다. 패턴 검사는 완전한 보안 감사가 아닙니다.

## 폴더 안내

```text
.github/               CI·Issue·PR 양식
apps/demo/             기존 데모 소스 인수 대기
docs/bible/            제공받은 기획서 원본
docs/assumptions/      가정 원장
docs/references/       공식 출처·원본 해시
docs/decisions/        한계·운영·공개 기록
docs/demo/             소스 인수·정합성 검토
docs/sprint/           최종 일정 작성을 위한 입력자료
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
| `feature/demo-import` | 원본 데모 제공·인수 | 설경민 제공 / 박동찬 검수 |

작업 전에 origin/main을 확인하고, 팀원이 올린 변경을 덮어쓰지 않습니다. Issue → 브랜치 → PR → 담당 리뷰 → 병합으로 진행합니다. PR에는 목적·기능 전후·검증 결과·가정 변경·AI 영향·검토자를 적습니다. Force push·기존 브랜치 삭제는 별도 승인 없이 하지 않습니다.

## 기존 데모 인수

현재 웹앱 기술 스택과 실행 명령은 미확인입니다. 설경민이 `feature/demo-import`의 `apps/demo/`에 원본 구조·README·lockfile·라이선스를 보존해 업로드한 뒤 확인합니다. 기존 Git 이력이 있다면 보존 방식을 먼저 협의합니다. 바이블의 목표를 실제 구현 기능으로 간주하지 않습니다. [상세 안내](apps/demo/README.md)

## 공개 저장소에 올리지 않는 자료

실제 API 키·토큰·`.env`·고객 금융정보·서명 서류는 제외합니다. 현재 고객 금액은 합성 가정입니다. 공모전 제출용 익명 본문은 공개 협업 기록과 분리합니다. [팀 공통 규칙](AGENTS.md)과 [공개 기록](docs/decisions/PUBLIC_RELEASE.md)을 따릅니다.
