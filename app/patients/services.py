from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from fastapi import HTTPException, UploadFile, status
from uuid import UUID
from datetime import datetime
import bcrypt
from app.patients.models import Patient
from app.patients.schemas import PatientCreate, PatientTokenData, PatientUpdate
from app.utils.email import send_email_async
from fastapi import BackgroundTasks  # Để chạy async task trong sync context nếu cần

class PatientService:
    """Service class để xử lý logic liên quan đến Patient"""
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
    
    def validate_login(self, patient_in: dict) -> Optional[Patient]:
        # user = (
        #     self.db.query(User)
        #     .filter(User.username == patient_in.get("username"))
        #     .first()
        # )
        # patient = self.get_patient_by_phone_number(patient_in.get("phone_number", ""))
        patient = self.get_patient_by_email(patient_in.get("email", ""))
        if not patient:
            # return None
            raise HTTPException(status_code=401, detail="Email không tồn tại")
        
        if not patient.password:
            raise HTTPException(status_code=401, detail="Bạn chưa có tài khoản. Hãy liên hệ với phòng khám để được cấp tài khoản!")

        if not self.verify_password(patient_in.get("password", ""), patient.password):
            raise HTTPException(status_code=401, detail="Email hoặc mật khẩu chưa chính xác")
            
        return PatientTokenData.model_validate(patient)

    def create_patient(self, patient_in: PatientCreate, background_tasks: BackgroundTasks) -> Patient:
        """Tạo bệnh nhân mới"""
        password = None
        if patient_in.password:
            # Hash password trước khi lưu
            password = self.get_password_hash(patient_in.password)
            # db_patient = Patient(
            #     full_name=patient_in.full_name,
            #     dob=patient_in.dob,
            #     gender=patient_in.gender,
            #     phone_number=patient_in.phone_number,
            #     password=hashed_password,  # Lưu password đã hash
            #     address=patient_in.address,
            #     medical_history=patient_in.medical_history,
            #     allergies=patient_in.allergies,
            # )
        # else:
        #     db_patient = Patient(**patient_in.dict())
        db_patient = Patient(
            full_name=patient_in.full_name,
            dob=patient_in.dob,
            gender=patient_in.gender,
            phone_number=patient_in.phone_number,
            password=password,  # Lưu password
            address=patient_in.address,
            medical_history=patient_in.medical_history,
            allergies=patient_in.allergies,
        )
        
        # Thêm vào database
        self.db.add(db_patient)
        self.db.commit()           # Commit transaction
        self.db.refresh(db_patient)   # Refresh để lấy ID và timestamp

        # Gửi email async qua background task nếu có password và email
        if(patient_in.password and patient_in.email):
            subject = "[FORSKIN] THÔNG TIN TÀI KHOẢN BỆNH NHÂN HỆ THỐNG QUẢN LÝ PHÒNG KHÁM DA LIỄU"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                    <h3>Xin chào {db_patient.full_name},</h3>
                    <p>Tài khoản bệnh nhân của bạn đã được tạo thành công trên hệ thống quản lý phòng khám.</p>
                    <div style="background:#f4f4f4; padding:15px; border-radius:8px; margin:20px 0;">
                        <p><strong>Email đăng nhập:</strong> {db_patient.email}</p>
                        {f'<p><strong>Mật khẩu tạm:</strong> {patient_in.password}</p>' if patient_in.password else ''}
                    </div>
                    <p>Vui lòng đổi ngay sau khi đăng nhập!</p>
                    <p><a href="http://localhost:3000/signin-patient" style="color:#0066cc;">Đăng nhập ngay</a></p>
                </body>
            </html>
            """
            background_tasks.add_task(send_email_async, db_patient.email, subject, body)

        return db_patient

    # @staticmethod
    def get_patient_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """Lấy thông tin bệnh nhân theo ID"""
        db_patient = self.db.query(Patient).filter(and_(Patient.id == patient_id, Patient.deleted_at.is_(None))).first()
        if not db_patient:
            return None
        return db_patient

    def get_patients(self, skip: int = 0, limit: int = 10, q: Optional[str] = None) -> list[Patient]:
        """Lấy danh sách patients với phân trang"""
        query = self.db.query(Patient).filter(
            Patient.deleted_at.is_(None)  # Chỉ lấy bệnh nhân chưa bị xóa
        )
        if q:
            term = f"%{q.strip()}%"
            query = query.filter(
                or_(
                    Patient.full_name.ilike(term),
                    Patient.phone_number.ilike(term)
                )
            )

        patients = query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()
        return patients
    
    def search_patients(self, search_term: str, skip: int = 0, limit: int = 100) -> List[Patient]:
        """Tìm kiếm bệnh nhân theo tên hoặc số điện thoại"""
        searched_patients = self.db.query(Patient).filter(
            and_(
                Patient.deleted_at.is_(None),
                or_(
                    Patient.full_name.ilike(f"%{search_term}%"),
                    Patient.phone_number.ilike(f"%{search_term}%")
                )
            )
        ).offset(skip).limit(limit).all()
        return searched_patients
    
    def count_patients(self, search_term: Optional[str] = None) -> int:
        """
        Đếm tổng số bệnh nhân đang active, hỗ trợ tìm kiếm theo tên hoặc số điện thoại.
        - Nếu search_term được cung cấp, đếm các bệnh nhân khớp với tìm kiếm.
        - Nếu không, đếm tất cả bệnh nhân active.
        """
        query = self.db.query(Patient).filter(Patient.deleted_at.is_(None))
        if search_term:
            search = f"%{search_term.strip()}%"
            query = query.filter(
                or_(
                    Patient.full_name.ilike(search),
                    Patient.phone_number.ilike(search)
                )
            )
        return query.count()
    
    def update_patient(self, patient_id: UUID, patient_update: PatientUpdate, background_tasks: BackgroundTasks) -> Optional[Patient]:
        """Cập nhật thông tin bệnh nhân"""
        db_patient = self.get_patient_by_id(patient_id)
        
        # Cập nhật các trường
        update_data = patient_update.dict(exclude_unset=True)  # Chỉ lấy các trường được set

        # Xử lý password riêng nếu có
        if 'password' in update_data and update_data['password']:
            hashed_password = self.get_password_hash(update_data['password'])
            setattr(db_patient, 'password', hashed_password)
            del update_data['password']  # Xóa password khỏi update_data để tránh lưu password gốc

        # Cập nhật các trường còn lại
        for field, value in update_data.items():
            setattr(db_patient, field, value)
        
        self.db.commit()
        self.db.refresh(db_patient)

        # Gửi email async qua background task nếu có password và email
        if(patient_update.password and patient_update.email):
            subject = "[FORSKIN] CẬP NHẬT MẬT KHẨU TÀI KHOẢN BỆNH NHÂN HỆ THỐNG QUẢN LÝ PHÒNG KHÁM DA LIỄU"
            body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                    <h3>Xin chào {db_patient.full_name},</h3>
                    <p>Tài khoản bệnh nhân của bạn đã được cập nhật thành công trên hệ thống quản lý phòng khám.</p>
                    <div style="background:#f4f4f4; padding:15px; border-radius:8px; margin:20px 0;">
                        <p><strong>Email đăng nhập:</strong> {db_patient.email}</p>
                        <p><strong>Mật khẩu mới:</strong> {update_data['password']}</p>
                    </div>
                    <p>Vui lòng đổi ngay sau khi đăng nhập!</p>
                    <p><a href="http://localhost:3000/signin-patient" style="color:#0066cc;">Đăng nhập ngay</a></p>
                </body>
            </html>
            """
            background_tasks.add_task(send_email_async, db_patient.email, subject, body)

        return db_patient

    def delete_patient(self, patient_id: UUID) -> bool:
        """ Xóa mềm bệnh nhân (set deleted_at)"""
        db_patient = self.get_patient_by_id(patient_id)
        if not db_patient:
            return False

        db_patient.deleted_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def get_patient_by_phone_number(self, phone_number: str) -> Optional[Patient]:
        """Lấy patient theo phone_number"""
        db_patient = self.db.query(Patient).filter(and_(Patient.phone_number == phone_number, Patient.deleted_at.is_(None))).first()
        if not db_patient:
            return None
        return db_patient
    
    def get_patient_by_email(self, email: str) -> Optional[Patient]:
        """Lấy patient theo email"""
        db_patient = self.db.query(Patient).filter(and_(Patient.email == email, Patient.deleted_at.is_(None))).first()
        if not db_patient:
            return None
        return db_patient





