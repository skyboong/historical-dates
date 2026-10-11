# historical-dates 사용자 매뉴얼

> 기준: 제공된 `models.py` 정의 및 `parser.py`, `normalize.py`, `converter.py`, `calendar_utils.py`, `__init__.py` 소스. 미확인 항목은 별도 표시했습니다.

## 1. 개요

문자열 날짜를 `HistoricalDate` 객체로 **파싱**하고, 이를 정규화된 날짜 문자열 또는 시각화용 숫자로 **변환**하는 라이브러리입니다.

```text
"기원전 469년경"
   │ parse_historical_date
   ▼
HistoricalDate(year=-469, precision=YEAR, is_approximate=True, ...)
   ├── normalize_historical_date ──► "-0468~"
   └── historical_date_to_number ─► -468.0
```

## 2. 설치

```bash
uv sync
uv run python -c "import historical_dates"
```

`historical_date_to_number`는 현재 `__init__.py`에서 재공개되지 않아 하위 모듈에서 가져와야 합니다.

## 3. 빠른 시작

```python
from historical_dates import parse_historical_date, normalize_historical_date
from historical_dates.converter import historical_date_to_number

date = parse_historical_date("기원전 469년경", strict=True)
assert date is not None
print(date.original)  # 기원전 469년경
print(date.year)  # -469 (역사학적 연도)
print(date.is_approximate)  # True
print(normalize_historical_date(date))  # -0468~
print(historical_date_to_number(date))  # -468.0
```

## 4. HistoricalDate 데이터 모델

| 필드 | 타입 | 기본값 | 용도 |
|---|---|---|---|
| `original` | `str` | 필수 | 빈 문자열을 제외한 원문 |
| `year` | `int \| None` | `None` | 역사학적 연도 |
| `month`, `day` | `int \| None` | `None` | 월·일(미상은 `None`) |
| `edtf` | `str \| None` | `None` | 정규화 결과 보관용 |
| `precision` | `DatePrecision` | `UNKNOWN` | YEAR, MONTH, DAY, CENTURY, DECADE, UNKNOWN |
| `is_uncertain` | `bool` | `False` | 불확실 여부 |
| `is_approximate` | `bool` | `False` | 근사 여부 |
| `calendar` | `str` | `"gregorian"` | 달력 메타데이터 |

모델은 `validate_assignment=True`, `extra="forbid"`입니다. **모델 자체는 월·일 및 연도 0의 모든 의미적 유효성을 검증하지 않습니다.** 날짜 문자열을 파싱하거나 `validate_date`를 사용해 검사하세요.

```python
from historical_dates import HistoricalDate, DatePrecision

record = HistoricalDate(original="1600년", year=1600, precision=DatePrecision.YEAR)
print(record.model_dump())
encoded = record.model_dump_json()
restored = HistoricalDate.model_validate_json(encoded)
```

## 5. 날짜 문자열 파싱

```python
from historical_dates import parse_historical_date

examples = [
    "1564-02-15",
    "1564-02",
    "1564",
    "기원전 469년",
    "469 BCE",
    "BC 469",
    "약 1600년",
    "1600?",
    "1600-00-00",
]
for value in examples:
    parsed = parse_historical_date(value, strict=True)
    print(value, parsed.year, parsed.month, parsed.day, parsed.precision)
```

파서는 `str`, `int`, `date`, `datetime`, `None`을 받고, `HistoricalDate | None`을 반환합니다. 기본 `strict=False`에서는 형식·날짜 오류 시 `None`을 반환하며 `strict=True`에서는 `ValueError`를 발생시킵니다. `None`과 공백 문자열 입력은 strict 모드에서도 `None`을 반환합니다.

`00`으로 표시된 미상 월·일은 `None`으로 처리합니다. 미상 월과 알려진 일이 함께 있으면 오류입니다.

불확실성 기호는 `?`(불확실), `~`(근사), `%`(둘 다)입니다. `년경`, `약`, `circa` 등 근사 표현도 인식합니다.

## 6. 날짜 정규화

```python
from historical_dates import parse_historical_date, normalize_historical_date

item = parse_historical_date("기원전 469년경", strict=True)
assert item is not None
print(normalize_historical_date(item))  # -0468~
```

반환값은 `str`이며 입력 객체의 `edtf` 값을 **자동으로 변경하지 않습니다**. 저장하려면 명시적으로 할당하세요.

```python
item.edtf = normalize_historical_date(item)
```

음수 역사학적 연도는 천문학적 연도로 한 해 이동합니다. 4자리를 초과하는 연도(절댓값 9999 초과)는 연도 단독일 때 `Y` 접두로 표현하며, 해당 연도의 연·월/연·월·일 표기는 지원하지 않습니다. 함수는 일 범위를 1~31로만 검사하므로 월별 실제 일수 확인은 `validate_date`를 별도로 이용하세요.

## 7. 타임라인용 숫자 변환

```python
from historical_dates import parse_historical_date
from historical_dates.converter import historical_date_to_number

item = parse_historical_date("1600-02", strict=True)
assert item is not None

start = historical_date_to_number(item, position="start")
middle = historical_date_to_number(item, position="middle")
end = historical_date_to_number(item, position="end")
print(start, middle, end)
```

`position`은 `"start"`, `"middle"`, `"end"`입니다. 연도만 주어지면 전체 연도, 월까지 있으면 해당 월, 일까지 있으면 그 하루에서 위치를 구합니다. 반환값은 소수형 연도 `float`입니다. 기본 `system="astronomical"`이며 `"historical"`로 변경할 수 있습니다.

**주의:** 결과는 실제 과거 경과일의 절대 일련번호가 아니라 시각화용 상대 연도 좌표입니다. `system="historical"`은 연도 0이 없는 축을 사용하므로 BCE/CE 경계에서 연속 축이 필요하면 기본 `astronomical`을 권장합니다. 불확실성/근사성 표기에 따른 오차범위는 계산하지 않습니다.

## 8. 달력 보조 도구

```python
from historical_dates import (
    historical_to_astronomical,
    astronomical_to_historical,
    is_leap_year,
    days_in_month,
    days_in_year,
    validate_date,
)

assert historical_to_astronomical(-1) == 0
assert astronomical_to_historical(0) == -1
assert is_leap_year(2000)
assert days_in_month(2000, 2) == 29
assert days_in_year(1900) == 365
assert validate_date(-469, 5, 10)
```

이 함수들은 **역산 그레고리력**을 사용합니다. `validate_date`는 유효하면 `True`, 잘못된 입력이면 `TypeError` 또는 `ValueError`를 발생시킵니다.

## 9. 흔한 오류

| 상황 | 조치 |
|---|---|
| `parse_historical_date(...)` 결과가 `None` | 원문 형식 확인; 원인 파악 시 `strict=True` 사용 |
| 0년을 입력함 | 역사학적 입력에는 0년이 없음; 천문학적 연도 변환 함수의 출력과 구분 |
| `-0468`이 `-469`와 다름 | 정규화 결과는 천문학적 연도 |
| `from historical_dates import historical_date_to_number` 실패 | 현재는 `historical_dates.converter`에서 import |
| `normalizer` 호출 후 `date.edtf is None` | 정규화 함수는 문자열만 반환; 필드 할당 필요 |
| 세기·10년 정밀도 변환 기대 | 현재 파서·변환기의 지원 범위가 제한됨 |

## 10. 테스트와 품질 검사

```bash
uv run pytest -v
uv run pyright
uv run ruff check .
uv run ruff format --check .
uv build
```

실제 테스트 통과 및 PyPI 배포 여부는 이 문서를 작성하면서 확인하지 않았습니다.
