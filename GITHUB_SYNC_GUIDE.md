# GitHub에 최신 파일 반영하는 방법

현재 프로젝트 폴더에 최신 파일이 있어도, GitHub에 자동으로 올라가는 것은 아닙니다. GitHub에 보이려면 아래 중 하나가 필요합니다.

## 가장 중요한 점

- 내 컴퓨터/작업 폴더에 파일이 있음 = GitHub에 올라간 것 아님
- Git commit 완료 = 내 Git 기록에 저장된 것
- Git push 완료 = GitHub 저장소에 올라간 것
- Pull Request 생성만 됨 = GitHub에 제안된 상태일 수 있음
- Pull Request merge 완료 = 기본 브랜치에 반영된 상태

## 현재 확인해야 하는 것

GitHub 저장소에 파일이 22개만 보이고, 여기서는 26개라고 보인다면 보통 아래 중 하나입니다.

1. 최신 commit이 GitHub에 push되지 않음
2. Pull Request는 만들어졌지만 merge되지 않음
3. GitHub에서 보고 있는 브랜치가 최신 작업 브랜치가 아님
4. ZIP 다운로드를 예전 commit 또는 예전 브랜치에서 받음

## CMD/Git Bash에서 확인할 명령어

프로젝트 폴더에서 아래 명령어를 입력합니다.

```bash
git status
git log --oneline -5
git remote -v
git branch
```

## GitHub에 올리는 기본 순서

원격 저장소가 연결되어 있다면 아래 명령어를 사용합니다.

```bash
git add .
git commit -m "Update special stock dashboard"
git push origin 현재브랜치명
```

이미 commit이 되어 있다면 `git add`와 `git commit`은 다시 할 필요 없이 아래만 하면 됩니다.

```bash
git push origin 현재브랜치명
```

## GitHub에서 확인할 것

GitHub 웹사이트에서 아래를 확인합니다.

1. 브랜치 선택 드롭다운이 최신 브랜치인지 확인
2. Pull requests 탭에서 열린 PR이 있는지 확인
3. PR이 있으면 Files changed에서 최신 파일이 보이는지 확인
4. 기본 브랜치에 반영하려면 PR을 merge해야 함

## 최신 파일인지 확인하는 기준

최신 파일에는 아래 파일들이 포함되어 있어야 합니다.

```text
create_desktop_shortcut.bat
BASIC_INPUT_TEMPLATE.md
BEGINNER_GUIDE.md
inventory/
special_stock/
run_windows_cmd.bat
run_windows_powershell.ps1
```

대시보드 화면 상단에는 `특별재고 대시보드 v2`가 보여야 합니다.
