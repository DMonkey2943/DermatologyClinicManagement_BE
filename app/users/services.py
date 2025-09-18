from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import bcrypt
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate, UserTokenData
from fastapi import HTTPException

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
            raise HTTPException(status_code=404, detail="User not found")

        if not self.verify_password(user_in.get("password", ""), user.password):
            return None
            
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

    def get_users(self, skip: int = 0, limit: int = 10) -> list[User]:
        """Lấy danh sách users với phân trang"""
        users = self.db.query(User).filter(
            User.deleted_at.is_(None)  # Chỉ lấy user chưa bị xóa
        ).offset(skip).limit(limit).all()
        return users
    
    def count_users(self) -> int:
        """
        Đếm tổng số người dùng đang active trong database.
        - Chỉ đếm các user có is_active = True (nếu dùng soft delete).
        - Trả về số nguyên là tổng số bản ghi.
        """
        return self.db.query(User).filter( User.deleted_at.is_(None)).count()
    
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





