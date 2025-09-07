from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

# Import các response từ schemas khác
from app.medications.schemas import MedicationResponse

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class PrescriptionBase(BaseSchema):
    """Schema cơ bản cho Prescription"""
    medical_record_id: UUID                 # ID lịch sử khám bệnh
    notes: Optional[str] = None             # Ghi chú

class PrescriptionCreate(PrescriptionBase):
    """Schema tạo Prescription mới"""
    pass

class PrescriptionUpdate(BaseSchema):
    """Schema cập nhật Prescription"""
    notes: Optional[str] = None

class PrescriptionResponse(PrescriptionBase):
    """Schema trả về thông tin Prescription"""
    id: UUID
    created_at: datetime



# ================================ PRESCRIPTION DETAIL SCHEMAS ================================
class PrescriptionDetailBase(BaseSchema):
    """Schema cơ bản cho Prescription Detail"""
    medical_record_id: UUID                 # ID hồ sơ y tế
    medication_id: UUID                     # ID thuốc
    quantity: int                           # Số lượng thuốc
    dosage: Optional[str] = None            # Liều lượng (VD: "1 viên x 2 lần/ngày")
    unit_price: float                       # Giá đơn vị

    @validator('quantity')
    def validate_quantity(cls, v):
        """Validator để đảm bảo số lượng >= 0"""
        if v < 0:
            raise ValueError('Số lượng thuốc không thể âm')
        return v

class PrescriptionDetailCreate(PrescriptionDetailBase):
    """Schema tạo Prescription Detail mới"""
    pass

class PrescriptionDetailUpdate(BaseSchema):
    """Schema cập nhật Prescription Detail"""
    medical_record_id: Optional[UUID] = None   
    medication_id: Optional[UUID] = None        
    quantity: Optional[int] = None             
    dosage: Optional[str] = None                
    unit_price: Optional[float] = None          

class PrescriptionDetailResponse(PrescriptionDetailBase):
    """Schema trả về thông tin Prescription Detail"""
    id: UUID
    medication: Optional[MedicationResponse] = None
    