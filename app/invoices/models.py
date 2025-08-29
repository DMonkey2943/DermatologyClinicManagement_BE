from sqlalchemy import Column, DateTime, Integer, Double, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Invoice(Base):
    """Model cho bảng INVOICE - Hóa đơn thanh toán"""
    __tablename__ = "invoices"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại - không được null
    medical_record_id = Column(UUID(as_uuid=True), ForeignKey("medical_records.id"), nullable=False)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    doctor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Thông tin tài chính
    service_subtotal = Column(Double)                              # Tổng tiền dịch vụ
    medication_subtotal = Column(Double)                           # Tổng tiền thuốc
    total_amount = Column(Double)                                  # Tổng cộng
    discount_amount = Column(Double)                               # Số tiền giảm giá
    final_amount = Column(Double)                                  # Thành tiền cuối cùng
    
    # Thông tin bổ sung
    notes = Column(Text)                                           # Ghi chú
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="invoices")
    patient = relationship("Patient", back_populates="invoices")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="invoices_as_doctor")
    created_by_user = relationship("User", foreign_keys=[created_by], back_populates="invoices_created")
    service_invoice_details = relationship("ServiceInvoiceDetail", back_populates="invoice")
    medication_invoice_details = relationship("MedicationInvoiceDetail", back_populates="invoice")


class ServiceInvoiceDetail(Base):
    """Model cho bảng SERVICE_INVOICE_DETAIL - Chi tiết dịch vụ trong hóa đơn"""
    __tablename__ = "service_invoice_details"

    # Khóa ngoại làm khóa chính kép
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), primary_key=True)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), primary_key=True)
    
    # Thông tin chi tiết
    quantity = Column(Integer)                                     # Số lượng dịch vụ
    unit_price = Column(Double)                                    # Giá đơn vị
    total_price = Column(Double)                                   # Thành tiền
    notes = Column(Text)                                           # Ghi chú

    # Relationships
    invoice = relationship("Invoice", back_populates="service_invoice_details")
    service = relationship("Service", back_populates="service_invoice_details")


class MedicationInvoiceDetail(Base):
    """Model cho bảng MEDICATION_INVOICE_DETAIL - Chi tiết thuốc trong hóa đơn"""
    __tablename__ = "medication_invoice_details"

    # Khóa ngoại làm khóa chính kép
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), primary_key=True)
    medication_id = Column(UUID(as_uuid=True), ForeignKey("medications.id"), primary_key=True)
    
    # Thông tin chi tiết
    quantity = Column(Integer)                                     # Số lượng thuốc
    unit_price = Column(Double)                                    # Giá đơn vị
    total_price = Column(Double)                                   # Thành tiền
    notes = Column(Text)                                           # Ghi chú

    # Relationships
    invoice = relationship("Invoice", back_populates="medication_invoice_details")
    medication = relationship("Medication", back_populates="medication_invoice_details")