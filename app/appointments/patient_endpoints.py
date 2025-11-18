from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.appointments.models import Appointment, AppointmentStatusEnum
from app.auth.patients.endpoints import PatientAuthCredentialDepend
from app.core.patient_authentication import patient_protected_route
from app.database import get_db
from app.appointments.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse, PatientAppointmentCreate
from app.appointments.services import AppointmentService
from app.users.models import UserRoleEnum as RoleEnum
from app.core.response import PaginationMeta, ResponseBase, PaginatedResponse

router = APIRouter(
    prefix="/patient-appointments",
    tags=["patient-appointments"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=ResponseBase[AppointmentResponse], status_code=status.HTTP_201_CREATED)
@patient_protected_route()
def create_appointment_by_patient(
    CREDENTIALS: PatientAuthCredentialDepend,
    appointment: PatientAppointmentCreate,
    DB: Session = Depends(get_db),
    CURRENT_PATIENT=None,
):
    """
    Tạo lịch hẹn mới
    - Kiểm tra sự tồn tại của bệnh nhân, bác sĩ và người tạo
    - Trả về thông tin lịch hẹn với thông tin bệnh nhân và bác sĩ
    """
    # repo = AppointmentService(DB)
    # db_appointment = repo.create_appointment_by_patient(appointment)
    db_appointment = Appointment(
        patient_id=CURRENT_PATIENT.id,
        doctor_id=appointment.doctor_id,
        created_by=appointment.created_by,
        appointment_time=appointment.appointment_time,
        appointment_date=appointment.appointment_date,
        time_slot=appointment.time_slot,
        status="SCHEDULED"
    )
    DB.add(db_appointment)
    DB.commit()
    DB.refresh(db_appointment)
    return ResponseBase(message="Đặt lịch hẹn thành công", data=db_appointment)

@router.get("/", response_model=PaginatedResponse[AppointmentResponse])
@patient_protected_route()
def read_appointments_by_patient(
    CREDENTIALS: PatientAuthCredentialDepend,
    # doctor_id: Optional[UUID] = Query(None, description="ID bác sĩ (user_id) để lọc"),
    # patient_id: Optional[UUID] = Query(None, description="ID bệnh nhân để lọc"),
    status: Optional[List[AppointmentStatusEnum]] = Query(None, description="Danh sách trạng thái để lọc (SCHEDULED, WAITING, COMPLETED, CANCELLED)"),
    appointment_date: Optional[date] = Query(None, description="Ngày hẹn để lọc (YYYY-MM-DD)"),
    week_start: Optional[date] = Query(None, description="Ngày bắt đầu tuần để lọc (YYYY-MM-DD)"),
    month: Optional[str] = Query(None, description="Tháng để lọc (YYYY-MM)"),
    upcoming: bool = Query(False, description="Lọc các lịch hẹn sắp tới (SCHEDULED hoặc WAITING từ ngày hiện tại trở đi)"),  # Thêm upcoming
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
    repo = AppointmentService(DB)
    
    # Kiểm tra nếu có nhiều hơn một bộ lọc thời gian
    time_filters = sum(1 for x in [appointment_date, week_start, month] if x is not None)
    if time_filters > 1:
        raise HTTPException(status_code=400, detail="Chỉ được cung cấp một trong các bộ lọc: appointment_date, week_start hoặc month")

    appointments = repo.get_appointments(
        skip=skip,
        limit=limit,
        # doctor_id=doctor_id,
        patient_id=CURRENT_PATIENT.id, 
        status=status,
        appointment_date=appointment_date,
        week_start=week_start,
        month=month,
        upcoming=upcoming
    )
    total = repo.count_appointments(
        # doctor_id=doctor_id,
        patient_id=CURRENT_PATIENT.id, 
        status=status,
        appointment_date=appointment_date,
        week_start=week_start,
        month=month,
        upcoming=upcoming
    )
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách lịch hẹn đã đặt thành công", data=appointments, meta=meta)