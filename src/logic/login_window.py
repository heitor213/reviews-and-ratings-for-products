from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
)
from src.logic.auth import authenticate


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация — Модуль отзывов")
        self.setFixedSize(340, 190)
        self.user = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Логин:"))
        self.login_edit = QLineEdit()
        layout.addWidget(self.login_edit)

        layout.addWidget(QLabel("Пароль:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_edit)

        btn = QPushButton("Войти")
        btn.clicked.connect(self._on_login)
        layout.addWidget(btn)

    def _on_login(self):
        user = authenticate(self.login_edit.text().strip(), self.password_edit.text())
        if not user:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль.")
            return
        self.user = user
        self.accept()