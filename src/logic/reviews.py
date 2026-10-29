"""CRUD отзывов, валидация, модерация, автопересчёт рейтинга."""

from src.db.database import db
from src.logic.ratings import recalc_rating
from src.logic.auth import log_action
from src.config import STATUS_ON_MODERATION, STATUS_PUBLISHED, STATUS_REJECTED


class ValidationError(ValueError):
    pass


def validate_review(rating: int, text: str) -> None:
    if not isinstance(rating, int) or not (1 <= rating <= 5):
        raise ValidationError("Оценка должна быть целым числом от 1 до 5.")
    if not text or len(text.strip()) < 10:
        raise ValidationError("Текст отзыва должен содержать не менее 10 символов.")


def create_review(user_id: int, item_id: int, rating: int, text: str) -> int:
    validate_review(rating, text)
    exists = db.fetch_one(
        "SELECT id FROM reviews WHERE user_id = ? AND item_id = ?",
        (user_id, item_id),
    )
    if exists:
        raise ValidationError("Вы уже оставили отзыв на этот объект.")

    db.execute(
        """
        INSERT INTO reviews(user_id, item_id, rating, text, status_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, item_id, rating, text.strip(), STATUS_ON_MODERATION),
    )
    row = db.fetch_one(
        "SELECT TOP 1 id FROM reviews WHERE user_id = ? AND item_id = ? ORDER BY id DESC",
        (user_id, item_id),
    )
    log_action(user_id, "create", "review", row["id"])
    return row["id"]


def update_review(review_id: int, user_id: int, rating: int, text: str) -> None:
    validate_review(rating, text)
    review = db.fetch_one("SELECT * FROM reviews WHERE id = ?", (review_id,))
    if not review or review["user_id"] != user_id:
        raise ValidationError("Отзыв не найден или не принадлежит пользователю.")

    db.execute(
        """
        UPDATE reviews
        SET rating = ?, text = ?, status_id = ?, updated_at = SYSDATETIME()
        WHERE id = ?
        """,
        (rating, text.strip(), STATUS_ON_MODERATION, review_id),
    )
    log_action(user_id, "update", "review", review_id)
    recalc_rating(review["item_id"])


def delete_review(review_id: int, actor_id: int, is_admin: bool = False) -> None:
    review = db.fetch_one("SELECT * FROM reviews WHERE id = ?", (review_id,))
    if not review:
        return
    if not is_admin and review["user_id"] != actor_id:
        raise ValidationError("Недостаточно прав для удаления отзыва.")

    db.execute("DELETE FROM reviews WHERE id = ?", (review_id,))
    log_action(actor_id, "delete", "review", review_id)
    recalc_rating(review["item_id"])


def moderate_review(review_id: int, admin_id: int, approve: bool) -> None:
    review = db.fetch_one("SELECT * FROM reviews WHERE id = ?", (review_id,))
    if not review:
        raise ValidationError("Отзыв не найден.")

    new_status = STATUS_PUBLISHED if approve else STATUS_REJECTED
    db.execute(
        "UPDATE reviews SET status_id = ?, updated_at = SYSDATETIME() WHERE id = ?",
        (new_status, review_id),
    )
    log_action(admin_id, "moderate", "review", review_id)
    recalc_rating(review["item_id"])


def list_reviews(item_id: int | None = None, only_published: bool = False) -> list:
    query = """
        SELECT r.id, r.rating, r.text, r.created_at, u.login AS author,
               i.title AS item, s.name AS status, r.item_id, r.user_id
        FROM reviews r
        JOIN users u ON u.id = r.user_id
        JOIN items i ON i.id = r.item_id
        JOIN review_statuses s ON s.id = r.status_id
        WHERE 1 = 1
    """
    params: list = []
    if item_id is not None:
        query += " AND r.item_id = ?"
        params.append(item_id)
    if only_published:
        query += " AND r.status_id = ?"
        params.append(STATUS_PUBLISHED)
    query += " ORDER BY r.created_at DESC"
    return db.fetch_all(query, tuple(params))