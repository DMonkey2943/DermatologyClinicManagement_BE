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

class MedicationBase(BaseSchema):
    """Schema cơ bản cho Medication"""
    name: str                               # Tên thuốc (bắt buộc)
    dosage_form: str                        # Dạng thuốc (bắt buộc)
    price: float                            # Giá (bắt buộc)
    stock_quantity: int                     # Số lượng tồn kho (bắt buộc)
    description: Optional[str] = None       # Mô tả

    @validator('price')
    def validate_price(cls, v):
        """Validator để đảm bảo giá >= 0"""
        if v < 0:
            raise ValueError('Giá không thể âm')
        return v

    @validator('stock_quantity')
    def validate_stock_quantity(cls, v):
        """Validator để đảm bảo số lượng >= 0"""
        if v < 0:
            raise ValueError('Số lượng tồn kho không thể âm')
        return v

class MedicationCreate(MedicationBase):
    """Schema tạo Medication mới"""
    pass

class MedicationUpdate(BaseSchema):
    """Schema cập nhật Medication"""
    name: Optional[str] = None
    dosage_form: Optional[str] = None
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    description: Optional[str] = None

class MedicationResponse(MedicationBase):
    """Schema trả về thông tin Medication"""
    id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None
