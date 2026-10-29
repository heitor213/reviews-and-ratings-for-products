from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QComboBox, QSpinBox, QTextEdit, QPushButton,
    QMessageBox, QVBoxLayout
)
from src.db.database import db
from src.logic.reviews import create_review, ValidationError


class ReviewForm(QDialog):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Новый отзыв")
        self.resize(420, 340)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.item_combo = QComboBox()
        for item in db.fetch_all("SELECT id, title FROM items ORDER BY title"):
            self.item_combo.addItem(item["title"], item["id"])
        form.addRow("Объект:", self.item_combo)

        self.rating_spin = QSpinBox()
        self.rating_spin.setRange(1, 5)
        form.addRow("Оценка (1–5):", self.rating_spin)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Текст отзыва (не менее 10 символов)...")
        form.addRow("Отзыв:", self.text_edit)

        layout.addLayout(form)

        btn = QPushButton("Отправить на модерацию")
        btn.clicked.connect(self._submit)
        layout.addWidget(btn)

    def _submit(self):
        try:
            create_review(
                self.user.id,
                self.item_combo.currentData(),
                self.rating_spin.value(),
                self.text_edit.toPlainText(),
            )
            self.accept()
        except ValidationError as exc:
            QMessageBox.warning(self, "Ошибка валидации", str(exc))