# historical-dates API Reference

> 이 문서는 제공된 구현을 기준으로 합니다. 함수 호출 예시는 `src` 레이아웃 설치 이후 실행하세요.

## 최상위 공개 API (`historical_dates/__init__.py`)

`DatePrecision`, `HistoricalDate`, `YearSystem`, `parse_historical_date`, `normalize_historical_date`, `historical_to_astronomical`, `astronomical_to_historical`, `is_leap_year`, `days_in_year`, `days_in_month`, `validate_date`.

`historical_date_to_number`는 `converter.py`에 있지만 현재 `__init__.py`에 포함되지 않았습니다.

## 모델 (`models.py`)

### `DatePrecision`

문자열 Enum: `YEAR="year"`, `MONTH="month"`, `DAY="day"`, `CENTURY="century"`, `DECADE="decade"`, `UNKNOWN="unknown"`.

### `HistoricalDate`

Pydantic `BaseModel`. 필드: `original: str`(필수, 최소 길이 1), `year`, `month`, `day`, `edtf`, `precision`, `is_uncertain`, `is_approximate`, `calendar`. 모델 설정: `validate_assignment=True`, `extra="forbid"`.

## 파서 (`parser.py`)

### `parse_historical_date(value: str | int | date | datetime | None, *, strict: bool = False) -> HistoricalDate | None`

날짜 문자열·정수·표준 Python 날짜를 역사학적 연도로 해석합니다.

- `strict=False`: 파싱 불가능한 입력은 `None`(빈 입력도 `None`).
- `strict=True`: 잘못된 형식·날짜는 `ValueError`; `None` 및 빈 입력은 `None`.
- 기원전은 음수 연도이며 0년은 유효하지 않습니다.
- 입력 정밀도에 따라 `YEAR`, `MONTH`, `DAY`를 지정합니다.
- `?`, `~`, `%`와 일부 한국어·영어 근사 표현을 인식합니다.

```python
from historical_dates import parse_historical_date

obj = parse_historical_date("기원전 469년경", strict=True)
assert obj is not None and obj.year == -469
```

## 정규화 (`normalize.py`)

### `normalize_historical_date(date: HistoricalDate) -> str`

천문학적 연도 기반 EDTF 형태 문자열을 반환합니다. 객체는 변경하지 않습니다.

- `TypeError`: 입력 객체 타입 오류
- `ValueError`: 연도 누락, 잘못된 구성 요소, 미지원 확장 연도 형식
- 불확실 `?`, 근사 `~`, 둘 다 `%`

```python
from historical_dates import normalize_historical_date, parse_historical_date

obj = parse_historical_date("기원전 469년경", strict=True)
assert obj is not None
assert normalize_historical_date(obj) == "-0468~"
```

## 변환기 (`converter.py`)

### `historical_date_to_number(date: HistoricalDate, *, position: Literal["start", "middle", "end"] = "start", system: YearSystem = "astronomical") -> float`

역산 그레고리력을 적용해 소수형 연도 좌표를 만듭니다.

- `position`: 기간의 시작, 중간, 마지막 날짜
- `system`: `"astronomical"`(기본), `"historical"`
- `TypeError`: `date` 타입 오류
- `ValueError`: 연도 누락, 잘못된 날짜/옵션

```python
from historical_dates import parse_historical_date
from historical_dates.converter import historical_date_to_number

obj = parse_historical_date("기원전 469년", strict=True)
assert obj is not None
assert historical_date_to_number(obj) == -468.0
```

## 달력 (`calendar_utils.py`)

### `historical_to_astronomical(year: int) -> int`

BCE는 1을 더하고 CE는 그대로 반환. `year=0` 금지. 잘못된 타입은 `TypeError`.

### `astronomical_to_historical(year: int) -> int`

천문학적 0 이하 연도는 1을 빼서 역사학적 연도로 반환. 잘못된 타입은 `TypeError`.

### `is_leap_year(year: int, *, system: YearSystem = "historical") -> bool`

역산 그레고리력 기준 윤년 판정.

### `days_in_year(year: int, *, system: YearSystem = "historical") -> int`

365 또는 366을 반환.

### `days_in_month(year: int, month: int, *, system: YearSystem = "historical") -> int`

해당 월의 날짜 수. 월 범위는 1~12.

### `validate_date(year: int, month: int | None = None, day: int | None = None, *, system: YearSystem = "historical") -> bool`

유효하면 `True`; 유효하지 않으면 예외. 월이 `None`이면 일이 있어서는 안 되며, 입력 값 0을 미상 월·일로 허용하지 않습니다(`parser.py`에서 `None`으로 치환).

### `YearSystem`

`Literal["historical", "astronomical"]` 타입 별칭.

## 구현상 주의사항

- 기본 연도 변환은 **천문학적 연도**입니다.
- `normalize_historical_date()`는 달력의 실제 월별 마지막 날짜까지 검사하지는 않습니다.
- `calendar` 모델 속성을 설정해도 계산 기준은 역산 그레고리력입니다.
- `DatePrecision.CENTURY` 및 `DECADE`는 변환기에서 별도의 기간 처리를 수행하지 않습니다.
