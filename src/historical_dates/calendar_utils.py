"""
역사적 날짜 계산을 위한 공통 유틸리티.

지원 기능
---------
- 역사학적 연도 ↔ 천문학적 연도
- 윤년 판정
- 월별 일수 계산
- 연간 일수 계산
- 날짜 유효성 검증

Notes
-----
- 역사학적 연도에는 0년이 없다.
- 천문학적 연도에는 0년이 있다.
- 윤년 계산에는 역산 그레고리력을 사용한다.
- Python datetime을 사용하지 않는다.
"""

from typing import Literal

YearSystem = Literal["historical", "astronomical"]


def historical_to_astronomical(year: int) -> int:
    """
    역사학적 연도를 천문학적 연도로 변환한다.

    Examples
    --------
    -800 -> -799
    -469 -> -468
    -1   -> 0
     1   -> 1
    """

    if isinstance(year, bool) or not isinstance(year, int):
        raise TypeError("year는 정수여야 합니다.")

    if year == 0:
        raise ValueError("역사학적 연도에는 0년이 존재하지 않습니다.")

    return year + 1 if year < 0 else year


def astronomical_to_historical(year: int) -> int:
    """
    천문학적 연도를 역사학적 연도로 변환한다.

    Examples
    --------
    -799 -> -800
    -468 -> -469
    -1   -> -2
     0   -> -1
     1   -> 1
    """

    if isinstance(year, bool) or not isinstance(year, int):
        raise TypeError("year는 정수여야 합니다.")

    return year - 1 if year <= 0 else year


def _to_astronomical(
    year: int,
    system: YearSystem,
) -> int:
    """지정된 연도 체계를 천문학적 연도로 변환한다."""

    if system == "historical":
        return historical_to_astronomical(year)

    if system == "astronomical":
        if isinstance(year, bool) or not isinstance(year, int):
            raise TypeError("year는 정수여야 합니다.")

        return year

    raise ValueError("system은 'historical' 또는 'astronomical'이어야 합니다.")


def is_leap_year(
    year: int,
    *,
    system: YearSystem = "historical",
) -> bool:
    """
    역산 그레고리력 기준 윤년 여부를 계산한다.

    Parameters
    ----------
    year : int
        계산할 연도.

    system : {"historical", "astronomical"}
        입력 연도의 체계.

    Returns
    -------
    bool
        윤년 여부.
    """

    y = _to_astronomical(year, system)

    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def days_in_year(
    year: int,
    *,
    system: YearSystem = "historical",
) -> int:
    """
    해당 연도의 총 일수를 반환한다.

    Returns
    -------
    int
        365 또는 366
    """

    return 366 if is_leap_year(year, system=system) else 365


def days_in_month(
    year: int,
    month: int,
    *,
    system: YearSystem = "historical",
) -> int:
    """
    지정된 연도와 월의 일수를 반환한다.

    Examples
    --------
    >>> days_in_month(2000, 2)
    29

    >>> days_in_month(1900, 2)
    28

    >>> days_in_month(-1, 2)
    29
    """

    if isinstance(month, bool) or not isinstance(month, int):
        raise TypeError("month는 정수여야 합니다.")

    if not 1 <= month <= 12:
        raise ValueError(f"month는 1~12 사이여야 합니다: {month}")

    # 연도와 체계의 유효성도 함께 검증한다.
    leap = is_leap_year(year, system=system)

    month_days = (
        31,
        29 if leap else 28,
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
    )

    return month_days[month - 1]


def validate_date(
    year: int,
    month: int | None = None,
    day: int | None = None,
    *,
    system: YearSystem = "historical",
) -> bool:
    """
    역사적 날짜의 유효성을 검증한다.

    Parameters
    ----------
    year : int
        연도.

    month : int | None
        월. None이면 연도 정밀도의 날짜.

    day : int | None
        일. None이면 월 정밀도의 날짜.

    system : {"historical", "astronomical"}
        입력 연도 체계.

    Returns
    -------
    bool
        유효한 날짜이면 True.

    Raises
    ------
    TypeError
        입력 타입이 올바르지 않은 경우.

    ValueError
        유효하지 않은 날짜인 경우.

    Notes
    -----
    - 월 또는 일이 None이면 날짜 정밀도를 보존한다.
    - 0월이나 0일은 허용하지 않는다.
    - 미상 월·일을 None으로 변환하는 것은 parser.py의 역할이다.
    """

    # 연도 검증
    _to_astronomical(year, system)

    # 월과 일이 모두 없는 경우
    if month is None:
        if day is not None:
            raise ValueError("월이 없는 날짜에 일을 지정할 수 없습니다.")

        return True

    # 월 검증
    if isinstance(month, bool) or not isinstance(month, int):
        raise TypeError("month는 정수여야 합니다.")

    if not 1 <= month <= 12:
        raise ValueError(f"유효하지 않은 월입니다: {month}")

    # 일이 없는 경우
    if day is None:
        return True

    # 일 검증
    if isinstance(day, bool) or not isinstance(day, int):
        raise TypeError("day는 정수여야 합니다.")

    max_day = days_in_month(
        year,
        month,
        system=system,
    )

    if not 1 <= day <= max_day:
        raise ValueError(f"유효하지 않은 날짜입니다: {year}-{month:02d}-{day:02d}")

    return True
