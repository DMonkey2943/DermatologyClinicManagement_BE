from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.response import ErrorResponse
from fastapi.middleware.cors import CORSMiddleware
from app.users.endpoints import router as users_router
from app.users.doctor_endpoints import router as doctors_router
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

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(message=exc.detail).model_dump()  # Sử dụng ErrorResponse
    )

@app.exception_handler(Exception)  # Handler cho các error bất ngờ
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(message="Internal server error", details=str(exc)).model_dump()
    )

# Include các router
app.include_router(users_router)    # Include routes từ users
app.include_router(auth_router)     # Include routes từ auth
app.include_router(doctors_router)    # Include routes từ doctors
app.include_router(patients_router) # Include routes từ patients

@app.get("/")
def read_root():
    return {"message": "Welcome to Skin Clinic Backend"}