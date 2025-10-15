from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.core.response import ErrorResponse
from fastapi.exceptions import RequestValidationError
from app.core.validation_handler import validation_handler_errors_out
from fastapi.middleware.cors import CORSMiddleware
from app.users.endpoints import router as users_router
from app.users.doctor_endpoints import router as doctors_router
from app.auth.endpoints import router as auth_router
from app.patients.endpoints import router as patients_router
from app.appointments.endpoints import router as appointments_router
from app.medications.endpoints import router as medications_router
from app.services.endpoints import router as services_router
from app.medical_records.endpoints import router as medical_records_router
from app.prescriptions.endpoints import router as prescriptions_router
from app.service_indications.endpoints import router as service_indications_router
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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors_out = validation_handler_errors_out(exc)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            message="Request Validation Error", 
            details=errors_out
        ).model_dump(),
    )


@app.exception_handler(Exception)  # Handler cho các error bất ngờ
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(message="Internal server error", details=str(exc)).model_dump()
    )

# Include các router
app.include_router(auth_router)     # Include routes từ auth
app.include_router(users_router)    # Include routes từ users
app.include_router(doctors_router)    # Include routes từ doctors
app.include_router(patients_router) # Include routes từ patients
app.include_router(appointments_router) # Include routes từ appointments
app.include_router(medications_router) # Include routes từ medications
app.include_router(services_router) # Include routes từ services
app.include_router(medical_records_router) # Include routes từ medical_records
app.include_router(prescriptions_router) # Include routes từ prescriptions
app.include_router(service_indications_router) # Include routes từ service_indications

@app.get("/")
def read_root():
    return {"message": "Welcome to Skin Clinic Backend"}