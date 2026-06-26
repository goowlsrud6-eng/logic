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


## 완성본 v1.0으로 사용하기

실제 업무용으로 사용하기 전에는 `FINAL_RELEASE_CHECKLIST.md`를 기준으로 실제 재고/판매, 오픈일, 이카운트 입고예정 파일을 한 번씩 업로드해 검수하세요.

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


## 앞으로 사용하는 입력 파일

이제 기존처럼 30개가 넘는 특별재고 시트를 계속 작성하는 것이 목표가 아닙니다. 기본 방식은 **간단 기초파일**입니다.

기초파일에는 최소한 아래 컬럼만 있으면 됩니다.

```text
상품명
현재고
최근한주수량
총판매수량
```

옵션별로 보고 싶으면 아래 컬럼을 추가합니다.

```text
상품코드
옵션명
판매일수
입고예정수량
배송수량
접수수량
```

대시보드에서 `기초파일 양식 다운로드`를 누르면 예시 엑셀을 받을 수 있습니다. 그 파일에 현재고, 최근한주수량, 총판매수량을 입력해서 업로드하면 판매가능주가 자동 계산됩니다. 자세한 컬럼 설명은 `BASIC_INPUT_TEMPLATE.md`에 정리되어 있습니다.

기존 특별재고 파일 업로드는 과거 파일을 읽기 위한 보조 기능으로 남겨두었습니다.

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


## 바탕화면 바로가기 만들기

프로젝트 폴더 안의 `create_desktop_shortcut.bat`를 더블클릭하면 바탕화면에 `특별재고 대시보드` 바로가기가 만들어집니다.

다음부터는 바탕화면 바로가기를 더블클릭해서 서버를 실행하면 됩니다.

화면이 예전 그대로 보이면 기존 CMD 서버를 `Ctrl + C`로 끈 뒤, 최신 파일로 다시 실행하세요. 상단 제목이 `특별재고 대시보드 v2`로 보이면 최신 화면입니다.


## GitHub에 최신 파일이 안 보일 때

GitHub에 파일 개수가 예전 그대로 보이면 최신 commit이 push/merge되지 않았을 수 있습니다. `GITHUB_SYNC_GUIDE.md`를 참고해서 브랜치, PR, push 상태를 확인하세요.


## CMD에서 한글이 깨져 보이는 경우

Windows CMD에서 `.bat` 파일 안의 한글이 깨지면 `내부 또는 외부 명령` 오류가 날 수 있습니다. 그래서 실행용 배치 파일은 영어만 사용하도록 바꿨습니다.

최신 `run_windows_cmd.bat`를 다시 실행하면 `[1/5] Project folder` 같은 영어 단계가 보여야 합니다.


## 화면 구성

대시보드는 3개 화면으로 나눕니다.

1. 요약 페이지: 모든 품목을 상품명 기준으로 한 줄씩 보여줍니다.
2. 품목별 상세 페이지: 요약 페이지에서 상품명을 클릭하면 해당 품목의 옵션별 상세를 보여줍니다.
3. 입고일정 페이지: 입고예정수량 파일에서 업로드한 일정만 따로 보여줍니다.

입고일정 파일을 업로드해도 요약 페이지의 재고/판매 기준 데이터는 마지막 재고/판매 통합 업로드 기준으로 유지됩니다.


## 확정 요구사항

특별재고 관리 시스템의 최종 요구사항은 `SPECIAL_STOCK_REQUIREMENTS.md`에 정리되어 있습니다. 구현할 때 이 문서를 기준으로 맞춥니다.

## 데이터가 섞이지 않도록 바뀐 점

이제 업로드 파일은 `재고/판매 통합`, `상품기본정보/오픈일`, `입고예정`으로 구분해서 저장합니다. 입고예정 파일만 다시 업로드해도 기존 재고/판매 데이터는 유지되고, 대시보드는 마지막 재고/판매 데이터에 현재 예정 상태의 입고예정을 합쳐서 계산합니다.

## 입고예정 직접 관리와 주차별 보관

입고예정일은 `20260624`, `2026/06/24`, `2026-06-24`, `6/24`, `06/24`, `0624`처럼 입력해도 자동으로 날짜로 변환합니다. 입고일정 화면에서 입고예정 건을 직접 추가, 수정, 삭제할 수 있습니다.

재고/판매 통합 파일은 업로드할 때마다 새 주차 스냅샷으로 저장되며, 과거 주차 데이터는 유지됩니다. 요약 화면의 주차별 스냅샷 버튼으로 과거 주차도 조회할 수 있습니다.

## 발주번호 기준 입고예정 일괄 관리

입고예정 양식에는 `발주번호` 컬럼이 포함됩니다. 입고일정 화면에서 같은 발주번호에 속한 옵션들을 그룹으로 보고, 입고예정일/비고를 일괄 수정하거나 해당 발주번호 전체를 삭제할 수 있습니다. 기존처럼 옵션별 개별 수정/삭제도 계속 가능합니다.

## 지난주 기준 계산 방식

지난주 기준 값은 직전 주차의 판매가능주를 그대로 가져오는 방식이 아니라, 현재 주차 입고후재고를 직전 주차의 최근한주 판매수량으로 나누어 계산합니다. 직전 주차는 현재 선택한 주차보다 이전 기준일의 최신 재고/판매 스냅샷을 자동으로 사용합니다.

## 품목 검색과 최근 조회

요약 페이지에서 상품명, 상품코드, 공급처옵션으로 검색하고 판매상태/입고예정 유무로 필터링할 수 있습니다. 품목 상세 화면에는 이전 품목/다음 품목 버튼이 있으며, 최근 조회 품목과 즐겨찾기 품목을 바로 다시 열 수 있습니다.
