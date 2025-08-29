from sqlalchemy import Column, DateTime, Text, ForeignKey, String, Integer, Double
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Prescription(Base):
    """Model cho bảng PRESCRIPTION - Đơn thuốc"""
    __tablename__ = "prescriptions"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại - không được null
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False)
    
    # Thông tin đơn thuốc
    notes = Column(Text)                                           # Ghi chú cho đơn thuốc
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="prescriptions")
    prescription_details = relationship("PrescriptionDetail", back_populates="prescription")


class PrescriptionDetail(Base):
    """Model cho bảng PRESCRIPTION_DETAIL - Chi tiết đơn thuốc"""
    __tablename__ = "prescription_details"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại - không được null
    prescription_id = Column(UUID(as_uuid=True), ForeignKey("prescriptions.id"), nullable=False)
    medication_id = Column(UUID(as_uuid=True), ForeignKey("medications.id"), nullable=False)
    
    # Thông tin chi tiết
    quantity = Column(Integer)                                     # Số lượng thuốc
    dosage = Column(String)                                        # Liều lượng (VD: "1 viên x 2 lần/ngày")
    unit_price = Column(Double)                                    # Giá đơn vị

    # Relationships
    prescription = relationship("Prescription", back_populates="prescription_details")
    medication = relationship("Medication", back_populates="prescription_details")
