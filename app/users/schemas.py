from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime, date
from uuid import UUID

# Import các enum từ models
from app.users.models import GenderEnum, UserRoleEnum
# Import validators
from app.users.validators import (
    validate_dob_at_least_18,
    validate_phone_number,
    validate_password,
)

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class UserBase(BaseSchema):
    """
    Schema cơ bản cho User - chứa các trường chung.
    Lưu ý: những trường bắt buộc sẽ được enforce bởi Pydantic (required).
    """
    username: str = Field(min_length=4, max_length=50, pattern='^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$')                           # Tên đăng nhập (required)    
    full_name: Optional[str] = Field(min_length=2, max_length=50, default=None) # Họ tên (không bắt buộc)
    dob: Optional[date] = None              # Ngày sinh (không bắt buộc)
    gender: Optional[GenderEnum] = None     # Giới tính (không bắt buộc)
    phone_number: str                       # Số điện thoại (bắt buộc)
    email: EmailStr                         # Email với validation tự động
    role: Optional[UserRoleEnum] = None     # Vai trò (không bắt buộc)
    avatar: Optional[str] = None            # Đường dẫn ảnh đại diện

    # Validators ---------------------------------------------------
    @field_validator("dob")
    @classmethod
    def _check_dob(cls, v):
        return validate_dob_at_least_18(v)

    @field_validator("phone_number")
    @classmethod
    def _check_phone(cls, v):
        return validate_phone_number(v)


class UserCreate(UserBase):
    """Schema để tạo User mới - thêm password"""
    password: str                           # Mật khẩu (bắt buộc)

    @field_validator("password")
    @classmethod
    def _check_password(cls, v):
        return validate_password(v)

class UserCreateWithAvatarForm(BaseModel):
    username: str = Field(..., min_length=4, max_length=50, pattern='^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$')
    full_name: Optional[str] = Field(None, min_length=2, max_length=50)
    password: str
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: str
    email: EmailStr
    role: Optional[UserRoleEnum] = None

    @field_validator("dob")
    @classmethod
    def _check_dob(cls, v):
        return validate_dob_at_least_18(v)

    @field_validator("phone_number")
    @classmethod
    def _check_phone(cls, v):
        return validate_phone_number(v)

    @field_validator("password")
    @classmethod
    def _check_password(cls, v):
        return validate_password(v)

class UserUpdate(BaseSchema):
    """Schema để cập nhật User - tất cả trường đều optional"""
    username: Optional[str] = Field(min_length=4, max_length=50, pattern='^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$', default=None)     
    full_name: Optional[str] = Field(min_length=2, max_length=50, default=None)
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRoleEnum] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None        # Có thể cập nhật trạng thái hoạt động

    @field_validator("dob")
    @classmethod
    def _check_dob(cls, v):
        return validate_dob_at_least_18(v)

    @field_validator("phone_number")
    @classmethod
    def _check_phone(cls, v):
        return validate_phone_number(v)


class UserResponse(BaseSchema):
    """Schema để trả về thông tin User - ẩn password"""
    id: UUID                                # ID của user
    username: str                           # Tên đăng nhập (required)    
    full_name: Optional[str]                # Họ tên (không bắt buộc)
    dob: Optional[date] = None              # Ngày sinh (không bắt buộc)
    gender: Optional[GenderEnum] = None     # Giới tính (không bắt buộc)
    phone_number: str                       # Số điện thoại (bắt buộc)
    email: EmailStr                         # Email với validation tự động
    role: Optional[UserRoleEnum] = None     # Vai trò (không bắt buộc)
    avatar: Optional[str] = None
    is_active: bool                         # Trạng thái hoạt động
    created_at: datetime                    # Thời gian tạo
    deleted_at: Optional[datetime] = None   # Thời gian xóa (soft delete)


class UserLogin(BaseSchema):
    username: str = Field(min_length=4, max_length=50, pattern='^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$')  
    password: str

    # @field_validator("password")
    # @classmethod
    # def _check_password(cls, v):
    #     return validate_password(v)

class RefreshTokenData(BaseSchema):
    refresh_token: str

class UserTokenData(BaseSchema):
    """Schema cho dữ liệu trong token"""
    id: UUID
    username: str
    full_name: Optional[str] = None
    email: EmailStr
    phone_number: str
    role: UserRoleEnum

class LoginResponseData(BaseSchema):
    user: UserTokenData
    access_token: str
    refresh_token: str

class UserForeignKeyResponse(BaseSchema):
    """Schema trả về thông tin User trong các quan hệ Foreign Key"""
    id: UUID
    full_name: Optional[str] = None


# ================================ DOCTOR SCHEMAS ================================
class DoctorBase(BaseSchema):
    """Schema cơ bản cho Doctor"""
    specialization: Optional[str] = Field(max_length=250, default=None)    # Chuyên khoa

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
    deleted_at: Optional[datetime] = None   # Thời gian xóa (soft delete)

class DoctorCombinedCreate(BaseSchema):
    """Schema gộp để tạo bác sĩ mới (gộp User và Doctor)"""
    username: str = Field(min_length=4, max_length=50, pattern='^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$')
    password: str
    full_name: Optional[str] = Field(min_length=2, max_length=50, default=None)
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: str
    email: EmailStr
    avatar: Optional[str] = None
    specialization: Optional[str] = Field(max_length=250, default=None)

    @field_validator("password")
    @classmethod
    def _check_password(cls, v):
        return validate_password(v)
    
    @field_validator("dob")
    @classmethod
    def _check_dob(cls, v):
        return validate_dob_at_least_18(v)

    @field_validator("phone_number")
    @classmethod
    def _check_phone(cls, v):
        return validate_phone_number(v)


class DoctorCombinedUpdate(BaseSchema):
    """Schema gộp để cập nhật bác sĩ (gộp User và Doctor)"""
    username: Optional[str] = Field(min_length=4, max_length=50, pattern='^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$', default=None)
    full_name: Optional[str] = Field(min_length=2, max_length=50, default=None)
    dob: Optional[date] = None
    gender: Optional[GenderEnum] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None
    specialization: Optional[str] = Field(max_length=250, default=None)
    
    @field_validator("dob")
    @classmethod
    def _check_dob(cls, v):
        return validate_dob_at_least_18(v)

    @field_validator("phone_number")
    @classmethod
    def _check_phone(cls, v):
        return validate_phone_number(v)