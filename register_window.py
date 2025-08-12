from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QMessageBox, QSizePolicy, QFormLayout
)
from PyQt5.QtCore import QTimer, Qt
import requests

from validators import is_valid_credential, is_not_empty, is_min_length

API_URL = "http://127.0.0.1:8000"


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация")
        self.resize(400, 600)

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.role_selection_ui()

    def role_selection_ui(self):
        """Первый экран — выбор роли"""
        self.clear_layout()

        label = QLabel("Выберите, кто вы:")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            font-size: 18pt;
            font-weight: 500;
            margin-top: 20px;
            margin-bottom: 30px;
        """)

        mentor_btn = QPushButton("Я — ментор")
        startup_btn = QPushButton("Я — представитель стартапа")
        staff_btn = QPushButton("Я — сотрудник Сколково")

        for btn in (mentor_btn, startup_btn, staff_btn):
            btn.setMinimumHeight(48)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e2e8f0;  /* светло-серый фон */
                    color: #1e293b;              /* тёмно-серый текст */
                    border: 1px solid #cbd5e1;
                    border-radius: 4px;
                    font-size: 14pt;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #cbd5e1;
                }
                QPushButton:pressed {
                    background-color: #94a3b8;
                    color: white;
                }
            """)

        mentor_btn.clicked.connect(self.show_mentor_form)
        startup_btn.clicked.connect(self.show_startup_form)
        staff_btn.clicked.connect(self.show_staff_form)

        self.layout.addWidget(label)
        self.layout.addWidget(mentor_btn)
        self.layout.addWidget(startup_btn)
        self.layout.addWidget(staff_btn)
        self.layout.addStretch()

    def show_mentor_form(self):
        self.clear_layout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_repeat_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_repeat_input.setEchoMode(QLineEdit.Password)

        self.fullname_input = QLineEdit()
        self.position_input = QLineEdit()
        self.experience_input = QTextEdit()
        self.skills_input = QTextEdit()
        self.achievements_input = QTextEdit()

        self.register_button = QPushButton("Зарегистрироваться")
        self.register_button.clicked.connect(self.send_registration)

        layout = self.layout
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Повторите пароль:"))
        layout.addWidget(self.password_repeat_input)
        layout.addWidget(QLabel("⚠ Эти данные пригодятся для быстрого заполнения файлов. Их можно будет изменить позже."))
        layout.addWidget(QLabel("ФИО:"))
        layout.addWidget(self.fullname_input)
        layout.addWidget(QLabel("Должность:"))
        layout.addWidget(self.position_input)
        layout.addWidget(QLabel("Опыт:"))
        layout.addWidget(self.experience_input)
        layout.addWidget(QLabel("Компетенции:"))
        layout.addWidget(self.skills_input)
        layout.addWidget(QLabel("Достижения:"))
        layout.addWidget(self.achievements_input)
        layout.addWidget(self.register_button)

    def show_startup_form(self):
        self.clear_layout()

        self.setWindowTitle("Регистрация стартапа")

        layout = self.layout

        label = QLabel("Регистрация представителя стартапа")
        label.setStyleSheet("font-size: 16pt; font-weight: bold; margin-bottom: 12px;")
        layout.addWidget(label)



        # Поля
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_repeat_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_repeat_input.setEchoMode(QLineEdit.Password)

        self.company_name = QLineEdit()
        self.company_ogrn = QLineEdit()
        self.representative_name = QLineEdit()
        self.representative_email = QLineEdit()
        self.representative_phone = QLineEdit()
        self.industry = QLineEdit()
        self.product_description = QTextEdit()
        self.website = QLineEdit()
        self.technology = QTextEdit()
        self.sales = QLineEdit()
        self.presentation = QLineEdit()
        self.goals = QTextEdit()
        self.investment = QLineEdit()
        self.current_stage = QTextEdit()
        self.near_term_plan = QTextEdit()

        form = QFormLayout()
        form.addRow("Логин:", self.username_input)
        form.addRow("Пароль:", self.password_input)
        form.addRow("Повторите пароль:", self.password_repeat_input)
        form.addRow("Наименование компании:", self.company_name)
        form.addRow("ОРН компании (при наличии):", self.company_ogrn)
        form.addRow("ФИО представителя:", self.representative_name)
        form.addRow("Email представителя:", self.representative_email)
        form.addRow("Телефон представителя:", self.representative_phone)
        form.addRow("Отрасль деятельности:", self.industry)
        form.addRow("Описание продукта/услуги:", self.product_description)
        form.addRow("Сайт / каталог:", self.website)
        form.addRow("Технология:", self.technology)
        form.addRow("Объем продаж (12 мес):", self.sales)
        form.addRow("Ссылка на презентацию:", self.presentation)
        form.addRow("Планируемые результаты:", self.goals)
        form.addRow("Поиск инвестиций:", self.investment)
        form.addRow("Текущая ситуация / запрос:", self.current_stage)
        form.addRow("Цели на 6 мес и год:", self.near_term_plan)

        layout.addLayout(form)

        self.register_button = QPushButton("Зарегистрировать стартап")
        layout.addWidget(self.register_button)


        self.register_button.clicked.connect(self.send_startup_registration)

    def show_staff_form(self):
        self.clear_layout()

        self.setWindowTitle("Регистрация сотрудника Сколково")

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_repeat_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_repeat_input.setEchoMode(QLineEdit.Password)

        self.fullname_input = QLineEdit()
        self.position_input = QLineEdit()

        layout = self.layout
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(QLabel("Повторите пароль:"))
        layout.addWidget(self.password_repeat_input)
        layout.addWidget(QLabel("ФИО:"))
        layout.addWidget(self.fullname_input)
        layout.addWidget(QLabel("Должность:"))
        layout.addWidget(self.position_input)

        self.register_button = QPushButton("Зарегистрироваться как сотрудник")
        self.register_button.clicked.connect(self.send_staff_registration)
        layout.addWidget(self.register_button)

    def send_staff_registration(self):
        username = self.username_input.text()
        password = self.password_input.text()
        password_repeat = self.password_repeat_input.text()

        if not is_not_empty(username) or not is_not_empty(password):
            QMessageBox.warning(self, "Ошибка", "Логин и пароль не должны быть пустыми")
            return

        if password != password_repeat:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        try:
            data = {
                "username": username,
                "password": password,
                "full_name": self.fullname_input.text(),
                "position": self.position_input.text()
            }

            response = requests.post(f"{API_URL}/auth/register_staff", json=data)

            if response.status_code == 200:
                QMessageBox.information(self, "Успешно", "Заявка отправлена администраторам")
                self.close()
            else:
                detail = response.json().get("detail", "Ошибка регистрации")
                QMessageBox.warning(self, "Ошибка", detail)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения", str(e))

    def send_startup_registration(self):
        from validators import is_not_empty, is_valid_credential, is_min_length

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        repeat = self.password_repeat_input.text().strip()

        if not all([is_not_empty(username), is_not_empty(password)]):
            QMessageBox.warning(self, "Ошибка", "Логин и пароль не должны быть пустыми")
            return

        if not is_valid_credential(username) or not is_valid_credential(password):
            QMessageBox.warning(self, "Ошибка", "Логин и пароль могут содержать только латинские буквы и цифры")
            return

        if not is_min_length(username, 2) or not is_min_length(password, 2):
            QMessageBox.warning(self, "Ошибка", "Минимальная длина логина и пароля — 2 символа")
            return

        if password != repeat:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        # Проверка остальных полей (по минимуму — на пустоту)
        required_fields = [
            self.company_name.text(), self.representative_name.text(),
            self.representative_email.text(), self.representative_phone.text(),
            self.industry.text(), self.product_description.toPlainText(),
            self.website.text(), self.technology.toPlainText()
        ]

        if not all(is_not_empty(f) for f in required_fields):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля")
            return

        # Сбор и отправка данных
        data = {
            "username": username,
            "password": password,
            "role": "startup",
            "company_name": self.company_name.text(),
            "company_ogrn": self.company_ogrn.text(),
            "representative_name": self.representative_name.text(),
            "email": self.representative_email.text(),
            "phone": self.representative_phone.text(),
            "industry": self.industry.text(),
            "description": self.product_description.toPlainText(),
            "website": self.website.text(),
            "technology": self.technology.toPlainText(),
            "sales": self.sales.text(),
            "presentation": self.presentation.text(),
            "goals": self.goals.toPlainText(),
            "investment": self.investment.text(),
            "current_stage": self.current_stage.toPlainText(),
            "six_month_plan": self.near_term_plan.toPlainText()

        }

        try:
            response = requests.post(f"{API_URL}/auth/register_startup", json=data)
            if response.status_code == 200:
                QMessageBox.information(self, "Успешно", "Стартап зарегистрирован")
                self.close()
            else:
                detail = response.json().get("detail", "Ошибка регистрации")
                QMessageBox.warning(self, "Ошибка", detail)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения", str(e))

    def clear_layout(self):
        """Удаляет все виджеты из layout"""
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)


    def send_registration(self):
        username = self.username_input.text()
        password = self.password_input.text()
        password_repeat = self.password_repeat_input.text()

        if not is_not_empty(username) or not is_not_empty(password):
            QMessageBox.warning(self, "Ошибка", "Логин и пароль не должны быть пустыми")
            return

        if not is_valid_credential(username) or not is_valid_credential(password):
            QMessageBox.warning(self, "Ошибка", "Логин и пароль могут содержать только латинские буквы и цифры")
            return

        if not is_min_length(username, 2) or not is_min_length(password, 2):
            QMessageBox.warning(self, "Ошибка", "Логин и пароль должны быть не короче 2 символов")
            return

        if password != password_repeat:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return

        try:
            data = {
                "username": username,
                "password": password,
                "role": "mentor",
                "full_name": self.fullname_input.text(),
                "position": self.position_input.text(),
                "experience": self.experience_input.toPlainText(),
                "skills": self.skills_input.toPlainText(),
                "achievements": self.achievements_input.toPlainText()
            }

            response = requests.post(f"{API_URL}/auth/register_mentor", json=data)

            if response.status_code == 200:
                QMessageBox.information(self, "Успешно", "Регистрация завершена!")
                QTimer.singleShot(0, self.close)
            else:
                try:
                    detail = response.json().get("detail", "Ошибка регистрации")
                except Exception:
                    detail = response.text or "Ошибка регистрации (некорректный ответ от сервера)"
                QMessageBox.warning(self, "Ошибка", detail)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка подключения", str(e))

