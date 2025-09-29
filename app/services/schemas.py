from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

# Import validators
from app.medications.validators import (
    validate_price,
)

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class ServiceBase(BaseSchema):
    """Schema cơ bản cho Service"""
    name: str = Field(max_length=250)                               # Tên dịch vụ (bắt buộc)
    price: float                            # Giá dịch vụ (bắt buộc)
    description: Optional[str] = Field(max_length=250, default=None)       # Mô tả    

    @field_validator("price")
    @classmethod
    def _check_price(cls, v):
        return validate_price(v)

class ServiceCreate(ServiceBase):
    """Schema tạo Service mới"""
    pass

class ServiceUpdate(BaseSchema):
    """Schema cập nhật Service"""
    name: Optional[str] = Field(max_length=250, default=None)
    price: Optional[float] = None
    description: Optional[str] = Field(max_length=250, default=None)

    @field_validator("price")
    @classmethod
    def _check_price(cls, v):
        return validate_price(v)

class ServiceResponse(ServiceBase):
    """Schema trả về thông tin Service"""
    id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None