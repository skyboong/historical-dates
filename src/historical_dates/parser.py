"""
역사적 날짜 문자열 파서.

원본 날짜를 해석하여 HistoricalDate 객체로 반환한다.

지원 기능
---------
- 서기 및 기원전 연도
- 한국어 날짜
- ISO 유사 날짜
- BC / BCE / AD / CE
- 연도, 월, 일 수준의 날짜 정밀도
- 불확실성 및 근사 날짜 표현
- 미상 월(00), 미상 일(00)
"""

import re
from datetime import date, datetime

from .models import DatePrecision, HistoricalDate

# ---------------------------------------------------------
# 날짜 표현 정규식
# ---------------------------------------------------------

# DATE_PATTERN = re.compile(
#     r"^(?P<sign>-?)"
#     r"(?P<year>\d{1,4})"
#     r"(?:-(?P<month>\d{1,2}))?"
#     r"(?:-(?P<day>\d{1,2}))?$"
# )

DATE_PATTERN = re.compile(
    r"^(?P<sign>-?)"
    r"(?P<year>\d+)"
    r"(?:-(?P<month>\d{1,2}))?"
    r"(?:-(?P<day>\d{1,2}))?$"
)

ERA_PREFIX = re.compile(
    r"^(기원전|기원후|서기|BCE|BC|CE|AD)\s*",
    re.IGNORECASE,
)

ERA_SUFFIX = re.compile(
    r"\s*(BCE|BC|CE|AD)$",
    re.IGNORECASE,
)

APPROX_PREFIX = re.compile(
    r"^(약|대략|대충|circa|ca\.?|c\.)\s*",
    re.IGNORECASE,
)

APPROX_SUFFIX = re.compile(
    r"\s*(년경|경|무렵)$",
)


def _extract_qualifiers(
    text: str,
) -> tuple[str, bool, bool]:
    """
    불확실성 및 근사 표현을 추출한다.

    Returns
    -------
    tuple
        (정리된 문자열, is_uncertain, is_approximate)
    """

    is_uncertain = False
    is_approximate = False

    text = text.strip()

    # EDTF의 불확실성 표기
    if text.endswith("%"):
        is_uncertain = True
        is_approximate = True
        text = text[:-1].strip()

    elif text.endswith("?"):
        is_uncertain = True
        text = text[:-1].strip()

    elif text.endswith("~"):
        is_approximate = True
        text = text[:-1].strip()

    # 한국어 및 영어 근사 표현
    match = APPROX_PREFIX.match(text)

    if match:
        is_approximate = True
        text = text[match.end() :].strip()

    match = APPROX_SUFFIX.search(text)

    if match:
        is_approximate = True
        text = text[: match.start()].strip()

    return text, is_uncertain, is_approximate


def _extract_era(
    text: str,
) -> tuple[str, bool | None]:
    """
    기원전·서기 표기를 추출한다.

    Returns
    -------
    tuple
        (정리된 문자열, 기원전 여부)

        True  : 기원전
        False : 서기
        None  : 명시적 시대 표기 없음
    """

    era = None

    match = ERA_PREFIX.match(text)

    if match:
        token = match.group(1).upper()

        era = token in {"기원전", "BC", "BCE"}
        text = text[match.end() :].strip()

    else:
        match = ERA_SUFFIX.search(text)

        if match:
            token = match.group(1).upper()

            era = token in {"BC", "BCE"}
            text = text[: match.start()].strip()

    return text, era


def _normalize_separators(text: str) -> str:
    """날짜 구분자를 하이픈으로 통일한다."""

    # 한국어 날짜
    text = re.sub(r"\s*년\s*", "-", text)
    text = re.sub(r"\s*월\s*", "-", text)
    text = re.sub(r"\s*일\s*", "", text)

    # 슬래시 및 마침표
    text = re.sub(r"\s*[/\.]\s*", "-", text)

    # 하이픈 주변 공백
    text = re.sub(r"\s*-\s*", "-", text)

    return text.strip().rstrip("-")


def _is_leap_year(year: int) -> bool:
    """
    역산 그레고리력 기준 윤년 여부.

    year는 역사학적 연도 체계를 사용한다.
    """

    astronomical_year = year + 1 if year < 0 else year

    return astronomical_year % 4 == 0 and (
        astronomical_year % 100 != 0 or astronomical_year % 400 == 0
    )


