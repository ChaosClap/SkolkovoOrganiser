import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException, Header, status, UploadFile, File, Response, Query, APIRouter
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from auth_utils import verify_password, create_access_token
import io
from schemas import AdminRequestOut


from database import SessionLocal, engine
from models import User, StartupProfile, MentorProfile, AdminRequest, AdminProfile
from database import Base
from datetime import datetime
from typing import Dict, List, Union


from auth_utils import hash_password, decode_token #auth_utils.py

from fastapi import Header, Depends
from jose import JWTError

from fastapi.responses import JSONResponse, FileResponse
from models import FormEntry, AdminRequest
from schemas import StartupRegister, MentorRegister, MentorOut, StartupOut, AdminRequestCreate, AdminRegister






CURRENT_VERSION = "1.0"
EXE_PATH = "SkolkovoOrganiser.exe"

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Создаем таблицы (один раз)
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

# Определение полей анкеты
fields = [
    {"label": "Название компании", "name": "company", "type": "text"},
    {"label": "Отрасль деятельности", "name": "industry", "type": "text"},
    {"label": "Описание продукта/услуги", "name": "description", "type": "textarea"},
    {"label": "Ссылка на сайт / каталог", "name": "website", "type": "text"},
    {"label": "Технология, лежащая в основе продукта", "name": "technology", "type": "textarea"},
    {"label": "Объем продаж за последние 12 месяцев", "name": "sales", "type": "text"},
    {"label": "Ссылка на презентацию", "name": "presentation", "type": "text"},
    {"label": "Ключевые планируемые результаты до конца года", "name": "goals", "type": "textarea"},
    {"label": "Поиск инвестиций до конца года (объем)", "name": "investment", "type": "text"},
]



@app.get("/latest-version", response_class=PlainTextResponse)
def get_latest_version():
    with open("version.txt", "r") as f:
        return f.read().strip()

@app.get("/SkolkovoOrganiser.zip")
def get_zip():
    zip_path = os.path.abspath(os.path.join("dist", "SkolkovoOrganiser.zip"))
    if not os.path.exists(zip_path):
        raise HTTPException(status_code=404, detail="ZIP-файл не найден")
    return FileResponse(zip_path, media_type="application/zip")

# НУЖЕН ДОМЕН ИЛИ ЧТО-ТО, ОТКУДА БУДЕМ КАЧАТЬ SETUP ФАЙЛ


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("form.html", {
        "request": request,
        "fields": fields,
        "success": False,
        "form_values": {}
    })


@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    company: str = Form(...),
    industry: str = Form(...),
    description: str = Form(...),
    website: str = Form(...),
    technology: str = Form(...),
    sales: str = Form(...),
    presentation: str = Form(...),
    goals: str = Form(...),
    investment: str = Form(...),
):
    form_data = {
        "company": company,
        "industry": industry,
        "description": description,
        "website": website,
        "technology": technology,
        "sales": sales,
        "presentation": presentation,
        "goals": goals,
        "investment": investment,
    }

    try:
        db: Session = SessionLocal()
        entry = FormEntry(**form_data)
        db.add(entry)
        db.commit()
        db.close()
        success = True
    except Exception as e:
        print("Ошибка при сохранении:", e)
        success = False

    form_values = {} if success else form_data

    return templates.TemplateResponse("form.html", {
        "request": request,
        "fields": fields,
        "success": success,
        "form_values": form_values
    })

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "mentor"
    full_name: str = ""
    position: str = ""
    experience: str = ""
    skills: str = ""
    achievements: str = ""

@app.post("/auth/register")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        role=user_data.role,
        full_name=user_data.full_name,
        position=user_data.position,
        experience=user_data.experience,
        skills=user_data.skills,
        achievements=user_data.achievements
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Пользователь успешно зарегистрирован", "user_id": user.id}


