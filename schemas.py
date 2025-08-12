from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Union


class StartupRegister(BaseModel):
    username: str
    password: str
    company_name: str
    company_ogrn: str
    representative_name: str
    email: str
    phone: str
    industry: str
    description: str
    website: str
    technology: str
    sales: str
    presentation: str
    goals: str
    investment: str
    current_stage: str
    six_month_plan: str

class MentorRegister(BaseModel):
    username: str
    password: str
    full_name: str
    position: str
    experience: str
    skills: str
    achievements: str

class MentorOut(BaseModel):
    id: int
    full_name: str
    position: str
    experience: str
    skills: str
    achievements: str

    class Config:
        orm_mode = True

class AdminRequestCreate(BaseModel):
    user_id: int


class StartupOut(BaseModel):
    id: int
    company_name: str
    company_ogrn: str
    representative_name: str
    email: str
    phone: str
    industry: str
    description: str
    website: str
    technology: str
    sales: str
    presentation: str
    goals: str
    investment: str
    current_stage: str
    six_month_plan: str

    class Config:
        orm_mode = True

class AdminRegister(BaseModel):
    username: str
    password: str
    full_name: str
    position: str

class AdminRequestOut(BaseModel):
    request_id: int
    user_id: int
    username: str
    full_name: str
    position: str
    created_at: datetime
    role: str

    class Config:
        orm_mode = True


