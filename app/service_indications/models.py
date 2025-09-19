from sqlalchemy import Column, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class ServiceIndication(Base):
    """Model cho bảng SERVICE_INDICATION - Phiếu chỉ định dịch vụ"""
    __tablename__ = "service_indications"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại - không được null
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False)
    
    # Thông tin phiếu chỉ định dịch vụ
    notes = Column(Text)                                           # Ghi chú cho phiếu chỉ định dịch vụ
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="service_indications")
    service_indication_details = relationship("ServiceIndicationDetail", back_populates="service_indication")


class ServiceIndicationDetail(Base):
    """Model cho bảng SERVICE_INDICATION_DETAIL - Chi tiết phiếu chỉ định dịch vụ"""
    __tablename__ = "service_indication_details"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại - không được null
    service_indication_id = Column(UUID(as_uuid=True), ForeignKey("service_indications.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    
    # Thông tin chi tiết
    quantity = Column(Integer)              # Số lượng

    # Relationships
    service_indication = relationship("ServiceIndication", back_populates="service_indication_details")
    service = relationship("Service", back_populates="service_indication_details")
