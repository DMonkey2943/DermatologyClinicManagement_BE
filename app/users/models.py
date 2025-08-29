from sqlalchemy import Column, Integer, String, Date, Enum, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum
import uuid
from sqlalchemy.dialects.postgresql import UUID

class GenderEnum(enum.Enum):
    """Enum cho giới tính"""
    MALE = "Male"
    FEMALE = "Female"

class UserRoleEnum(enum.Enum):
    """Enum cho vai trò người dùng"""
    ADMIN = "Admin"
    DOCTOR = "Doctor"
    STAFF = "Staff"

class User(Base):
    __tablename__ = "users"  # Tên table trong DB

    # Khóa chính - UUID để đảm bảo tính duy nhất toàn cầu
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True, nullable=False)

    # Thông tin đăng nhập - không được null
    username = Column(String, nullable=False, unique=True, index=True)  # Tên đăng nhập, unique để tránh trùng
    password = Column(String, nullable=False)                          # Mật khẩu đã hash

    # Thông tin cá nhân
    full_name = Column(String)                                         # Họ tên đầy đủ
    dob = Column(Date)                                                # Ngày sinh
    gender = Column(Enum(GenderEnum))                                 # Giới tính (Male/Female)

    # Thông tin liên lạc - không được null
    phone_number = Column(String, unique=True, nullable=False)                     # Số điện thoại
    email = Column(String, nullable=False, unique=True, index=True)   # Email, unique và indexed

    # Thông tin hệ thống
    role = Column(Enum(UserRoleEnum))                                 # Vai trò (Admin/Doctor/Staff)
    avatar = Column(String)                                           # Đường dẫn ảnh đại diện
    is_active = Column(Boolean, default=True, nullable=False)         # Trạng thái hoạt động

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)  # Thời gian tạo
    deleted_at = Column(DateTime(timezone=True))                      # Soft delete - thời gian xóa

    # Relationships - Quan hệ với các bảng khác
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False)           # 1-1 với Doctor
    appointments_as_doctor = relationship("Appointment", foreign_keys="[Appointment.doctor_id]", back_populates="doctor")   # Danh sách Appointment mà user này là bác sĩ.
    appointments_created = relationship("Appointment", foreign_keys="[Appointment.created_by]", back_populates="created_by_user")   # Danh sách Appointment do user (staff) này tạo.
    medical_records = relationship("MedicalRecord", back_populates="doctor")          # Danh sách MedicalRecord mà user này là bác sĩ.
    invoices_as_doctor = relationship("Invoice", foreign_keys="[Invoice.doctor_id]", back_populates="doctor")   # Danh sách Invoice mà user này là bác sĩ.
    invoices_created = relationship("Invoice", foreign_keys="[Invoice.created_by]", back_populates="created_by_user")   # Danh sách Invoice do user (staff) này tạo.


class Doctor(Base):
    __tablename__ = "doctors"

    # Khóa chính
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Khóa ngoại tham chiếu đến User
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    
    # Thông tin chuyên môn
    specialization = Column(String)  # Chuyên khoa của bác sĩ

    # Relationships
    user = relationship("User", back_populates="doctor_profile")  # Quan hệ 1-1 với User