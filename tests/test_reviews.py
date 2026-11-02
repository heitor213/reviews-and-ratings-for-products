import pytest
from src.logic.reviews import validate_review, ValidationError


@pytest.mark.parametrize("rating,text,ok", [
    (1, "Нормальный товар", True),
    (5, "Отличный курс, рекомендую", True),
    (0, "Короткий отзыв", False),
    (6, "Хорошо, но есть минусы", False),
    (5, "мало", False),
])
def test_validate_review(rating, text, ok):
    if ok:
        validate_review(rating, text)
    else:
        with pytest.raises(ValidationError):
            validate_review(rating, text)