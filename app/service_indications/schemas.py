from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import enum

# Import các response từ schemas khác
from app.services.schemas import ServiceResponse

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class ServiceIndicationBase(BaseSchema):
    """Schema cơ bản cho ServiceIndication"""
    medical_record_id: UUID                 # ID lịch sử khám bệnh
    notes: Optional[str] = None             # Ghi chú

class ServiceIndicationDetailInput(BaseSchema):
    """Schema input cho ServiceIndication Detail khi tạo"""
    service_id: UUID                        # ID thuốc
    quantity: int                           # Số lượng thuốc

class ServiceIndicationCreate(ServiceIndicationBase):
    """Schema tạo ServiceIndication mới"""
    service_indication_details: Optional[List[ServiceIndicationDetailInput]] = None

class ServiceIndicationUpdate(BaseSchema):
    """Schema cập nhật ServiceIndication"""
    notes: Optional[str] = None
    service_indication_details: Optional[List[ServiceIndicationDetailInput]] = None

class ServiceIndicationResponse(ServiceIndicationBase):
    """Schema trả về thông tin ServiceIndication"""
    id: UUID
    created_at: datetime



# ================================ ServiceIndication DETAIL SCHEMAS ================================
class ServiceIndicationDetailBase(BaseSchema):
    """Schema cơ bản cho ServiceIndication Detail"""
    service_indication_id: UUID             # ID phiếu chỉ định dịch vụ
    service_id: UUID                        # ID dịch vụ
    name: str                               # Tên dịch vụ
    quantity: int                           # Số lượng
    unit_price: float                       # Giá đơn vị
    total_price: float                      # Thành tiền

    @validator('quantity')
    def validate_quantity(cls, v):
        """Validator để đảm bảo số lượng >= 0"""
        if v < 0:
            raise ValueError('Số lượng thuốc không thể âm')
        return v

class ServiceIndicationDetailCreate(ServiceIndicationDetailBase):
    """Schema tạo ServiceIndication Detail mới"""
    pass

class ServiceIndicationDetailUpdate(BaseSchema):
    """Schema cập nhật ServiceIndication Detail"""
    service_indication_id: Optional[UUID] = None   
    service_id: Optional[UUID] = None        
    name: Optional[str] = None             
    quantity: Optional[int] = None                
    unit_price: Optional[float] = None          
    total_price: Optional[float] = None   

class ServiceIndicationDetailResponse(ServiceIndicationDetailBase):
    """Schema trả về thông tin ServiceIndication Detail"""
    id: UUID
    # service: Optional[ServiceResponse] = None

class ServiceIndicationFullResponse(ServiceIndicationBase):
    """Schema trả về thông tin ServiceIndication"""
    id: UUID
    created_at: datetime
    services: Optional[List[ServiceIndicationDetailResponse]] = None
    service_indication_details: Optional[List[ServiceIndicationDetailResponse]] = None

    