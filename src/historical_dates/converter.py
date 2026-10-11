"""
역사적 날짜를 숫자형 연도로 변환하는 모듈.

지원 기능
---------
- HistoricalDate -> float
- 역사학적 / 천문학적 연도 선택
- 연도 / 월 / 일 정밀도 반영
- 시작 / 중간 / 끝 대표 시점 선택
- 윤년 및 실제 월별 일수 반영

Notes
-----
- 기본 출력은 천문학적 연도 체계이다.
- 역산 그레고리력을 기준으로 계산한다.
- 출력값은 시각화를 위한 연속적인 숫자 좌표이다.
"""

from typing import Literal

from .calendar_utils import (
    YearSystem,
    days_in_month,
    days_in_year,
    historical_to_astronomical,
    validate_date,
)
from .models import HistoricalDate

DatePosition = Literal["start", "middle", "end"]


def _day_of_year(
    year: int,
    month: int,
    day: int,
) -> int:
    """
    날짜의 연중 순서를 계산한다.

    Examples
    --------
    2000-01-01 -> 1
    2000-02-01 -> 32
    """

    preceding_days = sum(days_in_month(year, m) for m in range(1, month))

    return preceding_days + day


def _get_position_fraction(
    start_day: int,
    end_day: int,
    total_days: int,
    position: DatePosition,
) -> float:
    """
    기간 내 대표 시점을 연도 소수로 변환한다.

    start_day와 end_day는 1부터 시작하는 연중 일수이다.
    """

    if position == "start":
        elapsed_days = start_day - 1

    elif position == "middle":
        elapsed_days = ((start_day - 1) + end_day) / 2

    elif position == "end":
        elapsed_days = end_day - 1

    else:
        raise ValueError("position은 'start', 'middle', 'end' 중 하나여야 합니다.")

    return elapsed_days / total_days


def historical_date_to_number(
    date: HistoricalDate,
    *,
    position: DatePosition = "start",
    system: YearSystem = "astronomical",
) -> float:
    """
    HistoricalDate 객체를 숫자형 연도로 변환한다.

    Parameters
    ----------
    date : HistoricalDate
        변환할 역사적 날짜 객체.

    position : {"start", "middle", "end"}, default="start"
        날짜 정밀도에 따른 대표 시점.

        start:
            해당 기간의 시작.

        middle:
            해당 기간의 중간.

        end:
            해당 기간의 마지막 날.

    system : {"historical", "astronomical"}, default="astronomical"
        반환할 연도 체계.

    Returns
    -------
    float
        연도와 연중 상대 위치를 결합한 숫자.

    Examples
    --------
    >>> date = parse_historical_date("1564-01-01")
    >>> historical_date_to_number(date)
    1564.0

    >>> date = parse_historical_date("기원전 469년")
    >>> historical_date_to_number(date)
    -468.0

    Notes
    -----
    - 입력 연도는 역사학적 연도 체계이다.
    - 기본 반환값은 천문학적 연도 체계이다.
    - 역산 그레고리력을 사용한다.
    - 불확실성에 따른 범위 추정은 수행하지 않는다.
    """

    if not isinstance(date, HistoricalDate):
        raise TypeError("date는 HistoricalDate 객체여야 합니다.")

    if date.year is None:
        raise ValueError("날짜에 연도 정보가 없습니다.")

    # -----------------------------------------
    # 입력 날짜 검증
    # -----------------------------------------
    validate_date(
        date.year,
        date.month,
        date.day,
    )

    # -----------------------------------------
    # 출력 연도 체계
    # -----------------------------------------
    if system == "astronomical":
        numeric_year = historical_to_astronomical(date.year)

    elif system == "historical":
        numeric_year = date.year

    else:
        raise ValueError("system은 'historical' 또는 'astronomical'이어야 합니다.")

    # -----------------------------------------
    # 연간 일수
    # -----------------------------------------
    total_days = days_in_year(date.year)

    # -----------------------------------------
    # 정밀도에 따른 기간 계산
    # -----------------------------------------

    # 연도 정밀도
    if date.month is None:
        start_day = 1
        end_day = total_days

    # 월 정밀도
    elif date.day is None:
        start_day = _day_of_year(
            date.year,
            date.month,
            1,
        )

        end_day = (
            start_day
            + days_in_month(
                date.year,
                date.month,
            )
            - 1
        )

    # 일 정밀도
    else:
        start_day = _day_of_year(
            date.year,
            date.month,
            date.day,
        )

        end_day = start_day

    # -----------------------------------------
    # 연도 내 상대 위치
    # -----------------------------------------
    fraction = _get_position_fraction(
        start_day,
        end_day,
        total_days,
        position,
    )

    return float(numeric_year + fraction)
