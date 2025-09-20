from sqlalchemy.orm import Session
from app.medications.models import Medication
from app.medications.schemas import MedicationCreate, MedicationUpdate, MedicationResponse
from uuid import UUID
from typing import List, Optional
from datetime import datetime

class MedicationService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_medication(self, medication_in: MedicationCreate) -> Medication:
        """Tạo một Medication mới"""
        db_medication = Medication(**medication_in.model_dump())
        self.db.add(db_medication)
        self.db.commit()
        self.db.refresh(db_medication)
        return db_medication
    
    def get_medication_by_id(self, medication_id: UUID) -> Optional[Medication]:
        """Lấy Medication theo ID"""
        return self.db.query(Medication).filter(Medication.id == medication_id).first()
    
    def get_medications(self, skip: int = 0, limit: int = 10) -> List[Medication]:
        """Lấy danh sách Medication với phân trang"""
        return self.db.query(Medication).filter(
            Medication.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def count_medications(self) -> int:
        """Đếm tổng số Medication"""
        return self.db.query(Medication).filter(Medication.deleted_at.is_(None)).count()
    
    def update_medication(self, medication_id: UUID, medication_in: MedicationUpdate) -> Optional[Medication]:
        db_medication = self.get_medication_by_id(medication_id)
        if not db_medication:
            return None

        update_data = medication_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_medication, field, value)

        self.db.commit()
        self.db.refresh(db_medication)
        return db_medication
    
    def delete_medication(self, medication_id: UUID) -> bool:
        db_medication = self.get_medication_by_id(medication_id)
        if not db_medication:
            return False
        db_medication.deleted_at = datetime.utcnow()
        self.db.commit()
        return True

