from sqlalchemy.orm import Session
from app.medical_records.models import MedicalRecord
from app.medical_records.schemas import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
from uuid import UUID
from typing import List, Optional
from datetime import datetime

class MedicalRecordService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_medical_record(self, record_in: MedicalRecordCreate) -> MedicalRecord:
        """Tạo một MedicalRecord mới"""
        db_record = MedicalRecord(**record_in.model_dump())
        self.db.add(db_record)
        self.db.commit()
        self.db.refresh(db_record)
        return db_record

    def get_medical_record_by_id(self, record_id: UUID) -> Optional[MedicalRecord]:
        """Lấy MedicalRecord theo ID"""
        return self.db.query(MedicalRecord).filter(MedicalRecord.id == record_id).first()
    
    def get_medical_records(self, skip: int = 0, limit: int = 10) -> List[MedicalRecord]:
        """Lấy danh sách MedicalRecord với phân trang"""
        return self.db.query(MedicalRecord).offset(skip).limit(limit).all()
    
    def get_medical_records_by_patient(self, patient_id: UUID, skip: int = 0, limit: int = 10) -> List[MedicalRecord]:
        """Lấy danh sách MedicalRecord theo patient_id với phân trang"""
        return self.db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id
        ).offset(skip).limit(limit).all()
    
    def count_medical_records(self) -> int:
        """Đếm tổng số MedicalRecord"""
        return self.db.query(MedicalRecord).count()
    
    def update_medical_record(self, record_id: UUID, record_in: MedicalRecordUpdate) -> Optional[MedicalRecord]:
        db_record = self.get_medical_record_by_id(record_id)
        if not db_record:
            return None

        update_data = record_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_record, field, value)

        self.db.commit()
        self.db.refresh(db_record)
        return db_record
    
    def delete_medical_record(self, record_id: UUID) -> bool:
        db_record = self.get_medical_record_by_id(record_id)
        if not db_record:
            return False
        self.db.delete(db_record)
        self.db.commit()
        return True
