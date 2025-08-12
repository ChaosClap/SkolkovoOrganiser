import os
import json
import requests

APP_DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_data")

def get_app_data_path():
    os.makedirs(APP_DATA_PATH, exist_ok=True)
    return APP_DATA_PATH

def get_avatar_path():
    path = os.path.join(get_app_data_path(), "avatar.jpg")
    return path if os.path.exists(path) else None

def save_profile_locally(profile_data):
    profile_path = os.path.join(get_app_data_path(), "profile.json")
    with open(profile_path, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=2)

def load_profile_locally():
    profile_path = os.path.join(get_app_data_path(), "profile.json")
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_avatar_locally(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get("http://127.0.0.1:8000/auth/avatar", headers=headers)
    if response.status_code == 200:
        avatar_path = os.path.join(get_app_data_path(), "avatar.jpg")
        with open(avatar_path, "wb") as f:
            f.write(response.content)
    else:
        print("⚠ Не удалось сохранить аватар")

def get_avatar_bytes():
    avatar_path = get_avatar_path()
    if avatar_path:
        with open(avatar_path, "rb") as f:
            return f.read()
    return None

def debug_print_all_cells(doc):
    print("\n📄 Сканирование таблиц:")
    for table_idx, table in enumerate(doc.tables):
        print(f"\n[Таблица {table_idx}]")
        for row_idx, row in enumerate(table.rows):
            for cell_idx, cell in enumerate(row.cells):
                cell_text = "\n".join(p.text for p in cell.paragraphs if p.text.strip())
                print(f"  [Ячейка {row_idx},{cell_idx}] -> '{cell_text}'")
