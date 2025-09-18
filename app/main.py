from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.users.endpoints import router as users_router
from app.auth.endpoints import router as auth_router
from app.patients.endpoints import router as patients_router
from app.models import *

app = FastAPI(title="Skin Clinic API")  # Tạo app FastAPI với title

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Chỉ định origin của frontend
    allow_credentials=True,  # Cho phép gửi credentials (cookies, token)
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Cho phép các phương thức HTTP
    allow_headers=["Content-Type", "Authorization"],  # Cho phép header tùy chỉnh
)

# Include các router
app.include_router(users_router)    # Include routes từ users
app.include_router(auth_router)     # Include routes từ auth
app.include_router(patients_router) # Include routes từ patients

@app.get("/")
def read_root():
    return {"message": "Welcome to Skin Clinic Backend"}