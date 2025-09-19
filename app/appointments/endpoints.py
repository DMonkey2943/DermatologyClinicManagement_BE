from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.core.dependencies import AuthCredentialDepend
from app.database import get_db
from app.appointments.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.appointments.services import AppointmentService
from app.core.authentication import protected_route
from app.users.models import UserRoleEnum as RoleEnum
from app.core.response import PaginationMeta, ResponseBase, PaginatedResponse

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=ResponseBase[AppointmentResponse], status_code=status.HTTP_201_CREATED)
@protected_route([RoleEnum.ADMIN, RoleEnum.STAFF])
def create_appointment(
    CREDENTIALS: AuthCredentialDepend,
    appointment: AppointmentCreate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo lịch hẹn mới
    - Kiểm tra sự tồn tại của bệnh nhân, bác sĩ và người tạo
    - Trả về thông tin lịch hẹn với thông tin bệnh nhân và bác sĩ
    """
    repo = AppointmentService(DB)
    db_appointment = repo.create_appointment(appointment)
    return ResponseBase(message="Lịch hẹn được tạo thành công", data=db_appointment)

@router.get("/{appointment_id}", response_model=ResponseBase[AppointmentResponse])
def read_appointment(
    CREDENTIALS: AuthCredentialDepend,
    appointment_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin lịch hẹn theo ID
    - Bao gồm thông tin bệnh nhân và bác sĩ
    """
    repo = AppointmentService(DB)
    db_appointment = repo.get_appointment_by_id(appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Lịch hẹn không tồn tại")
    return ResponseBase(message="Lấy thông tin lịch hẹn thành công", data=db_appointment)

@router.get("/", response_model=PaginatedResponse[AppointmentResponse])
def read_appointments(
    CREDENTIALS: AuthCredentialDepend,
    doctor_id: Optional[UUID] = Query(None, description="ID bác sĩ (user_id) để lọc"),
    appointment_date: Optional[date] = Query(None, description="Ngày hẹn để lọc (YYYY-MM-DD)"),
    week_start: Optional[date] = Query(None, description="Ngày bắt đầu tuần để lọc (YYYY-MM-DD)"),
    month: Optional[str] = Query(None, description="Tháng để lọc (YYYY-MM)"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách lịch hẹn với phân trang và bộ lọc
    - Có thể lọc theo bác sĩ, ngày, tuần hoặc tháng
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
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        week_start=week_start,
        month=month
    )
    total = repo.count_appointments(
        doctor_id=doctor_id,
        appointment_date=appointment_date,
        week_start=week_start,
        month=month
    )
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách lịch hẹn thành công", data=appointments, meta=meta)

@router.put("/{appointment_id}", response_model=ResponseBase[AppointmentResponse])
@protected_route([RoleEnum.ADMIN, RoleEnum.STAFF])
def update_appointment(
    CREDENTIALS: AuthCredentialDepend,
    appointment_id: UUID,
    appointment: AppointmentUpdate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Cập nhật thông tin lịch hẹn
    - Chỉ cập nhật các trường được cung cấp
    """
    repo = AppointmentService(DB)
    db_appointment = repo.update_appointment(appointment_id=appointment_id, appointment_update=appointment)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Lịch hẹn không tồn tại")
    return ResponseBase(message="Cập nhật lịch hẹn thành công", data=db_appointment)

# @router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
# @protected_route([RoleEnum.ADMIN, RoleEnum.STAFF])
# def delete_appointment(
#     CREDENTIALS: AuthCredentialDepend,
#     appointment_id: UUID,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Xóa lịch hẹn
#     - Trả về 204 nếu thành công
#     """
#     repo = AppointmentService(DB)
#     success = repo.delete_appointment(appointment_id=appointment_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Lịch hẹn không tồn tại")