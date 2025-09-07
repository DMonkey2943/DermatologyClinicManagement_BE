from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from uuid import UUID

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class ServiceBase(BaseSchema):
    """Schema cơ bản cho Service"""
    name: str                               # Tên dịch vụ (bắt buộc)
    price: float                            # Giá dịch vụ (bắt buộc)
    description: Optional[str] = None       # Mô tả

    @validator('price')
    def validate_price(cls, v):
        """Validator để đảm bảo giá >= 0"""
        if v < 0:
            raise ValueError('Giá dịch vụ không thể âm')
        return v

class ServiceCreate(ServiceBase):
    """Schema tạo Service mới"""
    pass

class ServiceUpdate(BaseSchema):
    """Schema cập nhật Service"""
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None

class ServiceResponse(ServiceBase):
    """Schema trả về thông tin Service"""
    id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None