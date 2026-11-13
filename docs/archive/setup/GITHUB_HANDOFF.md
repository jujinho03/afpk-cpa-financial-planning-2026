# GitHub 인수 기록

> 아래는 초기 Private 구축 당시의 보존 기록입니다. 현재 저장소는 Public이며 main 보호가 적용돼 있습니다. 공개 범위와 후속 보호 설정은 [공개 전환 기록](../../decisions/PUBLIC_RELEASE.md)을 확인합니다. 이후 실제 데모 `import/afpk-demo`의 `bd5a625`를 인수했고, [통합 PR #8](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/pull/8)에 실제 실행·브라우저 검수·원격 CI 결과를 연결했습니다. 최신 기능 상태는 [인수 보고](../../demo/DEMO_INTAKE_REPORT.md)를 참조합니다.

기준일: 2026-11-12 KST. 아래는 GitHub API와 실제 push 결과로 확인한 인수 상태입니다. 팀원 수락은 이후 바뀔 수 있습니다.

| 항목 | 상태 |
|---|---|
| Repository | https://github.com/jujinho03/afpk-cpa-financial-planning-2026 |
| Owner | `jujinho03`, 연결 프로필과 브라우저 소유자 확인 |
| Visibility | 브라우저 생성 결과 `Private` 확인 |
| Default branch | `main`, GitHub API 확인 |
| 초기 commit / push | `7fdfa401e4115ac57667cce91f4fbeb73700af02`, origin/main 최초 push 성공 |
| 협업 브랜치 | `feature/financial-model`, `feature/ai-evaluation`, `feature/demo-integration`, `feature/demo-import` 생성·push 확인 |
| 설경민 계정 | `k0ng-min`, Verimod README의 설경민 데모 출처로 확인 |
| 박동찬 계정 | `feeljis131`, 사용자 직접 제공 |
| 팀원 초대 | `k0ng-min`·`feeljis131` 두 계정 실재 확인, write 초대 발송 성공(201), 인수 확인 시 수락 대기. admin 권한 아님 |
| GitHub Actions | 초기 구현 커밋의 main 및 네 feature push 실행 모두 success. Linux·Windows Python 3.11 검사 |
| main 보호 강제 | 적용 시도했으나 403: 현재 Private 저장소에는 GitHub Pro 필요. 강제 설정 **미완료**, 유료 전환·Public 전환 없음 |
| 데모 통합 PR | 소스 없음으로 아직 생성하지 않음 |

설경민의 계정 근거: https://github.com/jujinho03/verimod 의 README에서 기존 설경민 디자인 출처를 `k0ng-min/verimod_demo`로 명시합니다. 이 저장소를 AFPK 데모로 간주하거나 복사하지 않습니다.

사용자 후속 지시: 프로젝트 생성 후 설경민이 기존 AFPK 데모를 업로드할 예정입니다. 원본 코드 분석·실행·빌드·차이 검증은 해당 업로드 후에만 완료할 수 있습니다.

## 검증 증거

- 초기 main CI: https://github.com/jujinho03/afpk-cpa-financial-planning-2026/actions/runs/43179205967 — success, 초기 구현 커밋 기준.
- 데모 업로드 브랜치 CI: https://github.com/jujinho03/afpk-cpa-financial-planning-2026/actions/runs/43179336072 — success, 아직 데모 소스는 없음.
- 로컬: 13개 테스트 통과, 12개 경로·720행 재생성 후 표 diff 없음, 원본 5개 SHA-256 일치, tracked working tree 및 초기 Git index의 제한된 비밀정보 패턴·상대 링크 검사 통과.
- 알려진 v4 결함은 보존·특성화했으며 테스트 통과가 현실 타당성 승인 또는 결함 수정은 아닙니다.
- 이후 문서 상태 갱신 커밋의 최신 CI는 Actions에서 해당 SHA를 확인합니다.

## 실제 작업 Issue

1. [기존 데모 원본 업로드·인수 PR](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/issues/1)
2. [데모 실행·빌드·정합성 검증](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/issues/2)
3. [실제 E1~E6 증거](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/issues/3)
4. [가정·ICL·v4 한계 검토](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/issues/4)
5. [필수 참가작·제출 QA 입력](https://github.com/jujinho03/afpk-cpa-financial-planning-2026/issues/5)

## main 운영 대안

사용자가 두 팀원의 write 초대와 PR 1명 승인·CI 통과 보호를 명시적으로 승인한 후 적용을 시도했습니다. 초대는 성공했지만 보호는 GitHub 요금제 제한으로 실패했습니다. 따라서 **PR 리뷰·CI 통과 후 주진호가 병합한다는 팀 규칙만 준비된 상태**이며 서버가 이를 강제한다고 말하지 않습니다. 강제 보호가 필요하면 Owner가 별도 요금제 결정을 해야 합니다.

## 다음 한 단계

설경민이 초대를 수락하고 원본 소스를 `feature/demo-import`의 `apps/demo/`에 업로드합니다. 업로드 전에 origin/main의 최신 문서도 확인합니다. 실제 변경이 올라오면 Issue #1의 원본·보안·실행 정보 확인 후 PR을 만들고 박동찬이 Issue #2를 진행합니다. 이번 초기 구축에서는 빈 통합 PR이나 새 웹앱을 만들지 않았습니다.
