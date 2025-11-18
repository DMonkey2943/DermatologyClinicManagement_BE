# app/auth/endpoints.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
# from app.core.dependencies import AuthCredentialDepend, PatientAuthCredentialDepend
from app.database import get_db
from app.patients.schemas import PatientLogin, PatientResponse
from app.patients.services import PatientService
from app.auth.patients.jwt_handler import create_access_token, create_refresh_token, verify_patient_token, get_patient_id_from_token
from app.core.response import ResponseBase
from app.patients.schemas import PatientTokenData, LoginResponseData, RefreshTokenData
from typing_extensions import Annotated

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(
    prefix="/patient-auth",    # Tất cả endpoint sẽ có prefix /auth
    tags=["patient-auth"],      # Nhóm trong Swagger docs
    responses={404: {"description": "Not found"}}  # Response chung cho 404
)  # Router cho grouping routes

PatientAuthCredentialDepend = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())]

# Cấu hình HTTPBearer cho Swagger
# security = HTTPBearer(
#     bearerFormat="JWT",
#     description="Enter JWT token"
# )

@router.post("/login", response_model=ResponseBase[LoginResponseData])
def login(patient: PatientLogin, db: Session = Depends(get_db)):
    patient_data    = patient.model_dump() # Chuyển Pydantic model thành dict
    repo = PatientService(db)  # Tạo repository instance    
    validated_patient    = repo.validate_login(patient_data)

    # if validated_user is None:
    #     raise HTTPException(status_code=401, detail="Invalid credentials")

    if validated_patient:
        access_token    = create_access_token(validated_patient)
        refresh_token   = create_refresh_token(validated_patient)

        data_login = {"patient": validated_patient, "access_token": access_token, "refresh_token": refresh_token}
        return ResponseBase(message="Login successfully", data=data_login)

@router.post("/refresh")
def refresh_token(data: RefreshTokenData):
    try:
        payload = verify_patient_token(data.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid refresh token")
    
    token_data = PatientTokenData(**payload)
    new_access_token = create_access_token(token_data)

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/me", response_model=ResponseBase[PatientResponse])
def get_current_patient(
    CREDENTIALS: PatientAuthCredentialDepend,
    DB: Session = Depends(get_db),
    # CURRENT_PATIENT = None,
):
    try:
        payload = verify_patient_token(CREDENTIALS.credentials)
        patient_service = PatientService(DB)
        patient = patient_service.get_patient_by_id(payload["id"])
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Kiểm tra patient có active không (nếu có field này)
        # if hasattr(patient, 'deleted_at') and not patient.deleted_at:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="Inactive patient"
        #     )

        return ResponseBase(message="Lấy thông tin tài khoản bệnh nhân thành công", data=patient)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
