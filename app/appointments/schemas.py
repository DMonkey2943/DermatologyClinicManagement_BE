from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime, date, time
from uuid import UUID
import enum

# Import các enum từ models
from app.appointments.models import AppointmentStatusEnum
# Import validators
from app.appointments.validators import (
    validate_appointment_date, 
    validate_appointment_time,
    # validate_appointment_time_for_date,
)

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
    appointment_time: time                  # Giờ hẹn (bắt buộc)
    time_slot: str = Field(max_length=100, default="30 phút")                          # Khung giờ (bắt buộc)
    status: AppointmentStatusEnum           # Trạng thái (bắt buộc)
    notes: Optional[str] = Field(max_length=250, default=None)             # Ghi chú

    @field_validator("appointment_date")
    @classmethod
    def check_appointment_date(cls, value):
        """Validate ngày hẹn"""
        return validate_appointment_date(value)

    @field_validator("appointment_time")
    @classmethod
    def check_appointment_time(cls, value):
        """Validate giờ hẹn"""
        return validate_appointment_time(value)

    # Model-level validator để kiểm cả date + time cùng lúc (mode="after")
    # @model_validator(mode="after")
    # def check_date_and_time(self) -> "AppointmentBase":
    #     # self là model instance, có attribute appointment_date và appointment_time
    #     appt_date = getattr(self, "appointment_date", None)
    #     appt_time = getattr(self, "appointment_time", None)
    #     # validate_appointment_time_for_date sẽ raise ValueError với msg tiếng Việt khi không hợp lệ
    #     validate_appointment_time_for_date(appt_time, appt_date)
    #     return self

    

class AppointmentCreate(AppointmentBase):
    """Schema tạo Appointment mới"""
    created_by: UUID                        # ID người tạo lịch hẹn

class AppointmentUpdate(BaseSchema):
    """Schema cập nhật Appointment"""
    doctor_id: Optional[UUID] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[time] = None
    time_slot: Optional[str] = Field(max_length=20, default=None)
    status: Optional[AppointmentStatusEnum] = None
    notes: Optional[str] = Field(max_length=250, default=None)  

    @field_validator("appointment_date")
    @classmethod
    def check_appointment_date(cls, value):
        """Validate ngày hẹn"""
        return validate_appointment_date(value)

    @field_validator("appointment_time")
    @classmethod
    def check_appointment_time(cls, value):
        """Validate giờ hẹn"""
        return validate_appointment_time(value)

class AppointmentResponse(AppointmentBase):
    """Schema trả về thông tin Appointment"""
    id: UUID
    created_at: datetime
    created_by: UUID
    patient: Optional[PatientForeignKeyResponse] = None    # Thông tin bệnh nhân
    doctor: Optional[UserForeignKeyResponse] = None        # Thông tin bác sĩ
    # created_by: Optional[UserResponse] = None # Thông tin người tạo lịch hẹn
