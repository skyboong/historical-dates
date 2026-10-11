# """
# Tests for historical_dates.models.

# HistoricalDate와 DatePrecision 모델의
# 기본 생성, 타입 검증 및 직렬화 기능을 테스트한다.
# """

# import pytest
# from pydantic import ValidationError

# from historical_dates.models import (
#     DatePrecision,
#     HistoricalDate,
# )


# # ---------------------------------------------------------
# # 1. 기본 모델 생성
# # ---------------------------------------------------------
# def test_create_historical_date():
#     date = HistoricalDate(
#         year=1600,
#         month=1,
#         day=1,
#         precision=DatePrecision.DAY,
#     )

#     assert date.year == 1600
#     assert date.month == 1
#     assert date.day == 1
#     assert date.precision == DatePrecision.DAY


# # ---------------------------------------------------------
# # 2. 기원전 날짜
# # ---------------------------------------------------------
# def test_bce_date():
#     date = HistoricalDate(
#         year=-700,
#         precision=DatePrecision.YEAR,
#     )

#     assert date.year == -700
#     assert date.precision == DatePrecision.YEAR


# # ---------------------------------------------------------
# # 3. 연도만 있는 불완전 날짜
# # ---------------------------------------------------------
# def test_year_only():
#     date = HistoricalDate(
#         year=1600,
#         precision=DatePrecision.YEAR,
#     )

#     assert date.year == 1600
#     assert date.month is None
#     assert date.day is None


# # ---------------------------------------------------------
# # 4. 연월까지만 있는 날짜
# # ---------------------------------------------------------
# def test_year_month():
#     date = HistoricalDate(
#         year=1600,
#         month=5,
#         precision=DatePrecision.MONTH,
#     )

#     assert date.year == 1600
#     assert date.month == 5
#     assert date.day is None


# # ---------------------------------------------------------
# # 5. 날짜 정밀도
# # ---------------------------------------------------------
# @pytest.mark.parametrize(
#     "precision",
#     [
#         DatePrecision.YEAR,
#         DatePrecision.MONTH,
#         DatePrecision.DAY,
#     ],
# )
# def test_date_precision(precision: DatePrecision):
#     date = HistoricalDate(
#         year=1600,
#         precision=precision,
#     )

#     assert date.precision == precision


# # ---------------------------------------------------------
# # 6. 잘못된 정밀도
# # ---------------------------------------------------------
# def test_invalid_precision():
#     with pytest.raises(ValidationError):
#         HistoricalDate.model_validate(
#             {
#                 "year": 1600,
#                 "precision": "invalid",
#             }
#         )


# # ---------------------------------------------------------
# # 7. JSON 직렬화
# # ---------------------------------------------------------
# def test_json_serialization():
#     date = HistoricalDate(
#         year=-700,
#         month=1,
#         day=1,
#         precision=DatePrecision.DAY,
#     )

#     json_data = date.model_dump_json()

#     assert isinstance(json_data, str)
#     assert '"year":-700' in json_data


# # ---------------------------------------------------------
# # 8. JSON 역직렬화
# # ---------------------------------------------------------
# def test_json_deserialization():
#     json_data = """
#     {
#         "year": -700,
#         "month": 1,
#         "day": 1,
#         "precision": "day"
#     }
#     """

#     date = HistoricalDate.model_validate_json(json_data)

#     assert date.year == -700
#     assert date.month == 1
#     assert date.day == 1
#     assert date.precision == DatePrecision.DAY


# # ---------------------------------------------------------
# # 9. 기원전·서기 경계
# # ---------------------------------------------------------
# @pytest.mark.parametrize(
#     "year",
#     [-2, -1, 1, 2],
# )
# def test_year_boundary(year: int):
#     date = HistoricalDate(
#         year=year,
#         precision=DatePrecision.YEAR,
#     )

#     assert date.year == year

"""
Tests for historical_dates.models.

HistoricalDate 모델의 생성, 검증,
직렬화 및 속성 변경 기능을 테스트한다.
"""

import pytest
from pydantic import ValidationError

from historical_dates.models import (
    DatePrecision,
    HistoricalDate,
)


# ---------------------------------------------------------
# 1. 기본 모델 생성
# ---------------------------------------------------------
def test_create_historical_date():
    date = HistoricalDate(
        original="1600-01-01",
        year=1600,
        month=1,
        day=1,
        precision=DatePrecision.DAY,
    )

    assert date.original == "1600-01-01"
    assert date.year == 1600
    assert date.month == 1
    assert date.day == 1
    assert date.precision == DatePrecision.DAY


