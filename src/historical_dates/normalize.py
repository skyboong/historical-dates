"""
역사적 날짜를 EDTF 표준 문자열로 정규화한다.

지원 범위
---------
- 역사학적 연도 -> 천문학적 연도
- 연도, 월, 일 정밀도 유지
- 기원전 연도
- 불확실성 및 근사성 표기
- 4자리 초과 연도의 연도 단독 표현

Notes
-----
- 입력은 HistoricalDate 객체이다.
- 입력 객체를 직접 변경하지 않는다.
- Python datetime에 의존하지 않는다.
"""

from .calendar_utils import historical_to_astronomical
from .models import HistoricalDate


def _get_qualifier(date: HistoricalDate) -> str:
    """
    EDTF 날짜의 불확실성 표기를 반환한다.
    """

    if date.is_uncertain and date.is_approximate:
        return "%"

    if date.is_uncertain:
        return "?"

    if date.is_approximate:
        return "~"

    return ""


def normalize_historical_date(
    date: HistoricalDate,
) -> str:
    """
    HistoricalDate 객체를 EDTF 문자열로 변환한다.

    Parameters
    ----------
    date : HistoricalDate
        parse_historical_date()로 생성한 날짜 객체.

    Returns
    -------
    str
        EDTF 표준 날짜 문자열.

    Raises
    ------
    TypeError
        HistoricalDate 객체가 아닌 경우.

    ValueError
        연도 정보가 없거나 날짜 구성요소가 잘못된 경우.
        지원하지 않는 확장 연도 형식인 경우.

    Examples
    --------
    >>> from historical_dates import parse_historical_date
    >>> date = parse_historical_date("기원전 469년경")
    >>> normalize_historical_date(date)
    '-0468~'
    """

    # -----------------------------------------
    # 입력 검증
    # -----------------------------------------
    if not isinstance(date, HistoricalDate):
        raise TypeError("date는 HistoricalDate 객체여야 합니다.")

    if date.year is None:
        raise ValueError("정규화할 연도 정보가 없습니다.")

    # -----------------------------------------
    # 역사학적 연도 -> 천문학적 연도
    # -----------------------------------------
    year = historical_to_astronomical(date.year)

    month = date.month
    day = date.day

    # -----------------------------------------
    # 날짜 구성요소 검증
    # -----------------------------------------
    if month is None and day is not None:
        raise ValueError("월이 없는 날짜에 일을 지정할 수 없습니다.")

    if month is not None and not 1 <= month <= 12:
        raise ValueError(f"유효하지 않은 월입니다: {month}")

    if day is not None and not 1 <= day <= 31:
        raise ValueError(f"유효하지 않은 일입니다: {day}")

    # -----------------------------------------
    # 연도 형식
    # -----------------------------------------
    if abs(year) > 9999:
        if month is not None or day is not None:
            raise ValueError(
                "5자리 이상 확장 연도의 연월일 표기는 현재 지원하지 않습니다."
            )

        year_str = f"Y{year}"

    elif year < 0:
        year_str = f"-{abs(year):04d}"

    else:
        year_str = f"{year:04d}"

    # -----------------------------------------
    # 날짜 정밀도 유지
    # -----------------------------------------
    if month is None:
        result = year_str

    elif day is None:
        result = f"{year_str}-{month:02d}"

    else:
        result = f"{year_str}-{month:02d}-{day:02d}"

    # -----------------------------------------
    # 불확실성 / 근사성
    # -----------------------------------------
    qualifier = _get_qualifier(date)

    return result + qualifier
