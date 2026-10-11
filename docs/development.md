# 개발 및 품질 관리

## 환경 구성

```bash
uv sync
uv run python -c "import historical_dates"
```

## 검사

```bash
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest -v
uv build
```

## 공개 API 정비 제안

현재 `converter.py`의 `historical_date_to_number()`가 최상위 API에 없습니다. 최상위 패키지에서 직접 가져오도록 하려면 `src/historical_dates/__init__.py`에 다음을 추가하세요.

```python
from .converter import historical_date_to_number
```

그리고 `__all__`에 `"historical_date_to_number"`를 추가하세요.

## 배포 전 점검

- `pyproject.toml`의 버전·요구 Python 버전·설명·빌드 백엔드 확인
- 연도 0/BCE-CE 경계, 윤년 및 00 월·일 처리 테스트
- 타입 검사와 패키지 빌드 성공 확인
- README와 라이선스 파일 추가
- 배포 전 변경 이력 및 라이선스 정책 확정

## 유지보수 시 주의

- 모델 검증과 파서/달력 계산 검증은 서로 역할이 다릅니다.
- EDTF 출력 형식과 표준 전체 범위의 지원 여부를 혼동하지 마세요.
- 실역사 달력 전환을 자동으로 반영하지 않습니다.
