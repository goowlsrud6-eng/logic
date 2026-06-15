# 특별재고 Django 대시보드

엑셀 기반 특별재고 파일을 업로드하고, 원본 파일을 보관하면서 품목/옵션별 재고 지표를 계산하는 Django 프로젝트입니다.

## 완전 초보자라면

처음이라면 먼저 `BEGINNER_GUIDE.md`를 열어서 따라 하세요. 파일 다운로드, CMD 열기, 폴더 이동, 서버 실행 순서까지 아주 자세히 적어두었습니다.

## 프로젝트 파일 준비하기

18개 파일을 **하나씩 따로 다운로드할 필요는 없습니다.** 프로젝트 폴더 전체를 한 번에 받아야 합니다.

권장 순서는 아래와 같습니다.

1. 원하는 위치에 프로젝트를 둘 폴더를 정합니다. 예: `C:\Users\me\logic`
2. GitHub/Git 저장소에서 프로젝트를 **Clone** 하거나, ZIP으로 **Download** 받은 뒤 압축을 풉니다.
3. 압축을 풀었거나 clone한 폴더 안에 `manage.py`, `requirements.txt`, `inventory`, `special_stock` 폴더가 보이면 제대로 받은 것입니다.
4. 그 폴더에서 CMD 또는 PowerShell을 열고 아래 실행 명령어를 입력합니다.

폴더 구조는 대략 이렇게 보여야 합니다.

```text
logic/
  manage.py
  requirements.txt
  README.md
  run_windows_cmd.bat
  run_windows_powershell.ps1
  inventory/
  special_stock/
```

Git을 사용할 수 있으면 가장 편한 방식은 아래입니다.

```bat
git clone <저장소주소> logic
cd logic
```

Git을 잘 모르겠다면 ZIP 다운로드 후 압축을 풀고, 압축을 푼 `logic` 폴더에서 시작하면 됩니다.

## 먼저 확인할 것

이 프로젝트는 **터미널에서 명령어를 실행해서 서버를 켠 뒤, 브라우저로 접속**하는 방식입니다. Windows에서는 아래 중 하나를 사용하면 됩니다.

- 추천: **PowerShell**
- 가능: **CMD 명령 프롬프트**
- 비추천: 더블클릭만으로 실행하려고 하는 방식

그리고 아래 명령어는 프로젝트 폴더에서 실행해야 합니다. 예를 들어 프로젝트가 `C:\Users\me\logic`에 있다면 먼저 이동합니다.

```powershell
cd C:\Users\me\logic
```

## Windows PowerShell에서 시작하기

PowerShell을 쓰는 경우에는 아래 순서대로 입력합니다.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

만약 `Activate.ps1` 실행에서 권한 오류가 나면 PowerShell에 아래 명령어를 한 번 실행한 뒤 다시 활성화합니다.

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

## Windows CMD에서 시작하기

CMD, 즉 명령 프롬프트를 쓰는 경우에는 `source .venv/bin/activate`를 입력하면 안 됩니다. 그건 Mac/Linux용 명령어입니다. CMD에서는 아래처럼 입력합니다.

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## Mac/Linux에서 시작하기

Mac이나 Linux에서는 아래 순서대로 입력합니다.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## 접속 방법

서버가 정상 실행되면 터미널에 대략 아래와 비슷한 메시지가 나옵니다.

```text
Starting development server at http://0.0.0.0:8000/
```

브라우저에서는 아래 주소로 접속하면 됩니다.

```text
http://localhost:8000
```

서버를 끄고 싶으면 터미널에서 `Ctrl + C`를 누릅니다.

## 자주 막히는 부분

### `source` 명령어를 찾을 수 없다고 나오는 경우

Windows CMD에서 Mac/Linux용 명령어를 입력한 경우입니다. CMD에서는 아래 명령어를 사용하세요.

```bat
.venv\Scripts\activate.bat
```

PowerShell에서는 아래 명령어를 사용하세요.

```powershell
.\.venv\Scripts\Activate.ps1
```

### `py` 명령어를 찾을 수 없다고 나오는 경우

Python이 설치되어 있지 않거나 PATH 등록이 안 된 상태입니다. Windows에서는 Python 설치 시 **Add python.exe to PATH** 옵션을 체크해야 합니다.

### `pip install -r requirements.txt`에서 실패하는 경우

회사/사내망/보안 프로그램 때문에 패키지 설치가 막힐 수 있습니다. 이 경우에는 오류 메시지를 그대로 복사해서 확인해야 합니다.

### `python manage.py migrate`에서 실패하는 경우

대부분 앞 단계의 패키지 설치가 실패했거나 가상환경이 활성화되지 않은 경우입니다. 터미널 앞에 `(.venv)`가 붙어 있는지 확인하세요.

## 현재 구현 범위

- 특별재고 엑셀 업로드
- 업로드 원본 파일 보관
- 업로드 이력 조회 및 원본 다운로드
- 품목별 요약 대시보드
- 괄호가 있는 품목 주차 시트 자동 탐색
- 가용재고, 입고예정수량, 입고후재고, 최근한주 판매수량, 총판매수량 기반 기초 계산

## 다음 단계

1. 실제 엑셀 파일 기준 컬럼 매핑 보정
2. `옵션채우기` 시트의 공급처옵션 자동 보정 로직 DB화
3. 지난주 대비 판매 상승/하락 계산 추가
4. 옵션별 상세 화면 및 엑셀 다운로드 추가
5. PostgreSQL 전환 및 로그인/권한 추가
