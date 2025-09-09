from sqlalchemy import Column, String, Date, Enum, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class GenderEnum(enum.Enum):
    """Enum cho giới tính"""
    MALE = "MALE"
    FEMALE = "FEMALE"

class Patient(Base):
    """Model cho bảng PATIENT - Quản lý thông tin bệnh nhân"""
    __tablename__ = "patients"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Thông tin cơ bản - không được null
    full_name = Column(String, nullable=False)        # Họ tên bệnh nhân
    dob = Column(Date)                                # Ngày sinh
    gender = Column(Enum(GenderEnum))                 # Giới tính
    phone_number = Column(String, nullable=False)     # Số điện thoại
    
    # Thông tin liên lạc và địa chỉ
    email = Column(String)                            # Email
    address = Column(String)                          # Địa chỉ
    
    # Thông tin y tế
    medical_history = Column(String)                  # Tiền sử bệnh lý
    allergies = Column(String)                        # Các chất gây dị ứng
    current_medications = Column(String)              # Thuốc đang sử dụng
    current_condition = Column(String)                # Tình trạng sức khỏe hiện tại
    notes = Column(Text)                             # Ghi chú thêm
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True))     # Soft delete

    # Relationships
    appointments = relationship("Appointment", back_populates="patient")    # Danh sách Appointment của bệnh nhân
    medical_records = relationship("MedicalRecord", back_populates="patient")   # Danh sách MedicalRecord của bệnh nhân
    invoices = relationship("Invoice", back_populates="patient")    # Danh sách Invoice của bệnh nhân