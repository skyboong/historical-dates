from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DatePrecision(str, Enum):
    """역사적 날짜의 정밀도."""

    YEAR = "year"
    MONTH = "month"
    DAY = "day"
    CENTURY = "century"
    DECADE = "decade"
    UNKNOWN = "unknown"


class HistoricalDate(BaseModel):
    """역사적 날짜 정보를 저장하는 데이터 모델."""

    model_config = ConfigDict(
        validate_assignment=True,
        extra="forbid",
    )

    # 원본 데이터
    original: str = Field(
        min_length=1,
        description="원본 날짜 문자열",
    )

    # 해석된 날짜: 역사학적 연도 체계
    year: int | None = None
    month: int | None = None
    day: int | None = None

    # 표준 날짜: normalize.py에서 생성
    edtf: str | None = None

    # 날짜 메타데이터
    precision: DatePrecision = DatePrecision.UNKNOWN
    is_uncertain: bool = False
    is_approximate: bool = False

    # 날짜 계산에 사용할 달력
    calendar: str = "gregorian"
