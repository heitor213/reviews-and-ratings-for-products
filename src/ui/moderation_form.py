from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from src.logic.reviews import list_reviews, moderate_review


class ModerationForm(QDialog):
    def __init__(self, admin):
        super().__init__()
        self.admin = admin
        self.setWindowTitle("Модерация отзывов")
        self.resize(800, 480)

        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Автор", "Объект", "Оценка", "Статус"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        btns = QHBoxLayout()
        btn_approve = QPushButton("Опубликовать")
        btn_reject = QPushButton("Отклонить")
        btn_refresh = QPushButton("Обновить")
        btns.addWidget(btn_approve)
        btns.addWidget(btn_reject)
        btns.addStretch()
        btns.addWidget(btn_refresh)
        layout.addLayout(btns)

        btn_approve.clicked.connect(lambda: self._moderate(True))
        btn_reject.clicked.connect(lambda: self._moderate(False))
        btn_refresh.clicked.connect(self.load)
        self.load()

    def load(self):
        rows = list_reviews(only_published=False)
        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate([row["id"], row["author"], row["item"], row["rating"], row["status"]]):
                item = QTableWidgetItem(str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(r, c, item)

    def _moderate(self, approve: bool):
        row = self.table.currentRow()
        if row < 0:
            return
        review_id = int(self.table.item(row, 0).text())
        try:
            moderate_review(review_id, self.admin.id, approve)
            self.load()
        except Exception as exc:
            QMessageBox.warning(self, "Ошибка", str(exc))