def _validate_date(
    year: int,
    month: int | None,
    day: int | None,
) -> None:
    """해석된 날짜의 유효성을 검사한다."""

    if year == 0:
        raise ValueError("역사학적 연도에는 0년이 존재하지 않습니다.")

    if month is None:
        if day is not None:
            raise ValueError("월이 없는 날짜에 일을 지정할 수 없습니다.")
        return

    if not 1 <= month <= 12:
        raise ValueError(f"유효하지 않은 월입니다: {month}")

    if day is None:
        return

    days_in_month = [
        31,
        29 if _is_leap_year(year) else 28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]

    max_day = days_in_month[month - 1]

    if not 1 <= day <= max_day:
        raise ValueError(f"유효하지 않은 일입니다: {year}-{month}-{day}")


def parse_historical_date(
    value: str | int | date | datetime | None,
    *,
    strict: bool = False,
) -> HistoricalDate | None:
    """
    역사적 날짜를 해석하여 HistoricalDate 객체로 반환한다.

    Parameters
    ----------
    value : str | int | date | datetime | None
        원본 날짜.

    strict : bool, default=False
        True이면 잘못된 입력에 ValueError를 발생시킨다.
        False이면 None을 반환한다.

    Returns
    -------
    HistoricalDate | None
        파싱된 날짜 객체.

    Examples
    --------
    >>> parse_historical_date("1564-02-15").year
    1564

    >>> parse_historical_date("기원전 469년경").year
    -469

    >>> parse_historical_date("1564-02").precision
    <DatePrecision.MONTH: 'month'>

    Notes
    -----
    - 연도는 역사학적 연도 체계를 사용한다.
    - 기원전 연도는 음수로 표현한다.
    - EDTF 변환은 수행하지 않는다.
    - 숫자형 연도 변환은 수행하지 않는다.
    """

    def fail(message: str) -> None:
        if strict:
            raise ValueError(message)

    # -----------------------------------------
    # 입력값 처리
    # -----------------------------------------
    if value is None:
        return None

    if isinstance(value, datetime):
        text = value.date().isoformat()

    elif isinstance(value, date):
        text = value.isoformat()

    elif isinstance(value, (str, int)):
        text = str(value).strip()

    else:
        return fail(f"지원하지 않는 입력 타입입니다: {type(value)}")

    if not text:
        return None

    original = text

    # -----------------------------------------
    # 불확실성 표현 추출
    # -----------------------------------------
    text, is_uncertain, is_approximate = _extract_qualifiers(text)

    # -----------------------------------------
    # 기원전 / 서기 추출
    # -----------------------------------------
    text, is_bce = _extract_era(text)

    # 시대 표기 앞의 근사 표현도 지원
    # 예: "BC c. 469"
    text, uncertain2, approximate2 = _extract_qualifiers(text)

    is_uncertain |= uncertain2
    is_approximate |= approximate2

    # -----------------------------------------
    # 날짜 구분자 표준화
    # -----------------------------------------
    text = _normalize_separators(text)

    # -----------------------------------------
    # 날짜 추출
    # -----------------------------------------
    match = DATE_PATTERN.fullmatch(text)

    if not match:
        return fail(f"날짜 형식을 해석할 수 없습니다: {original}")

    sign = match.group("sign")

    year = int(match.group("year"))

    month_str = match.group("month")
    day_str = match.group("day")

    month = int(month_str) if month_str is not None else None

    day = int(day_str) if day_str is not None else None

    # -----------------------------------------
    # 기원전 처리
    # -----------------------------------------
    if sign == "-":
        if is_bce is False:
            return fail(f"시대 표기가 충돌합니다: {original}")

        year = -year

    elif is_bce is True:
        year = -year

    # -----------------------------------------
    # 미상 월·일 처리
    # -----------------------------------------
    if month == 0:
        month = None

    if day == 0:
        day = None

    # 월이 미상인데 일이 지정된 경우
    if month is None and day is not None:
        return fail(f"월이 미상인데 일이 지정되었습니다: {original}")

    # -----------------------------------------
    # 날짜 검증
    # -----------------------------------------
    try:
        _validate_date(year, month, day)

    except ValueError as exc:
        return fail(str(exc))

    # -----------------------------------------
    # 날짜 정밀도
    # -----------------------------------------
    if day is not None:
        precision = DatePrecision.DAY

    elif month is not None:
        precision = DatePrecision.MONTH

    else:
        precision = DatePrecision.YEAR

    # -----------------------------------------
    # 결과 생성
    # -----------------------------------------
    return HistoricalDate(
        original=original,
        year=year,
        month=month,
        day=day,
        precision=precision,
        is_uncertain=is_uncertain,
        is_approximate=is_approximate,
    )
