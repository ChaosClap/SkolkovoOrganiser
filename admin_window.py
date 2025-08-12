from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QListWidget, QTextEdit,
    QPushButton, QHBoxLayout, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt
import requests


class AdminWindow(QMainWindow):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setWindowTitle("Панель администратора")
        self.resize(800, 500)

        self.requests = []
        self.selected_request = None

        # Виджеты
        self.list_widget = QListWidget()
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.approve_button = QPushButton("Одобрить заявку")

        self.list_widget.currentRowChanged.connect(self.display_request_details)
        self.approve_button.clicked.connect(self.approve_request)

        # Разметка
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Заявки на админку:"))
        left_layout.addWidget(self.list_widget)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Информация:"))
        right_layout.addWidget(self.detail_text)
        right_layout.addWidget(self.approve_button)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_requests()

    def load_requests(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        print(headers)
        response = requests.get("http://127.0.0.1:8000/admin/requests", headers=headers)

        if response.status_code == 200:
            data = response.json()
            self.requests = data["items"]
            self.list_widget.clear()

            for req in self.requests:
                self.list_widget.addItem(f"{req.get('full_name') or '—'} ({req.get('position') or '—'})")


        else:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить заявки")

    def display_request_details(self, index):
        if index < 0 or index >= len(self.requests):
            self.selected_request = None
            self.detail_text.clear()
            return

        request = self.requests[index]
        self.selected_request = request
        text = f"""
    <b>ФИО:</b> {request.get("full_name", "—")}<br>
    <b>Должность:</b> {request.get("position", "—")}<br>
    <b>Логин:</b> {request.get("username", "—")}<br>
    <b>ID пользователя:</b> {request.get("user_id", "—")}<br>
    <b>ID заявки:</b> {request.get("request_id", "—")}<br>
    """
        self.detail_text.setHtml(text)

    def approve_request(self):
        if not self.selected_request:
            QMessageBox.warning(self, "Ошибка", "Заявка не выбрана")
            return

        request_id = self.selected_request.get("request_id")
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            print(f"'{self.token}'")


            r = requests.post(f"http://127.0.0.1:8000/admin/approve/{request_id}", headers=headers)
            if r.status_code == 200:
                QMessageBox.information(self, "Успех", "Заявка одобрена")

                # Удаляем заявку из списка без полной перезагрузки
                index = self.list_widget.currentRow()
                if index != -1:
                    self.list_widget.takeItem(index)
                    self.requests.pop(index)

                self.detail_text.clear()
            else:
                QMessageBox.warning(self, "Ошибка", r.text)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

