from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

# Import validators
from app.medications.validators import (
    validate_price,
    validate_stock_quantity,
)

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class MedicationBase(BaseSchema):
    """Schema cơ bản cho Medication"""
    name: str = Field(min_length=2, max_length=250)                               # Tên thuốc (bắt buộc)
    dosage_form: str = Field(min_length=2, max_length=50)                        # Dạng thuốc (bắt buộc)
    price: float                            # Giá (bắt buộc)
    stock_quantity: int                     # Số lượng tồn kho (bắt buộc)
    description: Optional[str] = Field(max_length=250, default=None)       # Mô tả

    @field_validator("price")
    @classmethod
    def _check_price(cls, v):
        return validate_price(v)

    @field_validator("stock_quantity")
    @classmethod
    def _check_stock_quantity(cls, v):
        return validate_stock_quantity(v)
    

class MedicationCreate(MedicationBase):
    """Schema tạo Medication mới"""
    pass

class MedicationUpdate(BaseSchema):
    """Schema cập nhật Medication"""
    name: Optional[str] = Field(min_length=2, max_length=250, default=None)
    dosage_form: Optional[str] = Field(min_length=2, max_length=50, default=None)
    price: Optional[float] = None
    stock_quantity: Optional[int] = None
    description: Optional[str] = Field(max_length=250, default=None)

    @field_validator("price")
    @classmethod
    def _check_price(cls, v):
        return validate_price(v)

    @field_validator("stock_quantity")
    @classmethod
    def _check_stock_quantity(cls, v):
        return validate_stock_quantity(v)

class MedicationResponse(MedicationBase):
    """Schema trả về thông tin Medication"""
    id: UUID
    created_at: datetime
    deleted_at: Optional[datetime] = None
