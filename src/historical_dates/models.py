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


# class DatePrecision(str, Enum):
#     """역사적 날짜의 정밀도."""

#     YEAR = "year"
#     MONTH = "month"
#     DAY = "day"
#     CENTURY = "century"
#     DECADE = "decade"
#     UNKNOWN = "unknown"


# class HistoricalDate(BaseModel):
#     """
#     역사적 날짜 정보를 표현하는 데이터 모델.

#     Notes
#     -----
#     - 원본 날짜와 표준 날짜를 구분하여 저장한다.
#     - 기원전·서기 연도는 표준화 과정에서 처리한다.
#     - 날짜의 정밀도와 불확실성을 보존한다.
#     - 날짜 파싱 및 변환 로직은 별도 모듈에서 구현한다.
#     """

#     model_config = ConfigDict(
#         validate_assignment=True,
#         extra="forbid",
#     )

#     original: str = Field(
#         ...,
#         min_length=1,
#         description="입력된 원본 날짜",
#     )

#     edtf: str | None = Field(
#         default=None,
#         description="EDTF 표준 날짜",
#     )

#     precision: DatePrecision = Field(
#         default=DatePrecision.UNKNOWN,
#         description="날짜의 정밀도",
#     )

#     is_uncertain: bool = Field(
#         default=False,
#         description="날짜가 불확실한지 여부",
#     )

#     is_approximate: bool = Field(
#         default=False,
#         description="근사 날짜인지 여부",
#     )

#     calendar: str = Field(
#         default="gregorian",
#         description="날짜 계산에 적용하는 달력 체계",
#     )
