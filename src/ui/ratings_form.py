from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from src.db.database import db


class RatingsForm(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Агрегированные рейтинги")
        self.resize(640, 420)

        layout = QVBoxLayout(self)
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Объект", "Средний рейтинг", "Кол-во отзывов", "Обновлено"])
        table.horizontalHeader().setStretchLastSection(True)

        rows = db.fetch_all(
            """
            SELECT i.title, r.avg_rating, r.reviews_count, r.updated_at
            FROM ratings r JOIN items i ON i.id = r.item_id
            ORDER BY r.avg_rating DESC
            """
        )
        table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate([row["title"], row["avg_rating"], row["reviews_count"], row["updated_at"]]):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, c, item)

        layout.addWidget(table)