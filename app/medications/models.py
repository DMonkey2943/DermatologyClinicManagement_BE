from sqlalchemy import Column, String, DateTime, Integer, Double
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Medication(Base):
    """Model cho bảng MEDICATION - Quản lý thuốc"""
    __tablename__ = "medications"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Thông tin thuốc - không được null
    name = Column(String, nullable=False)             # Tên thuốc
    dosage_form = Column(String, nullable=False)      # Dạng thuốc (Viên, Chai, Tuýp, v.v.)
    price = Column(Double, nullable=False)            # Giá bán
    stock_quantity = Column(Integer, nullable=False)  # Số lượng tồn kho
    
    # Thông tin bổ sung
    description = Column(String)                      # Mô tả thuốc
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True))     # Soft delete

    # Relationships
    prescription_details = relationship("PrescriptionDetail", back_populates="medication")  # Danh sách chi tiết đơn thuốc.
    medication_invoice_details = relationship("MedicationInvoiceDetail", back_populates="medication")   # Danh sách chi tiết hóa đơn tiền thuốc.
