import requests
import os
import zipfile
import shutil
import subprocess
import time
import sys

API_URL = "http://127.0.0.1:8000"
REMOTE_VERSION_URL = f"{API_URL}/latest-version"
REMOTE_ZIP_URL = f"{API_URL}/SkolkovoOrganiser.zip"
APP_DIR = os.getcwd()
TMP_ZIP = "update_tmp.zip"
MAIN_EXE = "SkolkovoOrganiser.exe"
VERSION_FILE = "version.txt"

def get_local_version():
    path = os.path.join(APP_DIR, VERSION_FILE)
    if not os.path.exists(path):
        return "0.0"
    with open(path, "r") as f:
        return f.read().strip()

def get_remote_version():
    try:
        return requests.get(REMOTE_VERSION_URL, timeout=5).text.strip()
    except:
        return None

def download_and_extract_zip():
    response = requests.get(REMOTE_ZIP_URL, stream=True)
    with open(TMP_ZIP, "wb") as f:
        for chunk in response.iter_content(1024):
            f.write(chunk)
    with zipfile.ZipFile(TMP_ZIP, "r") as zip_ref:
        zip_ref.extractall(APP_DIR)
    os.remove(TMP_ZIP)

def run_main_app():
    if not os.path.exists(MAIN_EXE):
        print(f"❌ Не найден {MAIN_EXE} по пути: {os.path.abspath(MAIN_EXE)}")
        return
    subprocess.Popen([MAIN_EXE])
    time.sleep(1)
    sys.exit()

def main():
    local = get_local_version()
    remote = get_remote_version()

    if remote and remote != local:
        print(f"🔁 Обновление {local} → {remote}")
        download_and_extract_zip()
        with open(os.path.join(APP_DIR, VERSION_FILE), "w") as f:
            f.write(remote)
    else:
        print("✅ Уже последняя версия")

    run_main_app()

if __name__ == "__main__":
    main()