@app.post("/auth/register_startup")
def register_startup(data: StartupRegister, db: Session = Depends(get_db)):
    # Проверка на уникальность логина
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")

    # Создаём профиль стартапа
    startup = StartupProfile(
        company_name=data.company_name,
        company_ogrn=data.company_ogrn,
        representative_name=data.representative_name,
        email=data.email,
        phone=data.phone,
        industry=data.industry,
        description=data.description,
        website=data.website,
        technology=data.technology,
        sales=data.sales,
        presentation=data.presentation,
        goals=data.goals,
        investment=data.investment,
        current_stage=data.current_stage,
        six_month_plan=data.six_month_plan
    )
    db.add(startup)
    db.commit()
    db.refresh(startup)

    # Создаём пользователя и связываем с профилем
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        role="startup",
        startup_id=startup.id
    )
    db.add(user)
    db.commit()

    return {"message": "Стартап успешно зарегистрирован", "startup_id": startup.id, "user_id": user.id}

@app.post("/auth/register_mentor")
def register_mentor(data: MentorRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")

    mentor = MentorProfile(
        full_name=data.full_name,
        position=data.position,
        experience=data.experience,
        skills=data.skills,
        achievements=data.achievements
    )
    db.add(mentor)
    db.commit()
    db.refresh(mentor)

    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        role="mentor",
        mentor_id=mentor.id
    )
    db.add(user)
    db.commit()

    return {"message": "Ментор зарегистрирован", "mentor_id": mentor.id, "user_id": user.id}

@app.post("/auth/login", response_model=Token)
def login_user(form_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные имя пользователя или пароль")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": token,
        "role": user.role
    }




def get_current_user(token: str = Header(..., alias="Authorization"), db: Session = Depends(get_db)):
    print("🔥 RAW HEADER:", token)
    if token.startswith("Bearer "):
        token = token[7:]

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Неверный токен")

    user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return user