# ---------------------------------------------------------
# 2. 기원전 날짜
# ---------------------------------------------------------
def test_bce_date():
    date = HistoricalDate(
        original="-0700",
        year=-700,
        precision=DatePrecision.YEAR,
    )

    assert date.year == -700
    assert date.precision == DatePrecision.YEAR


# ---------------------------------------------------------
# 3. 연도만 존재하는 날짜
# ---------------------------------------------------------
def test_year_only():
    date = HistoricalDate(
        original="1600",
        year=1600,
        precision=DatePrecision.YEAR,
    )

    assert date.year == 1600
    assert date.month is None
    assert date.day is None


# ---------------------------------------------------------
# 4. 연월까지만 존재하는 날짜
# ---------------------------------------------------------
def test_year_month():
    date = HistoricalDate(
        original="1600-05",
        year=1600,
        month=5,
        precision=DatePrecision.MONTH,
    )

    assert date.year == 1600
    assert date.month == 5
    assert date.day is None


# ---------------------------------------------------------
# 5. 날짜 정밀도
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "precision",
    [
        DatePrecision.YEAR,
        DatePrecision.MONTH,
        DatePrecision.DAY,
        DatePrecision.CENTURY,
        DatePrecision.DECADE,
        DatePrecision.UNKNOWN,
    ],
)
def test_date_precision(precision: DatePrecision):
    date = HistoricalDate(
        original="1600",
        year=1600,
        precision=precision,
    )

    assert date.precision == precision


# ---------------------------------------------------------
# 6. 잘못된 정밀도
# ---------------------------------------------------------
def test_invalid_precision():
    with pytest.raises(ValidationError):
        HistoricalDate.model_validate(
            {
                "original": "1600",
                "year": 1600,
                "precision": "invalid",
            }
        )


# ---------------------------------------------------------
# 7. JSON 직렬화
# ---------------------------------------------------------
def test_json_serialization():
    date = HistoricalDate(
        original="-0700-01-01",
        year=-700,
        month=1,
        day=1,
        precision=DatePrecision.DAY,
    )

    json_data = date.model_dump_json()

    assert isinstance(json_data, str)
    assert '"year":-700' in json_data
    assert '"precision":"day"' in json_data


# ---------------------------------------------------------
# 8. JSON 역직렬화
# ---------------------------------------------------------
def test_json_deserialization():
    json_data = """
    {
        "original": "-0700-01-01",
        "year": -700,
        "month": 1,
        "day": 1,
        "precision": "day"
    }
    """

    date = HistoricalDate.model_validate_json(json_data)

    assert date.year == -700
    assert date.month == 1
    assert date.day == 1
    assert date.precision == DatePrecision.DAY


# ---------------------------------------------------------
# 9. 기원전·서기 경계
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "year",
    [-2, -1, 1, 2],
)
def test_year_boundary(year: int):
    date = HistoricalDate(
        original=str(year),
        year=year,
        precision=DatePrecision.YEAR,
    )

    assert date.year == year


# ---------------------------------------------------------
# 10. 원본 날짜 필수 검사
# ---------------------------------------------------------
def test_original_required():
    with pytest.raises(ValidationError):
        HistoricalDate.model_validate(
            {
                "year": 1600,
                "precision": "year",
            }
        )


# ---------------------------------------------------------
# 11. 빈 문자열 검사
# ---------------------------------------------------------
def test_empty_original():
    with pytest.raises(ValidationError):
        HistoricalDate(
            original="",
            year=1600,
        )


# ---------------------------------------------------------
# 12. 추가 필드 금지 검사
# ---------------------------------------------------------
def test_extra_field_forbidden():
    with pytest.raises(ValidationError):
        HistoricalDate.model_validate(
            {
                "original": "1600",
                "year": 1600,
                "unknown_field": 123,
            }
        )


# ---------------------------------------------------------
# 13. 속성 변경 검사
# ---------------------------------------------------------
def test_assignment_validation():
    date = HistoricalDate(
        original="1600",
        year=1600,
    )

    with pytest.raises(ValidationError):
        date.precision = "invalid"  # type: ignore[assignment]


# ---------------------------------------------------------
# 14. 날짜 메타데이터
# ---------------------------------------------------------
def test_date_metadata():
    date = HistoricalDate(
        original="약 1600년",
        year=1600,
        precision=DatePrecision.YEAR,
        is_approximate=True,
        is_uncertain=False,
    )

    assert date.is_approximate is True
    assert date.is_uncertain is False
    assert date.calendar == "gregorian"


# ---------------------------------------------------------
# 15. EDTF 필드
# ---------------------------------------------------------
def test_edtf_field():
    date = HistoricalDate(
        original="-0700",
        year=-700,
        edtf="-0700",
        precision=DatePrecision.YEAR,
    )

    assert date.edtf == "-0700"
