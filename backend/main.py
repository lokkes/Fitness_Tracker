import os
import shutil
import json
from pathlib import Path
from typing import Optional
from urllib import error, request

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from passlib.hash import bcrypt
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError

from .db import get_db
from .models import UserInfo, UserPerformance, user as UserModel
from .schemas import CreateUser, PerformanceRequest, TrainingRequest, UserLogin
from .modules import create_plan


app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
UPLOADS_DIR = BASE_DIR / "uploads"
LEGACY_UPLOADS_DIR = FRONTEND_DIR / "uploads"



@app.post("/register")
def add_user(user : CreateUser,db=Depends(get_db)):
    existing_user = db.query(UserModel).filter(UserModel.email==user.email).first()
    if existing_user:
       return {"success":False,"message" : "account aldready exists with this E-mail adress"}
    
    # hashed password
    hashed_password = bcrypt.hash(user.password)

    # creating new user object
    new_user=UserModel(
        name = user.name,
        email = user.email,
        password = hashed_password)
    
    # add session to commit 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": True, "message": "Registration successful!"}

@app.post("/login")
def login_user(user : UserLogin,db=Depends(get_db)):
    user_exists = db.query(UserModel).filter(UserModel.email==user.email).first()
    if user_exists:
        if bcrypt.verify(user.password,user_exists.password):
            return {"success" : True, "email": f"{user.email}"}
        else:
            return {"success" : False, "message" : "wrong password, try agiain"}    
    else:
        return {"success" : False, "message" : "user doesnt exist , please create a new account"}

@app.post("/add_info")

def add_info(
    email: str = Form(...),
    name: str = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    fights: int = Form(...),
    wins: int = Form(...),
    losses: int = Form(...),
    draws: int = Form(...),
    image: UploadFile = File(None),
    db=Depends(get_db)
):  
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    if image:
        saved_image_path = UPLOADS_DIR / image.filename
        with open(saved_image_path, "wb") as file_object:
            shutil.copyfileobj(image.file, file_object)
        image_path = f"uploads/{image.filename}"
    else:
        image_path = None 
    
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return {"success":False ,"message": "User not found"}
    
    existing_user = db.query(UserInfo).filter(UserInfo.user_id == user.id).first()
    if existing_user:
        return {"success": False, "message": "User info already exists. Use update instead."}
    
    user_info = UserInfo(
        user_id=user.id,
        name=name.strip() or user.name,
        height=height,
        weight=weight,
        fights=fights,
        wins=wins,
        losses=losses,
        draws=draws,
        image_path=image_path
    )

    try:
        db.add(user_info)
        db.commit()
        db.refresh(user_info)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not save user info: {exc.__class__.__name__}")

    return {"success": True, "message": "User info saved", "image_path": image_path}



@app.put("/add_info")
def edit_info(
    email: str = Form(...),
    name: str = Form(...),
    height: float = Form(...),
    weight: float = Form(...),
    fights: int = Form(...),
    wins: int = Form(...),
    losses: int = Form(...),
    draws: int = Form(...),
    image: UploadFile = File(None),
    db=Depends(get_db)
):
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return {"success": False, "message": "User not found"}

    user_info = db.query(UserInfo).filter(UserInfo.user_id == user.id).first()
    if not user_info:
        return {"success": False, "message": "User info not found"}

    if image and image.filename:
        saved_image_path = UPLOADS_DIR / image.filename
        with open(saved_image_path, "wb") as file_object:
            shutil.copyfileobj(image.file, file_object)
        user_info.image_path = f"uploads/{image.filename}"

    user_info.name = name.strip() or user.name
    user_info.height = height
    user_info.weight = weight
    user_info.fights = fights
    user_info.wins = wins
    user_info.losses = losses
    user_info.draws = draws

    try:
        db.commit()
        db.refresh(user_info)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not update user info: {exc.__class__.__name__}")

    return {"success": True, "message": "User info updated", "image_path": user_info.image_path}


@app.get("/api/profile")
def get_info(email:str,db=Depends(get_db)):

    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user :
        return {"success":False, "message" : "User not found"}
    user_info = db.query(UserInfo).filter(UserInfo.user_id == user.id).first()
    if not user_info:
        return {"success": False, "message": "User info not found"}
    return {
    "success": True,
    "data": {
        "name": user_info.name,
        "height": user_info.height,
        "weight": user_info.weight,
        "fights": user_info.fights,
        "wins": user_info.wins,
        "losses": user_info.losses,
        "draws": user_info.draws,
        "image_path": user_info.image_path
    }
    }


