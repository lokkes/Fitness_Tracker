from pathlib import Path
from fastapi import FastAPI,HTTPException,Depends
from .schemas import CreateUser,UserLogin,PersonalInfo
from .db import sessionLocal,get_db
from passlib.hash import bcrypt
from .models import user as UserModel, UserInfo
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


app = FastAPI()
FRONTEND_DIR = Path("./frontend")
TEMPLATES_DIR = FRONTEND_DIR / "templates"


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
            return {"success" : True, "message" : "Logged in"}
        else:
            return {"success" : False, "message" : "wrong password, try agiain"}    
    else:
        return {"success" : False, "message" : "user doesnt exist , please create a new account"}

@app.post("/add_info")
def add_info(info:PersonalInfo,user_email:str,db=Depends(get_db)):    
    user = db.query(UserModel).filter(UserModel.email == user_email).first()
    if not user:
        return {"error": "User not found"}
    user_info = UserInfo(
    user_id=user.id,
    image = info.image_path,
    name=info.name,
    height=info.height,
    weight=info.weight,
    fights=info.fights,
    wins=info.wins,
    losses=info.losses,
    draws=info.draws
)
    db.add(user_info)
    db.commit()
    db.refresh(user_info)

@app.put("/add_info")
def edit_info(info:PersonalInfo,db=Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == info.email).first()
    if not user:
        return {"message": "User not found"}
    
    user_info = db.query(UserInfo).filter(UserInfo.user_id == user.id).first()
    if not user_info:
        return {"message": "User info not found"}

    user_info.image_path = info.image_path
    user_info.height = info.height
    user_info.weight = info.weight
    user_info.fights = info.fights
    user_info.wins = info.wins
    user_info.losses = info.losses
    user_info.draws = info.draws

    db.commit()

@app.get("/")
def root():
    return FileResponse(TEMPLATES_DIR / "index.html")

@app.get("/index.html")
def index_page():
    return FileResponse(TEMPLATES_DIR / "index.html")

@app.get("/home.html")
def home_page():
    return FileResponse(TEMPLATES_DIR / "home.html")

@app.get("/add_data.html")
def add_data_page():
    return FileResponse(TEMPLATES_DIR / "add_data.html")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")








    
    






        


