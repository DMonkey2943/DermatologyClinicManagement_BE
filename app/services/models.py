from sqlalchemy import Column, String, DateTime, Double
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Service(Base):
    """Model cho bảng SERVICE - Quản lý dịch vụ"""
    __tablename__ = "services"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Thông tin dịch vụ - không được null
    name = Column(String, nullable=False)       # Tên dịch vụ
    price = Column(Double, nullable=False)      # Giá dịch vụ
    
    # Thông tin bổ sung
    description = Column(String)                # Mô tả dịch vụ
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True))  # Soft delete

    # Relationships
    service_invoice_details = relationship("ServiceInvoiceDetail", back_populates="service")    # Danh sách chi tiết hóa đơn tiền dịch vụ.
    service_indication_details = relationship("ServiceIndicationDetail", back_populates="service")  # Danh sách chi tiết phiếu chỉ định dịch vụ.