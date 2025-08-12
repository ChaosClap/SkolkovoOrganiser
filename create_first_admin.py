from database import SessionLocal
from models import User, AdminProfile
from auth_utils import hash_password

db = SessionLocal()

username = "admin"
password = "admin123"

# Проверка на существование
existing = db.query(User).filter(User.username == username).first()
if existing:
    print("Пользователь с таким логином уже существует.")
else:
    # Создаём профиль админа
    admin = AdminProfile(
        full_name="Главный админ",
        position="Администратор платформы",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)

    # Создаём пользователя
    user = User(
        username=username,
        hashed_password=hash_password(password),
        role="admin",
        admin_id=admin.id
    )
    db.add(user)
    db.commit()
    print("✅ Первый админ создан:", username)



