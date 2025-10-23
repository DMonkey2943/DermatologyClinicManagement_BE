from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Import các response từ schemas khác
from app.patients.schemas import PatientResponse
from app.prescriptions.schemas import PrescriptionDetailResponse
from app.service_indications.schemas import ServiceIndicationDetailResponse
from app.users.schemas import UserForeignKeyResponse, UserResponse
from app.services.schemas import ServiceResponse
from app.medications.schemas import MedicationResponse

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        from_attributes = True
        use_enum_values = True

class InvoiceBase(BaseSchema):
    """Schema cơ bản cho Invoice"""
    medical_record_id: UUID
    patient_id: UUID
    doctor_id: UUID
    created_by: UUID
    service_subtotal: Optional[float] = None
    medication_subtotal: Optional[float] = None
    total_amount: float = None
    discount_amount: Optional[float] = None
    final_amount: float = None
    notes: Optional[str] = None

    @validator('total_amount')
    def validate_total_amount(cls, v):
        """Validator để đảm bảo giá tổng cộng >= 0"""
        if v < 0:
            raise ValueError('Giá tổng cộng không thể âm')
        return v

    @validator('final_amount')
    def validate_final_amount(cls, v):
        """Validator để đảm bảo thành tiền >= 0"""
        if v < 0:
            raise ValueError('Thành tiền không thể âm')
        return v

class InvoiceCreate(InvoiceBase):
    """Schema tạo Invoice mới"""
    pass

class InvoiceUpdate(BaseSchema):
    """Schema cập nhật Invoice"""
    service_subtotal: Optional[float] = None
    medication_subtotal: Optional[float] = None
    total_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    final_amount: Optional[float] = None
    notes: Optional[str] = None

class InvoiceResponse(InvoiceBase):
    """Schema trả về thông tin Invoice"""
    id: UUID
    created_at: datetime
    patient: Optional[PatientResponse] = None
    doctor: Optional[UserForeignKeyResponse] = None
    created_by_user: Optional[UserForeignKeyResponse] = None
    # service_invoice_details: Optional[List["ServiceInvoiceDetailResponse"]] = None
    # medication_invoice_details: Optional[List["MedicationInvoiceDetailResponse"]] = None

class InvoiceFullResponse(InvoiceResponse):
    """Schema trả về thông tin Invoice full"""
    medications: Optional[List[PrescriptionDetailResponse]] = None
    services: Optional[List[ServiceIndicationDetailResponse]] = None



# ================================ SERVICE INVOICE DETAIL SCHEMAS ================================
class ServiceInvoiceDetailBase(BaseSchema):
    """Schema cơ bản cho Service Invoice Detail"""
    invoice_id: UUID
    service_id: UUID
    quantity: int = None
    unit_price: float = None
    total_price: float = None
    notes: Optional[str] = None

class ServiceInvoiceDetailCreate(ServiceInvoiceDetailBase):
    """Schema tạo Service Invoice Detail mới"""
    pass

class ServiceInvoiceDetailUpdate(BaseSchema):
    """Schema cập nhật Service Invoice Detail"""
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    notes: Optional[str] = None

class ServiceInvoiceDetailResponse(ServiceInvoiceDetailBase):
    """Schema trả về thông tin Service Invoice Detail"""
    service: Optional[ServiceResponse] = None



# ================================ MEDICATION INVOICE DETAIL SCHEMAS ================================
class MedicationInvoiceDetailBase(BaseSchema):
    """Schema cơ bản cho Medication Invoice Detail"""
    invoice_id: UUID
    medication_id: UUID
    quantity: int = None
    unit_price: float = None
    total_price: float = None
    notes: Optional[str] = None

class MedicationInvoiceDetailCreate(MedicationInvoiceDetailBase):
    """Schema tạo Medication Invoice Detail mới"""
    pass

class MedicationInvoiceDetailUpdate(BaseSchema):
    """Schema cập nhật Medication Invoice Detail"""
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    notes: Optional[str] = None

class MedicationInvoiceDetailResponse(MedicationInvoiceDetailBase):
    """Schema trả về thông tin Medication Invoice Detail"""
    medication: Optional[MedicationResponse] = None

# Để hỗ trợ forward reference cho các response chứa list chi tiết
InvoiceResponse.update_forward_refs()
