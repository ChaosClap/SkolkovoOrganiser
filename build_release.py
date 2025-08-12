import subprocess
import os
import zipfile
import shutil

EXE_NAME = "SkolkovoOrganiser.exe"
UPDATER_NAME = "Updater.exe"
VERSION_FILE = "version.txt"
ZIP_NAME = "SkolkovoOrganiser.zip"

def build_exe(script_name, exe_name):
    print(f"⚙️  Собираем {exe_name} из {script_name}...")
    subprocess.run([
        "pyinstaller", "--noconfirm", "--onefile", "--windowed",
        "--name", exe_name.replace(".exe", ""),
        script_name
    ])

def increment_version():
    print("🔢 Инкремент версии...")
    if not os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "w") as f:
            f.write("1.0")
        return "1.0"

    with open(VERSION_FILE, "r") as f:
        current = f.read().strip()

    parts = current.split(".")
    if len(parts) == 2:
        major, minor = map(int, parts)
        minor += 1
        new_version = f"{major}.{minor}"
    elif len(parts) == 3:
        major, minor, patch = map(int, parts)
        patch += 1
        new_version = f"{major}.{minor}.{patch}"
    else:
        new_version = "1.0"

    with open(VERSION_FILE, "w") as f:
        f.write(new_version)

    print(f"✅ Новая версия: {new_version}")
    return new_version

def collect_files(version):
    print("📦 Создание архива...")
    dist_path = "dist"
    zip_path = os.path.join(dist_path, ZIP_NAME)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in [
            os.path.join(dist_path, EXE_NAME),
           # os.path.join(dist_path, UPDATER_NAME),
            "startup_template.docx",
            "app_icon.ico",
            VERSION_FILE
        ]:
            if os.path.exists(file):
                arcname = os.path.basename(file)
                zipf.write(file, arcname)
                print(f" + {arcname}")
            else:
                print(f"⚠ Файл не найден: {file}")

    print(f"\n🎉 Архив готов: {zip_path}")

def clean_pyinstaller_artifacts():
    for d in ["build", "__pycache__"]:
        if os.path.exists(d):
            shutil.rmtree(d)
    for spec in [f for f in os.listdir() if f.endswith(".spec")]:
        os.remove(spec)

def main():
    clean_pyinstaller_artifacts()
    build_exe("login_window.py", EXE_NAME)
    build_exe("updater.py", UPDATER_NAME)
    version = increment_version()
    collect_files(version)

if __name__ == "__main__":
    main()
