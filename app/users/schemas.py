from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
import enum

# Import các enum từ models
from app.users.models import GenderEnum, UserRoleEnum

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class UserBase(BaseSchema):
    """Schema cơ bản cho User - chứa các trường chung"""
    username: str                           # Tên đăng nhập
    full_name: Optional[str] = None         # Họ tên (không bắt buộc)
    dob: Optional[date] = None              # Ngày sinh (không bắt buộc)
    gender: Optional[GenderEnum] = None     # Giới tính (không bắt buộc)
    phone_number: str                       # Số điện thoại (bắt buộc)
    email: EmailStr                         # Email với validation tự động
    role: Optional[UserRoleEnum] = None     # Vai trò (không bắt buộc)
    avatar: Optional[str] = None            # Đường dẫn ảnh đại diện

class UserCreate(UserBase):
    """Schema để tạo User mới - thêm password"""
    password: str                           # Mật khẩu (sẽ được hash)

class UserUpdate(BaseSchema):
    """Schema để cập nhật User - tất cả trường đều optional"""
    username: Optional[str] = None
    full_name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRoleEnum] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None        # Có thể cập nhật trạng thái hoạt động

class UserResponse(UserBase):
    """Schema để trả về thông tin User - ẩn password"""
    id: UUID                                # ID của user
    is_active: bool                         # Trạng thái hoạt động
    created_at: datetime                    # Thời gian tạo
    deleted_at: Optional[datetime] = None   # Thời gian xóa (soft delete)



# ================================ DOCTOR SCHEMAS ================================
class DoctorBase(BaseSchema):
    """Schema cơ bản cho Doctor"""
    specialization: Optional[str] = None    # Chuyên khoa

class DoctorCreate(DoctorBase):
    """Schema tạo Doctor mới"""
    user_id: UUID                           # ID của user tương ứng

class DoctorUpdate(DoctorBase):
    """Schema cập nhật Doctor"""
    pass                                    # Chỉ có specialization có thể update

class DoctorResponse(DoctorBase):
    """Schema trả về thông tin Doctor"""
    id: UUID
    user_id: UUID
    user: Optional[UserResponse] = None     # Thông tin user tương ứng
