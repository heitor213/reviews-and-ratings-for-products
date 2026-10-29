from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt

from src.logic.reviews import list_reviews, delete_review
from src.ui.review_form import ReviewForm
from src.ui.moderation_form import ModerationForm
from src.ui.ratings_form import RatingsForm


class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle(f"Модуль отзывов — {user.login} ({user.role})")
        self.resize(900, 560)

        central = QWidget()
        root = QVBoxLayout(central)

        nav = QHBoxLayout()
        nav.addWidget(QLabel("Навигация:"))
        btn_refresh = QPushButton("Обновить")
        btn_add = QPushButton("Оставить отзыв")
        btn_ratings = QPushButton("Рейтинги")
        nav.addWidget(btn_refresh)
        nav.addWidget(btn_add)
        nav.addWidget(btn_ratings)

        if user.is_admin:
            btn_moderate = QPushButton("Модерация")
            nav.addWidget(btn_moderate)
            btn_moderate.clicked.connect(self._open_moderation)

        nav.addStretch()
        root.addLayout(nav)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Автор", "Объект", "Оценка", "Статус", "Текст"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        root.addWidget(self.table)

        bottom = QHBoxLayout()
        btn_del = QPushButton("Удалить выбранный")
        bottom.addStretch()
        bottom.addWidget(btn_del)
        root.addLayout(bottom)

        self.setCentralWidget(central)

        btn_refresh.clicked.connect(self.load_reviews)
        btn_add.clicked.connect(self._open_add_review)
        btn_ratings.clicked.connect(lambda: RatingsForm().exec())
        btn_del.clicked.connect(self._delete_selected)

        self.load_reviews()

    def load_reviews(self):
        reviews = list_reviews(only_published=False)
        self.table.setRowCount(len(reviews))
        for r, row in enumerate(reviews):
            values = [
                row["id"], row["author"], row["item"], row["rating"],
                row["status"], row["text"]
            ]
            for c, val in enumerate(values):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)

    def _open_add_review(self):
        dialog = ReviewForm(self.user)
        if dialog.exec():
            self.load_reviews()

    def _open_moderation(self):
        dialog = ModerationForm(self.user)
        if dialog.exec():
            self.load_reviews()

    def _delete_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        review_id = int(self.table.item(row, 0).text())
        try:
            delete_review(review_id, self.user.id, is_admin=self.user.is_admin)
            self.load_reviews()
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))