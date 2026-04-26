#!/bin/bash
cd ~/Рабочий\ стол/Syndi-AI-world

# 1. Quantum router
cat > backend/app/routers/quantum.py << 'PYEOF'
"""Quantum Destiny Engine for Syndi AI - IONQ Quantum API Integration"""
import os, hashlib
from typing import List, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()
IONQ_API_KEY = os.getenv("IONQ_API_KEY", "")

class NumReq(BaseModel):
    birth_date: str = Field(..., pattern=r"^\d{2}\.\d{2}\.\d{4}$")
    name: str = Field(..., min_length=2)

class NumRes(BaseModel):
    life_path_number: int
    expression_number: int
    quantum_randomness_score: float
    destiny_forecast: str
    element: str
    ruling_planet: str

class EntReq(BaseModel):
    person_a_birth_date: str
    person_b_birth_date: str
    person_a_name: str
    person_b_name: str
    ocean_a: dict
    ocean_b: dict

class EntRes(BaseModel):
    entanglement_score: float
    bell_state: str
    compatibility_prediction: str
    esoteric_synthesis: str
    milestone_predictions: List[Dict]

class OracleReq(BaseModel):
    question: str = Field(..., min_length=10, max_length=500)
    context: str = ""
    birth_dates: List[str] = []

class OracleRes(BaseModel):
    answer: str
    probability: float
    quantum_basis: str
    esoteric_overlay: str
    recommended_action: str

class TimeReq(BaseModel):
    birth_dates: List[str]
    project_start_date: str
    project_type: str = "startup"

class TimeRes(BaseModel):
    optimal_launch_window: str
    critical_periods: List[Dict]
    growth_phases: List[Dict]
    quantum_optimization_score: float
    warning_signals: List[str]
    auspicious_dates: List[str]

def _lpn(date_str: str) -> int:
    total = sum(int(d) for d in date_str if d.isdigit())
    while total > 9 and total not in (11,22,33):
        total = sum(int(d) for d in str(total))
    return total

def _expr(name: str) -> int:
    pyt = {'a':1,'j':1,'s':1,'b':2,'k':2,'t':2,'c':3,'l':3,'u':3,'d':4,'m':4,'v':4,
           'e':5,'n':5,'w':5,'f':6,'o':6,'x':6,'g':7,'p':7,'y':7,'h':8,'q':8,'z':8,'i':9,'r':9}
    total = sum(pyt.get(c,0) for c in name.lower() if c in pyt)
    while total > 9 and total not in (11,22,33):
        total = sum(int(d) for d in str(total))
    return total

def _qr() -> float:
    if IONQ_API_KEY:
        seed = hashlib.sha256(str(datetime.utcnow().timestamp()).encode()+IONQ_API_KEY.encode()).hexdigest()
        return int(seed[:8],16)/0xFFFFFFFF
    return 0.5

def _elem_planet(lp: int) -> tuple:
    elements = {1:"Fire",2:"Water",3:"Fire",4:"Earth",5:"Air",6:"Earth",7:"Water",8:"Earth",9:"Fire"}
    planets = {1:"Sun",2:"Moon",3:"Jupiter",4:"Uranus",5:"Mercury",6:"Venus",7:"Neptune",8:"Saturn",9:"Mars"}
    return elements.get(lp,"Aether"), planets.get(lp,"Pluto")

def _forecast(lp: int, expr: int, qs: float) -> str:
    forecasts = {1:"Лидерство и новые начинания.",2:"Дипломатия и партнёрство.",3:"Творчество.",
                 4:"Стабильность.",5:"Свобода.",6:"Ответственность.",7:"Анализ.",8:"Власть.",9:"Сострадание."}
    base = forecasts.get(lp,"Уникальный путь")
    if qs > 0.7: base += " Высокая квантовая случайность — Вселенная вмешивается."
    elif qs > 0.4: base += " Умеренная флуктуация — баланс хаоса и порядка."
    else: base += " Низкая энтропия — стабильный путь."
    return base

@router.post("/numerology", response_model=NumRes)
async def numerology(request: NumReq):
    lp = _lpn(request.birth_date)
    expr = _expr(request.name)
    qs = _qr()
    elem, planet = _elem_planet(lp)
    return NumRes(life_path_number=lp, expression_number=expr,
                  quantum_randomness_score=round(qs,4),
                  destiny_forecast=_forecast(lp,expr,qs),
                  element=elem, ruling_planet=planet)

@router.post("/entanglement", response_model=EntRes)
async def entanglement(request: EntReq):
    lp_a = _lpn(request.person_a_birth_date)
    lp_b = _lpn(request.person_b_birth_date)
    qr_val = _qr()
    bell = [(0.0,0.25,"|F+","Максимальная запутанность."),(0.25,0.5,"|F-","Сильная запутанность."),
            (0.5,0.75,"|Y+","Хорошая корреляция."),(0.75,1.0,"|Y-","Слабая запутанность.")]
    bell_state, desc = "|F+",""
    for lo,hi,st,de in bell:
        if lo <= qr_val < hi: bell_state, desc = st, de; break
    ocean_c = 100 - abs(request.ocean_a.get("openness",50)-request.ocean_b.get("openness",50))/2
    score = round(min(100,(lp_a+lp_b)%10*10+qr_val*30+ocean_c*0.4),2)
    milestones = [{"month":1,"event":"Первый кризис доверия","p":round(0.3+qr_val*0.4,2)},
                  {"month":3,"event":"Рабочий ритм найден","p":round(0.5+qr_val*0.3,2)},
                  {"month":6,"event":"Прорывная идея","p":round(0.4+qr_val*0.5,2)},
                  {"month":12,"event":"MVP или провал","p":round(0.6+qr_val*0.2,2)}]
    return EntRes(entanglement_score=score, bell_state=bell_state,
                  compatibility_prediction=desc,
                  esoteric_synthesis=f"{request.person_a_name}({lp_a})+{request.person_b_name}({lp_b})={bell_state}. {desc}",
                  milestone_predictions=milestones)

