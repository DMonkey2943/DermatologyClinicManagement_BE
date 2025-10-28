from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import bcrypt
from app.users.models import User, Doctor
from app.users.schemas import UserCreate, UserUpdate, UserTokenData, UserResponse, DoctorCombinedCreate, DoctorCombinedUpdate, DoctorResponse
from fastapi import HTTPException, UploadFile
from app.core.response import ErrorResponse
from app.utils.file_handler import file_handler

class UserService:
    """Service class để xử lý logic liên quan đến User"""
    def __init__(self, db: Session):
        self.db = db  # Inject DB session
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Mã hóa password"""
        # Chuyển password thành bytes và hash với bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Xác thực password"""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def validate_login(self, user_in: dict) -> Optional[User]:
        # user = (
        #     self.db.query(User)
        #     .filter(User.username == user_in.get("username"))
        #     .first()
        # )
        user = self.get_user_by_username(user_in.get("username", ""))
        if not user:
            # return None
            raise HTTPException(status_code=401, detail="Username không tồn tại")

        if not self.verify_password(user_in.get("password", ""), user.password):
            raise HTTPException(status_code=401, detail="Username hoặc mật khẩu chưa chính xác")
            
        return UserTokenData.model_validate(user)

    def create_user(self, user_in: UserCreate) -> User:
        """Tạo user mới"""
        # Hash password trước khi lưu
        hashed_password = self.get_password_hash(user_in.password)
        
        # Tạo đối tượng User từ schema
        db_user = User(
            username=user_in.username,
            password=hashed_password,  # Lưu password đã hash
            full_name=user_in.full_name,
            dob=user_in.dob,
            gender=user_in.gender,
            phone_number=user_in.phone_number,
            email=user_in.email,
            role=user_in.role,
            avatar=user_in.avatar
        )
        
        # Thêm vào database
        self.db.add(db_user)
        self.db.commit()           # Commit transaction
        self.db.refresh(db_user)   # Refresh để lấy ID và timestamp
        return db_user
    
    async def create_user_with_avatar(self, user_in: UserCreate, avatar: Optional[UploadFile] = None) -> User:
        """
        Tạo user mới kèm avatar
        - Upload avatar nếu có
        - Tạo user với avatar URL
        
        Args:
            user_in: Dữ liệu user từ request
            avatar: File avatar upload (optional)
        """
        # Upload avatar nếu có
        avatar_url = None
        if avatar:
            avatar_url = await file_handler.save_upload_file(avatar)

        # Hash password trước khi lưu
        hashed_password = self.get_password_hash(user_in.password)
        
        # Tạo đối tượng User từ schema
        db_user = User(
            username=user_in.username,
            password=hashed_password,  # Lưu password đã hash
            full_name=user_in.full_name,
            dob=user_in.dob,
            gender=user_in.gender,
            phone_number=user_in.phone_number,
            email=user_in.email,
            role=user_in.role,
            avatar=avatar_url
        )
        
        # Thêm vào database
        self.db.add(db_user)
        self.db.commit()           # Commit transaction
        self.db.refresh(db_user)   # Refresh để lấy ID và timestamp
        return db_user

    # @staticmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Lấy user theo ID"""
        db_user = self.db.query(User).filter(and_(User.id == user_id, User.deleted_at.is_(None))).first()
        if not db_user:
            return None
        return db_user

    # @staticmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Lấy user theo ID"""
        db_user = self.db.query(User).filter(and_(User.id == user_id, User.deleted_at.is_(None))).first()
        if not db_user:
            return None
        return db_user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Lấy user theo email"""
        db_user = self.db.query(User).filter(and_(User.email == email, User.deleted_at.is_(None))).first()
        if not db_user:
            return None
        return db_user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Lấy user theo username"""
        db_user = self.db.query(User).filter(and_(User.username == username, User.deleted_at.is_(None))).first()
        if not db_user:
            return None
        return db_user

    def get_users(self, skip: int = 0, limit: int = 10, q: Optional[str] = None) -> list[User]:
        """Lấy danh sách users với phân trang và hỗ trợ tìm kiếm theo full_name (case-insensitive) hoặc username hoặc phone_number"""
        query = self.db.query(User).filter(User.deleted_at.is_(None))
        if q:
            term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(term),
                    User.username.ilike(term),
                    User.phone_number.ilike(term)
                )
            )
        users = query.offset(skip).limit(limit).all()
        return users
    
    def count_users(self, q: Optional[str] = None) -> int:
        """
        Đếm tổng số người dùng đang active trong database hoặc theo search query nếu q được cung cấp.
        """
        query = self.db.query(User).filter(User.deleted_at.is_(None))
        if q:
            term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(term),
                    User.username.ilike(term),
                    User.phone_number.ilike(term)
                )
            )
        return query.count()
    
    def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Cập nhật thông tin user"""
        db_user = self.get_user_by_id(user_id)
        
        # Cập nhật các trường
        update_data = user_update.dict(exclude_unset=True)  # Chỉ lấy các trường được set
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: UUID) -> bool:
        """ Xóa mềm User (set deleted_at)"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False

        db_user.deleted_at = datetime.utcnow()
        db_user.is_active = False
        self.db.commit()
        return True



