from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.appointments.models import Appointment, AppointmentStatusEnum
from app.auth.patients.endpoints import PatientAuthCredentialDepend
from app.core.patient_authentication import patient_protected_route
from app.database import get_db
from app.medical_records.schemas import MedicalRecordDetailResponse, MedicalRecordResponse
from app.medical_records.services import MedicalRecordService
from app.users.models import UserRoleEnum as RoleEnum
from app.core.response import PaginationMeta, ResponseBase, PaginatedResponse

router = APIRouter(
    prefix="/patient-medical-records",
    tags=["patient-medical-records"],
    responses={404: {"description": "Not found"}}
)

@router.get("/", response_model=PaginatedResponse[MedicalRecordResponse])
@patient_protected_route()
def read_medical_records_by_patient(
    CREDENTIALS: PatientAuthCredentialDepend,
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    DB: Session = Depends(get_db),    
    CURRENT_PATIENT=None,
):
    """
    Lấy danh sách lịch hẹn với phân trang và bộ lọc
    - Có thể lọc theo bác sĩ, bệnh nhân, các trạng thái, ngày, tuần hoặc tháng
    - Bao gồm thông tin bệnh nhân và bác sĩ
    """
    repo = MedicalRecordService(DB)
    total = repo.count_medical_records(patient_id=CURRENT_PATIENT.id, doctor_id=None)    
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    records = repo.get_medical_records(skip=skip, limit=limit, patient_id=CURRENT_PATIENT.id, doctor_id=None)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy lịch sử khám bệnh thành công", data=records, meta=meta)

@router.get("/{record_id}", response_model=ResponseBase[MedicalRecordDetailResponse])
@patient_protected_route()
def read_medical_records_by_patient(
    CREDENTIALS: PatientAuthCredentialDepend,
    record_id: UUID,
    DB: Session = Depends(get_db),    
    CURRENT_PATIENT=None,
):
    """
    Lấy thông tin hồ sơ khám bệnh của bệnh nhân theo ID
    """
    repo = MedicalRecordService(DB)
    db_record = repo.get_medical_record_detail_of_patient(record_id, current_patient_id=CURRENT_PATIENT.id)
    # if db_record is None:
    #     raise HTTPException(status_code=404, detail="Hồ sơ khám bệnh không tồn tại")
    return ResponseBase(message="Lấy thông tin hồ sơ khám bệnh thành công", data=db_record)