@app.get("/api/user_summary")
def get_user_summary(email: str, db=Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return {"success": False, "message": "User not found"}

    user_info = db.query(UserInfo).filter(UserInfo.user_id == user.id).first()
    display_name = user_info.name if user_info and user_info.name else user.name

    return {
        "success": True,
        "data": {
            "name": display_name,
            "email": user.email,
        }
    }

@app.post("/training_plan")
def trainings_plan(plan: TrainingRequest):
    result = create_plan(plan)
    return {
        "success": True,
        **result
    }


@app.get("/api/performance")
def get_performance(email: str, db=Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        return {"success": False, "message": "User not found"}

    performance = db.query(UserPerformance).filter(UserPerformance.user_id == user.id).first()
    if not performance:
        return {"success": False, "message": "Performance data not found"}

    return {
        "success": True,
        "data": {
            "sprint_100m_seconds": performance.sprint_100m_seconds,
            "sprint_400m_seconds": performance.sprint_400m_seconds,
            "run_5k_minutes": performance.run_5k_minutes,
            "bench_press_kg": performance.bench_press_kg,
            "squat_kg": performance.squat_kg,
            "deadlift_kg": performance.deadlift_kg,
            "pull_ups": performance.pull_ups,
            "push_ups": performance.push_ups,
            "rounds_completed": performance.rounds_completed,
        }
    }


@app.post("/performance")
def add_performance(payload: PerformanceRequest, db=Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if not user:
        return {"success": False, "message": "User not found"}

    existing_performance = db.query(UserPerformance).filter(UserPerformance.user_id == user.id).first()
    if existing_performance:
        return {"success": False, "message": "Performance data already exists. Use update instead."}

    performance = UserPerformance(
        user_id=user.id,
        sprint_100m_seconds=payload.sprint_100m_seconds,
        sprint_400m_seconds=payload.sprint_400m_seconds,
        run_5k_minutes=payload.run_5k_minutes,
        bench_press_kg=payload.bench_press_kg,
        squat_kg=payload.squat_kg,
        deadlift_kg=payload.deadlift_kg,
        pull_ups=payload.pull_ups,
        push_ups=payload.push_ups,
        rounds_completed=payload.rounds_completed,
    )

    try:
        db.add(performance)
        db.commit()
        db.refresh(performance)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not save performance: {exc.__class__.__name__}")

    return {"success": True, "message": "Performance saved successfully"}


@app.put("/performance")
def update_performance(payload: PerformanceRequest, db=Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == payload.email).first()
    if not user:
        return {"success": False, "message": "User not found"}

    performance = db.query(UserPerformance).filter(UserPerformance.user_id == user.id).first()
    if not performance:
        return {"success": False, "message": "Performance data not found"}

    performance.sprint_100m_seconds = payload.sprint_100m_seconds
    performance.sprint_400m_seconds = payload.sprint_400m_seconds
    performance.run_5k_minutes = payload.run_5k_minutes
    performance.bench_press_kg = payload.bench_press_kg
    performance.squat_kg = payload.squat_kg
    performance.deadlift_kg = payload.deadlift_kg
    performance.pull_ups = payload.pull_ups
    performance.push_ups = payload.push_ups
    performance.rounds_completed = payload.rounds_completed

    try:
        db.commit()
        db.refresh(performance)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Could not update performance: {exc.__class__.__name__}")

    return {"success": True, "message": "Performance updated successfully"}

@app.get("/")
def root():
    return FileResponse(TEMPLATES_DIR / "index.html")

@app.get("/index.html")
def index_page():
    return FileResponse(TEMPLATES_DIR / "index.html")

@app.get("/home.html")
def home_page():
    return FileResponse(TEMPLATES_DIR / "home.html")

@app.get("/training_plan")
def training_plan_page():
    return FileResponse(TEMPLATES_DIR / "training_plan.html")

@app.get("/track_Performance")
def performance_page():
    return FileResponse(TEMPLATES_DIR / "performance.html")

@app.get("/add_data.html")
def add_data_page():
    return FileResponse(TEMPLATES_DIR / "add_data.html")

@app.get("/profile")
@app.get("/profile.html")
def get_profile():
    return FileResponse(TEMPLATES_DIR / "profile.html")

@app.get("/uploads/{filename:path}")
def get_uploaded_file(filename: str):
    for directory in (UPLOADS_DIR, LEGACY_UPLOADS_DIR):
        file_path = directory / filename
        if file_path.is_file():
            return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Uploaded file not found")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")







        