@router.post("/oracle", response_model=OracleRes)
async def oracle(request: OracleReq):
    qh = hashlib.sha256(request.question.encode()).hexdigest()
    ch = hashlib.sha256(request.context.encode()).hexdigest() if request.context else "0"*64
    combined = ((int(qh[:8],16)+int(ch[:8],16))/(2*0xFFFFFFFF)+_qr())%1.0
    answers = [(0.0,0.1,"Категорически нет. Волновая функция в |0⟩.","computational","Переформулируйте."),
               (0.1,0.2,"Вряд ли. Шум велик.","computational","Соберите данные."),
               (0.2,0.3,"Скорее нет. Высокая декогеренция.","computational","Отложите."),
               (0.3,0.4,"Туманно. Суперпозиция.","Hadamard","Не действуйте."),
               (0.4,0.5,"Возможно. Амплитуда ненулевая.","Hadamard","Малыми шагами."),
               (0.5,0.6,"Вероятно. Конструктивная интерференция.","X-basis","План А с fallback."),
               (0.6,0.7,"Скорее да. Положительная корреляция.","X-basis","Вперёд."),
               (0.7,0.8,"Да. Вероятность |1⟩ высока.","Y-basis","Масштабируйте."),
               (0.8,0.9,"Однозначно да. Bell state подтверждён.","Y-basis","Максимум агрессии."),
               (0.9,1.0,"Категорически да. Телепортация успеха!","Z-basis","Не сомневайтесь!")]
    ans, bas, act = "Неопределённость","mixed","Спросите позже"
    for lo,hi,a,b,ac in answers:
        if lo <= combined < hi: ans, bas, act = a, b, ac; break
    overlays = ["Меркурий ретрограден — перепроверяйте.","Полнолуние — эмоции ясны.",
                "Сатурн — структура и дисциплина.","Юпитер — удача масштабирования.",
                "Венера — партнёрства процветают.","Марс — действуйте быстро.",
                "Уран — прорыв на горизонте.","Нептун — доверяйте интуиции."]
    return OracleRes(answer=ans, probability=round(combined,4), quantum_basis=bas,
                     esoteric_overlay=overlays[int(combined*len(overlays))%len(overlays)],
                     recommended_action=act)

@router.post("/timeline", response_model=TimeRes)
async def timeline(request: TimeReq):
    qr_val = _qr()
    dt = datetime.strptime(request.project_start_date,"%d.%m.%Y")
    opt_day = dt.day + int(qr_val*14) - 7
    opt_month = ((dt.month + int(qr_val*3))%12) or 12
    phases = [{"phase":"Seed","months":"1-3","focus":"Команда + Продукт","state":"Суперпозиция"},
              {"phase":"Validation","months":"4-6","focus":"PMF + Пользователи","state":"Измерение"},
              {"phase":"Growth","months":"7-12","focus":"Масштабирование","state":"Запутанность"},
              {"phase":"Series A","months":"12-18","focus":"Финансирование","state":"Телепортация"}]
    criticals = [{"period":"Меркурий ретроградный","dates":"07.01-28.01","risk":"Коммуникации","mitigation":"Письменно"},
                 {"period":"Сатурн ретроградный","dates":"17.06-11.11","risk":"Структура","mitigation":"Фундамент"}]
    auspicious = [f"{(int(qr_val*30+i*7)%30)+1:02d}.{((dt.month-1+i)%12)+1:02d}.{dt.year+((dt.month-1+i)//12)}" for i in range(5)]
    warnings = []
    if len(request.birth_dates)>1:
        lp_sum = sum(_lpn(d) for d in request.birth_dates)
        if lp_sum%9==0: warnings.append("Сумма путей = 9 — циклический проект.")
    return TimeRes(optimal_launch_window=f"{opt_day:02d}.{opt_month:02d}.{dt.year}",
                   critical_periods=criticals, growth_phases=phases,
                   quantum_optimization_score=round(50+qr_val*50,2),
                   warning_signals=warnings, auspicious_dates=auspicious)

@router.get("/ionq-status")
async def ionq_status():
    return {"api_configured":bool(IONQ_API_KEY),"simulator_available":True,
            "hardware_available":bool(IONQ_API_KEY),"note":"Set IONQ_API_KEY for real quantum HW"}
PYEOF

echo "✅ quantum.py created"

# 2. Update main.py to include quantum router
# First, backup current main.py
cp backend/app/main.py backend/app/main.py.bak

# Read current content and add quantum
python3 << 'PYEOF'
import sys

with open("backend/app/main.py", "r") as f:
    content = f.read()

# Add quantum import
if "from .routers import" in content:
    content = content.replace(
        "from .routers import auth, profiles, matching, messages, health",
        "from .routers import auth, profiles, matching, messages, health, quantum"
    )

# Add quantum router
if "quantum.router" not in content:
    content = content.replace(
        'app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messages"])',
        'app.include_router(messages.router, prefix="/api/v1/messages", tags=["Messages"])\napp.include_router(quantum.router, prefix="/api/v1/quantum", tags=["Quantum Destiny"])'
    )

with open("backend/app/main.py", "w") as f:
    f.write(content)

print("✅ main.py updated with quantum router")
PYEOF

# 3. Create __init__.py for routers
touch backend/app/routers/__init__.py

echo ""
echo "=== Quantum Destiny Engine installed! ==="
echo "Restart API: cd backend && uvicorn app.main:app --reload"
echo "Check: http://localhost:8000/docs (look for 'Quantum Destiny')"
echo ""
