from fastapi import FastAPI
from app.users.endpoints import router as users_router
from app.patients.endpoints import router as patients_router
from app.models import *

app = FastAPI(title="Skin Clinic API")  # Tạo app FastAPI với title

app.include_router(users_router)    # Include routes từ users
app.include_router(patients_router)    # Include routes từ patients

@app.get("/")
def read_root():
    return {"message": "Welcome to Skin Clinic Backend"}