@app.get("/auth/me")
def get_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "mentor":
        mentor = db.query(MentorProfile).filter(MentorProfile.id == current_user.mentor_id).first()
        if not mentor:
            raise HTTPException(status_code=404, detail="Профиль ментора не найден")
        return {
            "full_name": mentor.full_name,
            "position": mentor.position,
            "experience": mentor.experience,
            "skills": mentor.skills,
            "achievements": mentor.achievements
        }

    elif current_user.role == "startup":
        startup = db.query(StartupProfile).filter(StartupProfile.id == current_user.startup_id).first()
        if not startup:
            raise HTTPException(status_code=404, detail="Профиль стартапа не найден")
        return {
            "company_name": startup.company_name,
            "company_ogrn": startup.company_ogrn,
            "representative_name": startup.representative_name,
            "email": startup.email,
            "phone": startup.phone,
            "industry": startup.industry,
            "description": startup.description,
            "website": startup.website,
            "technology": startup.technology,
            "sales": startup.sales,
            "presentation": startup.presentation,
            "goals": startup.goals,
            "investment": startup.investment,
            "current_stage": startup.current_stage,
            "six_month_plan": startup.six_month_plan
        }


    elif current_user.role == "admin":
        admin = db.query(AdminProfile).filter(AdminProfile.id == current_user.admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Профиль администратора не найден")
        return {
            "full_name": admin.full_name,
            "position": admin.position,
            "is_active": admin.is_active
        }


    else:
        raise HTTPException(status_code=400, detail="Неизвестная роль")



@app.post("/auth/avatar")
def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type not in ["image/png", "image/jpeg"]:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат изображения")

    avatar_bytes = file.file.read()

    if user.role == "mentor" and user.mentor:
        user.mentor.avatar = avatar_bytes
    elif user.role == "startup" and user.startup:
        user.startup.avatar = avatar_bytes
    else:
        raise HTTPException(status_code=400, detail="Аватар можно загрузить только для стартапа или ментора")

    db.commit()
    return {"message": "Аватар успешно сохранён"}



@app.get("/auth/avatar")
def get_avatar(user: User = Depends(get_current_user)):
    avatar = None
    if user.role == "mentor" and user.mentor:
        avatar = user.mentor.avatar
    elif user.role == "startup" and user.startup:
        avatar = user.startup.avatar

    if not avatar:
        raise HTTPException(status_code=404, detail="Аватар не найден")

    return Response(content=avatar, media_type="image/png")



@router.get("/mentors", response_class=JSONResponse)
def get_mentors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(MentorProfile)
    if search:
        query = query.filter(MentorProfile.full_name.ilike(f"%{search}%"))

    total = query.count()
    mentors = query.offset(skip).limit(limit).all()

    result = [
        {
            "id": m.id,
            "full_name": m.full_name
        }
        for m in mentors
    ]
    return {"total": total, "items": result}



@router.get("/mentors/{mentor_id}", response_model=MentorOut)
def get_mentor_by_id(mentor_id: int, db: Session = Depends(get_db)):
    mentor = db.query(MentorProfile).filter(MentorProfile.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Ментор не найден")
    return mentor

@router.get("/mentors/{mentor_id}/avatar")
def get_mentor_avatar(mentor_id: int, db: Session = Depends(get_db)):
    mentor = db.query(MentorProfile).filter(MentorProfile.id == mentor_id).first()
    if not mentor or not mentor.avatar:
        raise HTTPException(status_code=404, detail="Аватар не найден")
    return Response(content=mentor.avatar, media_type="image/png")



# аналогично только теперь для стартапов

@router.get("/startups")
def get_startups(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(StartupProfile)
    total = query.count()
    startups = query.offset(skip).limit(limit).all()

    items = [
        {
            "id": s.id,
            "company_name": s.company_name
        }
        for s in startups
    ]

    return {
        "total": total,
        "items": items
    }


@router.get("/startups/{startup_id}")
def get_startup_by_id(startup_id: int, db: Session = Depends(get_db)):
    startup = db.query(StartupProfile).filter(StartupProfile.id == startup_id).first()
    if not startup:
        raise HTTPException(status_code=404, detail="Стартап не найден")
    return {
        "id": startup.id,
        "company_name": startup.company_name,
        "company_ogrn": startup.company_ogrn,
        "representative_name": startup.representative_name,
        "email": startup.email,
        "phone": startup.phone,
        "industry": startup.industry,
        "description": startup.description,
        "website": startup.website,
        "technology": startup.technology,
        "sales": startup.sales,
        "presentation": startup.presentation,
        "goals": startup.goals,
        "investment": startup.investment,
        "current_stage": startup.current_stage,
        "six_month_plan": startup.six_month_plan,
    }


@router.get("/startups/{startup_id}/avatar")
def get_startup_avatar(startup_id: int, db: Session = Depends(get_db)):
    startup = db.query(StartupProfile).filter(StartupProfile.id == startup_id).first()
    if not startup or not startup.avatar:
        raise HTTPException(status_code=404, detail="Аватар не найден")
    return Response(content=startup.avatar, media_type="image/png")



@app.post("/admin/request")
def request_admin_access(data: AdminRequestCreate, db: Session = Depends(get_db)):
    # уже админ?
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(404, detail="Пользователь не найден")
    if user.role == "admin" and user.admin and user.admin.is_active == 1:
        raise HTTPException(400, detail="Пользователь уже админ")

    # заявка уже существует?
    existing = db.query(AdminRequest).filter_by(user_id=data.user_id).first()
    if existing:
        raise HTTPException(400, detail="Заявка уже подана")

    req = AdminRequest(user_id=data.user_id, created_at=datetime.utcnow())
    db.add(req)
    db.commit()
    db.refresh(req)
    return {"message": "Заявка подана", "request_id": req.id}

def get_current_active_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin" or not user.admin or not user.admin.is_active:
        raise HTTPException(status_code=403, detail="Доступ только для подтверждённых админов")
    return user



@app.get("/admin/requests", response_model=Dict[str, Union[int, List[AdminRequestOut]]])
def get_admin_requests(
    current_user: User = Depends(get_current_active_admin),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=100)
):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Доступ запрещён")

    query = (
        db.query(AdminRequest)
        .join(User)
        .join(AdminProfile, AdminProfile.id == User.admin_id)
        .filter(AdminProfile.is_active == 0)  # <--- ВАЖНО
        .order_by(AdminRequest.created_at.desc())
    )

    total = query.count()
    requests = query.offset(skip).limit(limit).all()

    items = []
    for req in requests:
        user = req.user
        role = user.role

        if role == "mentor" and user.mentor:
            full_name = user.mentor.full_name
            position = user.mentor.position
        elif role == "admin" and user.admin:
            full_name = user.admin.full_name
            position = user.admin.position
        else:
            full_name = "—"
            position = "—"

        items.append({
            "request_id": req.id,
            "user_id": user.id,
            "username": user.username,
            "created_at": req.created_at,
            "role": role,
            "full_name": full_name,
            "position": position,
        })

    return {
        "total": total,
        "items": items
    }



@app.post("/admin/approve/{user_id}")
def approve_admin_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Только админ может одобрять
    if current_user.role != "admin":
        raise HTTPException(403, detail="Доступ запрещён")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, detail="Пользователь не найден")

    # Проверим, есть ли заявка
    request = db.query(AdminRequest).filter_by(user_id=user_id).first()
    if not request:
        raise HTTPException(404, detail="Заявка не найдена")

    # Создаём профиль админа
    admin_profile = AdminProfile(
        full_name=user.username,  # можно заменить если нужно
        position="",
        is_active=1
    )
    db.add(admin_profile)
    db.commit()
    db.refresh(admin_profile)

    # Обновляем пользователя
    user.role = "admin"
    user.admin_id = admin_profile.id
    db.delete(request)
    db.commit()

    return {"message": "Пользователь назначен админом"}


@app.post("/admin/reject/{user_id}")
def reject_admin_request(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(403, detail="Доступ запрещён")

    request = db.query(AdminRequest).filter_by(user_id=user_id).first()
    if not request:
        raise HTTPException(404, detail="Заявка не найдена")

    db.delete(request)
    db.commit()
    return {"message": "Заявка отклонена"}


@app.post("/auth/register_staff")
def register_staff(data: AdminRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")

    # создаём профиль админа
    admin_profile = AdminProfile(
        full_name=data.full_name,
        position=data.position,
        is_active=0
    )
    db.add(admin_profile)
    db.flush()  # получаем ID до коммита

    # создаём юзера с ролью "admin" и привязкой к профилю
    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        role="admin",
        admin_id=admin_profile.id
    )
    db.add(user)
    db.flush()

    # связываем профиль с юзером (обратная связь)
    admin_profile.user = user

    # создаём заявку
    if db.query(AdminRequest).filter_by(user_id=user.id).first():
        raise HTTPException(status_code=400, detail="Заявка уже существует")

    request = AdminRequest(user_id=user.id, created_at=datetime.utcnow())
    db.add(request)
    db.commit()

    return {"message": "Заявка отправлена администраторам"}


    @router.post("/admin/approve/{request_id}")
    def approve_admin_request(
            request_id: int,
            data: AdminRegister,
            db: Session = Depends(get_db),
            current_admin: User = Depends(get_current_active_admin)  # <--- заменили
    ):
        admin_request = db.query(AdminRequest).filter_by(id=request_id).first()
        if not admin_request:
            raise HTTPException(status_code=404, detail="Заявка не найдена")

        user = db.query(User).filter_by(id=admin_request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if user.admin_id is not None:
            raise HTTPException(status_code=400, detail="Пользователь уже является администратором")

        profile = user.admin
        if not profile:
            raise HTTPException(status_code=400, detail="Профиль администратора не найден")

        # Обновляем и активируем
        profile.full_name = data.full_name
        profile.position = data.position
        profile.is_active = 1




        db.add(user)
        db.delete(admin_request)
        db.commit()

        return {"message": "Администратор подтверждён"}





# ВСЕГДА В КОНЦЕ!
app.include_router(router)



