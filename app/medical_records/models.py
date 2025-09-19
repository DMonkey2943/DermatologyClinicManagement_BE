from sqlalchemy import Column, DateTime, Enum, ForeignKey, Text, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class MedicalRecordStatusEnum(enum.Enum):
    """Enum cho trạng thái hồ sơ y tế"""
    COMPLETED = "COMPLETED"     # Hoàn thành
    IN_PROGRESS = "IN_PROGRESS" # Đang thực hiện

class ImageTypeEnum(enum.Enum):
    """Enum cho loại hình ảnh da"""
    LEFT = "LEFT"     # Ảnh bên trái
    RIGHT = "RIGHT"   # Ảnh bên phải
    FRONT = "FRONT"   # Ảnh phía trước

class MedicalRecord(Base):
    """Model cho bảng MEDICAL_RECORD - Hồ sơ khám bệnh"""
    __tablename__ = "medical_records"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại - không được null
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    appointment_id = Column(UUID(as_uuid=True), ForeignKey("appointments.id"))
    
    # Thông tin khám bệnh
    symptoms = Column(Text)                                    # Triệu chứng
    diagnosis = Column(Text)                                   # Chẩn đoán
    status = Column(Enum(MedicalRecordStatusEnum), nullable=False)  # Trạng thái
    notes = Column(Text)                                       # Ghi chú
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="medical_records")
    doctor = relationship("User", back_populates="medical_records")
    appointment = relationship("Appointment", back_populates="medical_records")
    skin_images = relationship("SkinImage", back_populates="medical_record")
    prescriptions = relationship("Prescription", back_populates="medical_record")
    service_indications = relationship("ServiceIndications", back_populates="medical_record")
    invoices = relationship("Invoice", back_populates="medical_record")


class SkinImage(Base):
    """Model cho bảng SKIN_IMAGE - Hình ảnh da của bệnh nhân"""
    __tablename__ = "skin_images"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại - không được null
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False)
    
    # Thông tin hình ảnh - không được null
    image_path = Column(String, nullable=False)                    # Đường dẫn lưu hình ảnh
    image_type = Column(Enum(ImageTypeEnum), nullable=False)       # Loại ảnh (LEFT/RIGHT/FRONT)
    
    # Kết quả AI
    ai_results = Column(String)                                    # Kết quả phân tích bằng AI
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="skin_images")