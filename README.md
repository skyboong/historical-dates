# historical-dates

기원전·서기 역사적 날짜를 파싱하고 정규화하며 타임라인용 숫자로 변환하는 Python 라이브러리입니다.

## 핵심 기능

- 한국어 날짜, BCE/BC/CE/AD, 음수 연도 및 연·월·일 단위 파싱
- 불확실한(`?`)·근사(`~`) 날짜 표시
- 역사학적 연도(0년 없음)와 천문학적 연도(0년 있음) 사이 변환
- 역산 그레고리력을 적용한 윤년·날짜 검증
- 연도 내 시작·중간·끝 위치를 소수형 연도로 표시

## 설치 및 실행

개발 프로젝트 루트에서:

```bash
uv sync
uv run python -c "import historical_dates; print(historical_dates.__file__)"
```

> PyPI 배포 여부와 요구 Python 버전은 프로젝트의 `pyproject.toml`에서 확인하세요.

## 빠른 시작

현재 업로드된 `__init__.py` 기준으로 `converter` 함수는 최상위 패키지에 재공개되지 않습니다.

```python
from historical_dates import parse_historical_date, normalize_historical_date
from historical_dates.converter import historical_date_to_number

date = parse_historical_date("기원전 469년경", strict=True)
assert date is not None
print(date.year)  # -469
print(normalize_historical_date(date))  # -0468~
print(historical_date_to_number(date))  # -468.0
```

## 문서

- [사용자 매뉴얼](docs/user_guide.md)
- [API 참조](docs/api_reference.md)
- [개발 안내](docs/development.md)

## 날짜 규칙 및 제한

- 역사학적 연도에서 기원전 1년은 `-1`, 서기 1년은 `1`이며 **0년은 없습니다**.
- 정규화 결과는 천문학적 연도로 표기하며, 기원전 1년은 `0000`이 됩니다.
- 윤년과 날짜 계산은 실제 역사 시대별 달력 전환을 복원하지 않는 **역산 그레고리력** 기준입니다.
- `HistoricalDate`의 `calendar` 필드는 현재 계산 함수에 전달되지 않아 달력 계산을 바꾸지 않습니다.
- `DatePrecision.CENTURY`·`DECADE`는 모델에 존재하지만 현재 파서에서 생성하지 않고, 숫자 변환기도 이 메타데이터를 직접 해석하지 않습니다.

## 검증

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -v
uv build
```

## License

This project is licensed under the MIT License.

Copyright (c) 2026 Boong Kee Choi.

See [LICENSE](LICENSE) for details.
