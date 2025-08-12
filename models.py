from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary
from database import Base
from datetime import datetime

class FormEntry(Base):
    __tablename__ = "forms"

    id = Column(Integer, primary_key=True, index=True)
    company = Column(String)
    industry = Column(String)
    description = Column(Text)
    website = Column(String)
    technology = Column(Text)
    sales = Column(String)
    presentation = Column(String)
    goals = Column(Text)
    investment = Column(String)

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base


class StartupProfile(Base):
    __tablename__ = "startups"

    id = Column(Integer, primary_key=True)
    company_name = Column(String, nullable=False)
    company_ogrn = Column(String)
    representative_name = Column(String)
    email = Column(String)
    phone = Column(String)
    industry = Column(String)
    description = Column(Text)
    website = Column(String)
    technology = Column(Text)
    sales = Column(String)
    presentation = Column(String)
    goals = Column(Text)
    investment = Column(String)
    current_stage = Column(Text)
    six_month_plan = Column(Text)
    avatar = Column(LargeBinary, nullable=True)  # <--- вот добавка

    user = relationship("User", back_populates="startup")


class MentorProfile(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    position = Column(String)
    experience = Column(Text)
    skills = Column(Text)
    achievements = Column(Text)
    avatar = Column(LargeBinary, nullable=True)

    user = relationship("User", back_populates="mentor", uselist=False)


class AdminProfile(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    position = Column(String)
    is_active = Column(Integer, default=0)  # 0 = неактивен, 1 = активен
    user = relationship("User", back_populates="admin", uselist=False)


class AdminRequest(Base):
    __tablename__ = "admin_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "startup", "mentor", "admin"

    # nullable-ссылки на профили
    startup_id = Column(Integer, ForeignKey("startups.id"), nullable=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=True)
    admin_id = Column(Integer, ForeignKey("admins.id"), nullable=True)

    # связи
    startup = relationship("StartupProfile", back_populates="user", uselist=False)
    mentor = relationship("MentorProfile", back_populates="user", uselist=False)
    admin = relationship("AdminProfile", back_populates="user", uselist=False)






