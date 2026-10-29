"""Агрегация рейтинга по опубликованным отзывам."""

from src.db.database import db
from src.config import STATUS_PUBLISHED


def recalc_rating(item_id: int) -> None:
    row = db.fetch_one(
        """
        SELECT AVG(CAST(rating AS DECIMAL(5,2))) AS avg_rating,
               COUNT(*) AS cnt
        FROM reviews
        WHERE item_id = ? AND status_id = ?
        """,
        (item_id, STATUS_PUBLISHED),
    )
    avg = float(row["avg_rating"]) if row and row["avg_rating"] is not None else 0.0
    cnt = int(row["cnt"]) if row else 0

    db.execute(
        """
        MERGE ratings AS target
        USING (SELECT ? AS item_id) AS src
        ON target.item_id = src.item_id
        WHEN MATCHED THEN
            UPDATE SET avg_rating = ?, reviews_count = ?, updated_at = SYSDATETIME()
        WHEN NOT MATCHED THEN
            INSERT(item_id, avg_rating, reviews_count) VALUES (?, ?, ?);
        """,
        (item_id, avg, cnt, item_id, avg, cnt),
    )