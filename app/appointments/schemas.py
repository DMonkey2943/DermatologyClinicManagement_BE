from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
import enum

# Import các enum từ models
from app.appointments.models import AppointmentStatusEnum

# Import các response từ schemas khác
from app.patients.schemas import PatientForeignKeyResponse
from app.users.schemas import UserForeignKeyResponse

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class AppointmentBase(BaseSchema):
    """Schema cơ bản cho Appointment"""
    patient_id: UUID                        # ID bệnh nhân (bắt buộc)
    doctor_id: UUID                         # ID bác sĩ (bắt buộc)
    appointment_date: date                  # Ngày hẹn (bắt buộc)
    time_slot: str                          # Khung giờ (bắt buộc)
    status: AppointmentStatusEnum           # Trạng thái (bắt buộc)
    notes: Optional[str] = None             # Ghi chú

class AppointmentCreate(AppointmentBase):
    """Schema tạo Appointment mới"""
    created_by: UUID                        # ID người tạo lịch hẹn

class AppointmentUpdate(BaseSchema):
    """Schema cập nhật Appointment"""
    appointment_date: Optional[date] = None
    time_slot: Optional[str] = None
    status: Optional[AppointmentStatusEnum] = None
    notes: Optional[str] = None

class AppointmentResponse(AppointmentBase):
    """Schema trả về thông tin Appointment"""
    id: UUID
    created_at: datetime
    created_by: UUID
    patient: Optional[PatientForeignKeyResponse] = None    # Thông tin bệnh nhân
    doctor: Optional[UserForeignKeyResponse] = None        # Thông tin bác sĩ
    # created_by: Optional[UserResponse] = None # Thông tin người tạo lịch hẹn
