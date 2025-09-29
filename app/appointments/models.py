from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Date, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

from app.patients.models import Patient

class AppointmentStatusEnum(enum.Enum):
    """Enum cho trạng thái lịch hẹn"""
    SCHEDULED = "SCHEDULED"     # Đã lên lịch
    WAITING = "WAITING"         # Đang chờ
    COMPLETED = "COMPLETED"     # Hoàn thành
    CANCELLED = "CANCELLED"     # Hủy bỏ

class Appointment(Base):
    """Model cho bảng APPOINTMENT - Quản lý lịch hẹn khám"""
    __tablename__ = "appointments"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại - không được null
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Thông tin lịch hẹn - không được null
    appointment_date = Column(Date, nullable=False)                           # Ngày hẹn
    appointment_time = Column(Time)                                          # Giờ hẹn
    time_slot = Column(String, nullable=False)                               # Khung giờ hẹn 
    status = Column(Enum(AppointmentStatusEnum), nullable=False)             # Trạng thái lịch hẹn
    
    # Thông tin bổ sung
    notes = Column(Text)                                                     # Ghi chú
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    patient = relationship(lambda: Patient, back_populates="appointments")    
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="appointments_as_doctor")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="appointments_created")
    medical_records = relationship("MedicalRecord", back_populates="appointment")