from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.patients.models import Patient
from app.patients.schemas import PatientCreate, PatientUpdate

class PatientService:
    """Service class để xử lý logic liên quan đến Patient"""
    def __init__(self, db: Session):
        self.db = db  # Inject DB session

    def create_patient(self, patient_in: PatientCreate) -> Patient:
        """Tạo bệnh nhân mới"""
        db_patient = Patient(**patient_in.dict())
        
        # Thêm vào database
        self.db.add(db_patient)
        self.db.commit()           # Commit transaction
        self.db.refresh(db_patient)   # Refresh để lấy ID và timestamp
        return db_patient

    # @staticmethod
    def get_patient_by_id(self, patient_id: UUID) -> Optional[Patient]:
        """Lấy thông tin bệnh nhân theo ID"""
        db_patient = self.db.query(Patient).filter(and_(Patient.id == patient_id, Patient.deleted_at.is_(None))).first()
        if not db_patient:
            return None
        return db_patient

    def get_patients(self, skip: int = 0, limit: int = 10) -> list[Patient]:
        """Lấy danh sách patients với phân trang"""
        patients = self.db.query(Patient).filter(
            Patient.deleted_at.is_(None)  # Chỉ lấy bệnh nhân chưa bị xóa
        ).offset(skip).limit(limit).all()
        return patients
    
    def search_patients(self, search_term: str) -> List[Patient]:
        """Tìm kiếm bệnh nhân theo tên hoặc số điện thoại"""
        searched_patients = self.db.query(Patient).filter(
            and_(
                Patient.deleted_at.is_(None),
                or_(
                    Patient.full_name.ilike(f"%{search_term}%"),
                    Patient.phone_number.ilike(f"%{search_term}%")
                )
            )
        ).all()
        return searched_patients
    
    def update_patient(self, patient_id: UUID, patient_update: PatientUpdate) -> Optional[Patient]:
        """Cập nhật thông tin bệnh nhân"""
        db_patient = self.get_patient_by_id(patient_id)
        
        # Cập nhật các trường
        update_data = patient_update.dict(exclude_unset=True)  # Chỉ lấy các trường được set
        for field, value in update_data.items():
            setattr(db_patient, field, value)
        
        self.db.commit()
        self.db.refresh(db_patient)
        return db_patient

    def delete_patient(self, patient_id: UUID) -> bool:
        """ Xóa mềm bệnh nhân (set deleted_at)"""
        db_patient = self.get_patient_by_id(patient_id)
        if not db_patient:
            return False

        db_patient.deleted_at = datetime.utcnow()
        self.db.commit()
        return True





