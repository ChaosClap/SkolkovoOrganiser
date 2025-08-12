import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
import subprocess


from mentor_window import MentorWindow
from register_window import RegisterWindow
from startup_window import StartupWindow
from admin_window import AdminWindow

from validators import is_valid_credential, is_not_empty, is_min_length




API_URL = "http://127.0.0.1:8000"

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход / Регистрация")
        self.resize(400, 250)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логин")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Войти")
        self.register_button = QPushButton("Зарегистрироваться")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Имя пользователя:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.register)

    def login(self):
        try:
            username = self.username_input.text()
            password = self.password_input.text()

            if not is_not_empty(username) or not is_not_empty(password):
                QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
                return

            if not is_valid_credential(username) or not is_valid_credential(password):
                QMessageBox.warning(self, "Ошибка", "Допустимы только латинские буквы и цифры")
                return

            if not is_min_length(username, 2) or not is_min_length(password, 2):
                QMessageBox.warning(self, "Ошибка", "Логин и пароль должны быть не короче 2 символов")
                return

            response = requests.post(f"{API_URL}/auth/login", json={
                "username": username,
                "password": password
            })

            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]
                role = data.get("role", "")

                with open("token.txt", "w") as f:
                    f.write(token)

                self.hide()

                if role == "mentor":
                    self.mentor_window = MentorWindow(username=username, token=token)
                    self.mentor_window.show()
                    self.close()

                elif role == "startup":
                    self.startup_window = StartupWindow(username=username, token=token)
                    self.startup_window.show()
                    self.close()

                elif role == "admin":
                    headers = {"Authorization": f"Bearer {token}"}
                    profile_resp = requests.get(f"{API_URL}/auth/me", headers=headers)

                    if profile_resp.status_code == 200:
                        profile_data = profile_resp.json()
                        if profile_data.get("is_active") != 1:
                            QMessageBox.warning(self, "Ожидание подтверждения",
                                                "Ваш аккаунт ещё не подтверждён администратором.")
                            self.show()
                            return

                        # Всё ок, админ подтверждён
                        self.admin_window = AdminWindow(token)
                        self.admin_window.show()
                        self.close()
                    else:
                        QMessageBox.critical(self, "Ошибка", "Не удалось получить данные администратора")
                        self.show()

                else:
                    QMessageBox.critical(self, "Ошибка", f"Неизвестная роль: {role}")
                    self.show()
                    return


            else:
                QMessageBox.warning(self, "Ошибка", "Неверные данные для входа")

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            QMessageBox.critical(self, "Ошибка", f"Критическая ошибка:\n{e}")

    def register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
