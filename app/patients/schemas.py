from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
import enum

# Import các enum từ models
from app.patients.models import GenderEnum

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class PatientBase(BaseSchema):
    """Schema cơ bản cho Patient"""
    full_name: str                          # Họ tên (bắt buộc)
    dob: Optional[date] = None              # Ngày sinh
    gender: Optional[GenderEnum] = None     # Giới tính
    phone_number: str                       # Số điện thoại (bắt buộc)
    email: Optional[EmailStr] = None        # Email (không bắt buộc)
    address: Optional[str] = None           # Địa chỉ
    medical_history: Optional[str] = None   # Tiền sử bệnh lý
    allergies: Optional[str] = None         # Dị ứng
    current_medications: Optional[str] = None  # Thuốc đang dùng
    current_condition: Optional[str] = None # Tình trạng hiện tại
    notes: Optional[str] = None             # Ghi chú

class PatientCreate(PatientBase):
    """Schema tạo Patient mới"""
    pass                                    # Sử dụng hết các trường từ base

class PatientUpdate(BaseSchema):
    """Schema cập nhật Patient - tất cả trường optional"""
    full_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    current_condition: Optional[str] = None
    notes: Optional[str] = None

class PatientResponse(PatientBase):
    """Schema trả về thông tin Patient"""
    id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None

class PatientForeignKeyResponse(BaseSchema):
    """Schema trả về thông tin Patient trong các quan hệ Foreign Key"""
    id: UUID
    full_name: str