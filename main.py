import sys
from PyQt6.QtWidgets import QApplication
from src.ui.login_window import LoginWindow
from src.ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    login = LoginWindow()
    if login.exec() != LoginWindow.DialogCode.Accepted:
        return
    window = MainWindow(login.user)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()