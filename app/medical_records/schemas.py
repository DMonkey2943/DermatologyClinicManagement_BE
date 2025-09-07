from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

# Import các enum từ models
from app.medical_records.models import MedicalRecordStatusEnum, ImageTypeEnum

# Import các response từ schemas khác
from app.patients.schemas import PatientResponse
from app.users.schemas import UserResponse

class BaseSchema(BaseModel):
    """Base schema cho tất cả các schema khác"""
    class Config:
        # Cho phép sử dụng ORM objects (SQLAlchemy models)
        from_attributes = True
        # Sử dụng enum values thay vì enum objects
        use_enum_values = True

class MedicalRecordBase(BaseSchema):
    """Schema cơ bản cho Medical Record"""
    patient_id: UUID                        # ID bệnh nhân
    doctor_id: UUID                         # ID bác sĩ
    symptoms: Optional[str] = None          # Triệu chứng
    diagnosis: Optional[str] = None         # Chẩn đoán
    status: MedicalRecordStatusEnum         # Trạng thái
    notes: Optional[str] = None             # Ghi chú
    appointment_id: Optional[UUID] = None   # ID lịch hẹn (nếu có)

class MedicalRecordCreate(MedicalRecordBase):
    """Schema tạo Medical Record mới"""
    pass

class MedicalRecordUpdate(BaseSchema):
    """Schema cập nhật Medical Record"""
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None
    status: Optional[MedicalRecordStatusEnum] = None
    notes: Optional[str] = None

class MedicalRecordResponse(MedicalRecordBase):
    """Schema trả về thông tin Medical Record"""
    id: UUID
    created_at: datetime
    patient: Optional[PatientResponse] = None
    doctor: Optional[UserResponse] = None



# ================================ SKIN IMAGE SCHEMAS ================================
class SkinImageBase(BaseSchema):
    """Schema cơ bản cho Skin Image"""
    medical_record_id: UUID                 # ID hồ sơ y tế
    image_path: str                         # Đường dẫn hình ảnh
    image_type: ImageTypeEnum               # Loại hình ảnh
    ai_results: Optional[str] = None        # Kết quả AI

class SkinImageCreate(SkinImageBase):
    """Schema tạo Skin Image mới"""
    pass

class SkinImageUpdate(BaseSchema):
    """Schema cập nhật Skin Image"""
    ai_results: Optional[str] = None        # Chỉ có thể update kết quả AI

class SkinImageResponse(SkinImageBase):
    """Schema trả về thông tin Skin Image"""
    id: UUID
    created_at: datetime