from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

# Import các enum từ models
from app.patients.models import GenderEnum
# Import validators
from app.users.validators import (
    validate_phone_number,
)

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class PatientBase(BaseSchema):
    """Schema cơ bản cho Patient"""
    full_name: str = Field(min_length=2, max_length=50)                          # Họ tên (bắt buộc)
    dob: Optional[date] = None              # Ngày sinh
    gender: Optional[GenderEnum] = None     # Giới tính
    phone_number: str                       # Số điện thoại (bắt buộc)
    email: Optional[EmailStr] = None        # Email (không bắt buộc)
    address: Optional[str] = Field(max_length=250, default=None)           # Địa chỉ
    medical_history: Optional[str] = Field(max_length=250, default=None)   # Tiền sử bệnh lý
    allergies: Optional[str] = Field(max_length=250, default=None)         # Dị ứng
    current_medications: Optional[str] = Field(max_length=250, default=None)  # Thuốc đang dùng
    current_condition: Optional[str] = Field(max_length=250, default=None) # Tình trạng hiện tại
    notes: Optional[str] = None             # Ghi chú

    @field_validator("phone_number")
    @classmethod
    def _check_phone(cls, v):
        return validate_phone_number(v)
    

class PatientCreate(PatientBase):
    """Schema tạo Patient mới"""
    pass                                    # Sử dụng hết các trường từ base

class PatientUpdate(BaseSchema):
    """Schema cập nhật Patient - tất cả trường optional"""
    full_name: Optional[str] = Field(min_length=2, max_length=50, default=None) 
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(max_length=250, default=None)
    medical_history: Optional[str] = Field(max_length=250, default=None)
    allergies: Optional[str] = Field(max_length=250, default=None)
    current_medications: Optional[str] = Field(max_length=250, default=None)
    current_condition: Optional[str] = Field(max_length=250, default=None)
    notes: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def _check_phone(cls, v):
        return validate_phone_number(v)

class PatientResponse(PatientBase):
    """Schema trả về thông tin Patient"""
    id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None

class PatientForeignKeyResponse(BaseSchema):
    """Schema trả về thông tin Patient trong các quan hệ Foreign Key"""
    id: UUID
    full_name: str