from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QMessageBox, QHBoxLayout, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import requests
from profile_utils import (
    save_profile_locally, load_profile_locally, save_avatar_locally,
    get_avatar_path
)
import os, json


class StartupWindow(QMainWindow):
    def __init__(self, username, token):
        super().__init__()
        self.token = token
        self.username = username
        self.setWindowTitle("Интерфейс стартапа")
        self.resize(1200, 600)

        self.current_page = 0
        self.page_size = 20
        self.total_items = 0

        self.profile_data = self.get_profile_info()

        save_profile_locally(self.profile_data)
        save_avatar_locally(self.token)

        self.avatar_label_startup = QLabel()
        self.avatar_label_startup.setAlignment(Qt.AlignCenter)
        self.avatar_label_startup.setFixedSize(128, 128)
        self.load_avatar()

        self.upload_avatar_button = QPushButton("Загрузить аватар")
        self.upload_avatar_button.clicked.connect(self.upload_avatar)

        self.profile_text = QTextEdit()
        self.profile_text.setReadOnly(True)
        self.profile_text.setMinimumWidth(300)
        self.profile_text.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        self.set_profile_info()

        left_panel = QVBoxLayout()
        avatar_container = QHBoxLayout()
        avatar_container.addStretch()
        avatar_container.addWidget(self.avatar_label_startup)
        avatar_container.addStretch()

        left_panel.addLayout(avatar_container)
        left_panel.addWidget(self.upload_avatar_button)
        left_panel.addWidget(self.profile_text)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.display_mentor_details)

        center_panel = QVBoxLayout()
        center_panel.addWidget(QLabel("Список менторов"))
        center_panel.addWidget(self.list_widget)
        self.prev_button = QPushButton("← Назад")
        self.next_button = QPushButton("Вперёд →")
        self.prev_button.clicked.connect(self.prev_page)
        self.next_button.clicked.connect(self.next_page)

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.prev_button)
        nav_layout.addWidget(self.next_button)

        center_panel.addLayout(nav_layout)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMinimumWidth(400)
        self.detail_text.setStyleSheet("background-color: #f9f9f9; padding: 10px;")


        # аватар над правой панелью
        self.avatar_label_mentor = QLabel()
        self.avatar_label_mentor.setAlignment(Qt.AlignCenter)
        self.avatar_label_mentor.setFixedSize(128, 128)
        self.avatar_label_mentor.setStyleSheet("border: 1px solid gray; background-color: #eee;")

        # правая панель
        right_panel = QVBoxLayout()
        right_panel.addWidget(self.avatar_label_mentor)
        right_panel.addWidget(QLabel("Информация о менторе"))
        right_panel.addWidget(self.detail_text)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_panel)
        main_layout.addLayout(center_panel)
        main_layout.addLayout(right_panel)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.mentors = []
        self.load_mentors()

    def set_profile_info(self):
        profile = self.profile_data
        text = f"""
<b>Название компании:</b> {profile.get('company_name', '—')}<br>
<b>ОРН компании:</b> {profile.get('company_ogrn', '—')}<br>
<b>Представитель:</b> {profile.get('representative_name', '—')}<br>
<b>Индустрия:</b> {profile.get('industry', '—')}<br><br>
<b>Описание:</b><br>{profile.get('description', '—')}<br><br>
<b>Сайт:</b> {profile.get('website', '—')}<br><br>
<b>Технология:</b><br>{profile.get('technology', '—')}<br><br>
<b>Продажи:</b><br>{profile.get('sales', '—')}<br><br>
<b>Цели:</b><br>{profile.get('goals', '—')}<br><br>
<b>Инвестиции:</b><br>{profile.get('investment', '—')}<br><br>
<b>Этап:</b><br>{profile.get('current_stage', '—')}<br><br>
<b>План на 6 месяцев:</b><br>{profile.get('six_month_plan', '—')}
"""
        self.profile_text.setHtml(text)

    def update_nav_buttons(self):
        self.prev_button.setEnabled(self.current_page > 0)
        max_pages = (self.total_items - 1) // self.page_size
        self.next_button.setEnabled(self.current_page < max_pages)

    def next_page(self):
        self.current_page += 1
        self.load_mentors()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_mentors()

    def load_avatar(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get("http://127.0.0.1:8000/auth/avatar", headers=headers)
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    self.avatar_label_startup.setPixmap(
                        pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки аватара: {e}")

    def upload_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите аватар", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    filename = file_path.split("/")[-1]
                    mime_type = "image/jpeg" if filename.lower().endswith((".jpg", ".jpeg")) else "image/png"
                    files = {"file": (filename, f, mime_type)}
                    headers = {"Authorization": f"Bearer {self.token}"}
                    response = requests.post("http://127.0.0.1:8000/auth/avatar", files=files, headers=headers)
                    if response.status_code == 200:
                        self.load_avatar()
                        QMessageBox.information(self, "Успех", "Аватар обновлён")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки: {e}")

    def get_profile_info(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = requests.get("http://127.0.0.1:8000/auth/me", headers=headers)
        if response.status_code == 200:
            return response.json()
        return {}

    def load_mentors(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            skip = self.current_page * self.page_size
            url = f"http://127.0.0.1:8000/api/mentors?skip={skip}&limit={self.page_size}"
            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                self.total_items = data["total"]
                self.mentors = data["items"]

                self.list_widget.clear()
                for m in self.mentors:
                    self.list_widget.addItem(m.get("full_name", "Без имени"))

                self.update_nav_buttons()

            else:
                QMessageBox.warning(self, "Ошибка", f"Код {response.status_code}: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки списка менторов: {e}")

    def display_mentor_details(self, index):
        if index == -1:
            self.detail_text.clear()
            return
        mentor_id = self.mentors[index].get("id")
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = requests.get(f"http://127.0.0.1:8000/api/mentors/{mentor_id}", headers=headers)
            if response.status_code == 200:
                m = response.json()
                details = f"""
<b>ФИО:</b> {m.get('full_name', '—')}<br>
<b>Должность:</b> {m.get('position', '—')}<br><br>
<b>Опыт:</b><br>{m.get('experience', '—')}<br><br>
<b>Компетенции:</b><br>{m.get('skills', '—')}<br><br>
<b>Достижения:</b><br>{m.get('achievements', '—')}
"""
                self.detail_text.setHtml(details)

                # Получаем аватар (если есть)
            r_avatar = requests.get(f"http://127.0.0.1:8000/api/mentors/{mentor_id}/avatar", headers=headers)
            if r_avatar.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(r_avatar.content):
                    self.avatar_label_mentor.setPixmap(
                        pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.avatar_label_mentor.clear()
            else:
                self.avatar_label_mentor.clear()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки деталей: {e}")