class DoctorService:
    """Service class để xử lý logic liên quan đến Doctor"""
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)

    def create_doctor(self, doctor_in: DoctorCombinedCreate) -> DoctorResponse:
        """Tạo bác sĩ mới (bao gồm cả User và Doctor) từ schema gộp"""
        # Tạo UserCreate từ DoctorCombinedCreate
        user_in = UserCreate(
            username=doctor_in.username,
            password=doctor_in.password,
            full_name=doctor_in.full_name,
            dob=doctor_in.dob,
            gender=doctor_in.gender,
            phone_number=doctor_in.phone_number,
            email=doctor_in.email,
            role="DOCTOR",  # Đảm bảo role là DOCTOR
            avatar=doctor_in.avatar
        )
        
        # Tạo User
        db_user = self.user_service.create_user(user_in)
        
        # Tạo Doctor
        db_doctor = Doctor(
            user_id=db_user.id,
            specialization=doctor_in.specialization
        )
        
        self.db.add(db_doctor)
        self.db.commit()
        self.db.refresh(db_doctor)
        
        # Tạo response với thông tin User
        doctor_response = DoctorResponse(
            id=db_doctor.id,
            user_id=db_doctor.user_id,
            specialization=db_doctor.specialization,
            user=UserResponse.from_orm(db_user)
        )
        return doctor_response

    def get_doctor_by_id(self, doctor_id: UUID) -> Optional[Doctor]:
        """Lấy bác sĩ theo ID"""
        db_doctor = self.db.query(Doctor).filter(and_(Doctor.id == doctor_id)).first()
        if not db_doctor:
            return None
            
        # Lấy thông tin User liên kết
        db_user = self.user_service.get_user_by_id(db_doctor.user_id)
        if not db_user:
            return None
            
        # Tạo response với thông tin User
        doctor_response = DoctorResponse(
            id=db_doctor.id,
            user_id=db_doctor.user_id,
            specialization=db_doctor.specialization,
            user=UserResponse.from_orm(db_user)
        )
        return doctor_response

    def get_doctors(self, skip: int = 0, limit: int = 10) -> list[Doctor]:
        """Lấy danh sách bác sĩ với phân trang"""
        doctors = self.db.query(Doctor).offset(skip).limit(limit).all()
        result = []
        for doctor in doctors:
            user = self.user_service.get_user_by_id(doctor.user_id)
            if user:
                doctor_response = DoctorResponse(
                    id=doctor.id,
                    user_id=doctor.user_id,
                    specialization=doctor.specialization,
                    user=UserResponse.from_orm(user)
                )
                result.append(doctor_response)
        return result

    def count_doctors(self) -> int:
        """Đếm tổng số bác sĩ"""
        return self.db.query(Doctor).filter(Doctor.deleted_at.is_(None)).count()

    def update_doctor(self, doctor_id: UUID, doctor_update: DoctorCombinedUpdate) -> Optional[DoctorResponse]:
        """Cập nhật thông tin bác sĩ (bao gồm cả User) từ schema gộp"""
        db_doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not db_doctor:
            return None

        # Lấy thông tin User hiện tại
        db_user = self.user_service.get_user_by_id(db_doctor.user_id)
        if not db_user:
            return None

        # Tạo UserUpdate từ DoctorCombinedUpdate
        user_update = UserUpdate(
            username=doctor_update.username if doctor_update.username is not None else db_user.username,
            full_name=doctor_update.full_name if doctor_update.full_name is not None else db_user.full_name,
            dob=doctor_update.dob if doctor_update.dob is not None else db_user.dob,
            gender=doctor_update.gender if doctor_update.gender is not None else db_user.gender,
            phone_number=doctor_update.phone_number if doctor_update.phone_number is not None else db_user.phone_number,
            email=doctor_update.email if doctor_update.email is not None else db_user.email,
            avatar=doctor_update.avatar if doctor_update.avatar is not None else db_user.avatar,
            is_active=doctor_update.is_active if doctor_update.is_active is not None else db_user.is_active
        )

        # Cập nhật User
        db_user = self.user_service.update_user(db_doctor.user_id, user_update)
        if not db_user:
            return None

        # Cập nhật Doctor
        if doctor_update.specialization is not None:
            db_doctor.specialization = doctor_update.specialization

        self.db.commit()
        self.db.refresh(db_doctor)

        # Tạo response với thông tin User
        doctor_response = DoctorResponse(
            id=db_doctor.id,
            user_id=db_doctor.user_id,
            specialization=db_doctor.specialization,
            user=UserResponse.from_orm(db_user)
        )
        return doctor_response

    def delete_doctor(self, doctor_id: UUID) -> bool:
        """Xóa bác sĩ (bao gồm cả User - soft delete)"""
        db_doctor = self.db.query(Doctor).filter(Doctor.id == doctor_id).first()
        if not db_doctor:
            return False

        # Xóa User liên kết
        success = self.user_service.delete_user(db_doctor.user_id)
        if not success:
            return False
        
        # Xóa Doctor
        db_doctor.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
