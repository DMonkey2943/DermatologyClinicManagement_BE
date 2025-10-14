from sqlalchemy.orm import Session
from app.medical_records.models import MedicalRecord
from app.medical_records.schemas import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from app.users.services import UserService
from app.patients.services import PatientService

class MedicalRecordService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.patient_service = PatientService(db)
    
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
    
    def get_medical_records(
        self, 
        skip: int = 0, 
        limit: int = 10,
        patient_id: Optional[UUID] = None,
        doctor_id: Optional[UUID] = None,
    ) -> List[MedicalRecord]:
        """Lấy danh sách MedicalRecord với phân trang"""
        query = self.db.query(MedicalRecord)

        if patient_id:
            patient = self.patient_service.get_patient_by_id(patient_id)
            if not patient:
                raise HTTPException(status_code=404, detail="Bệnh nhân không tồn tại")
            query = query.filter(MedicalRecord.patient_id == patient_id)

        if doctor_id:
            doctor = self.user_service.get_user_by_id(doctor_id)
            if not doctor:
                raise HTTPException(status_code=404, detail="Bác sĩ không tồn tại")
            # if doctor.role != "DOCTOR":
            #     raise HTTPException(status_code=400, detail="User không phải là bác sĩ")
            query = query.filter(MedicalRecord.doctor_id == doctor_id)
        
        medical_records = query.offset(skip).limit(limit).all()        
        result = []
        for medical_record in medical_records:            
            patient = self.patient_service.get_patient_by_id(medical_record.patient_id)
            doctor = self.user_service.get_user_by_id(medical_record.doctor_id)
            result.append(MedicalRecordResponse(
                id=medical_record.id,
                patient_id=medical_record.patient_id,
                doctor_id=medical_record.doctor_id,
                symptoms=medical_record.symptoms,
                diagnosis=medical_record.diagnosis,
                status=medical_record.status,
                notes=medical_record.notes,
                appointment_id=medical_record.appointment_id,
                created_at=medical_record.created_at,
                patient=patient,
                doctor=doctor
            ))
        return result
    
    def get_medical_records_by_patient(self, patient_id: UUID, skip: int = 0, limit: int = 10) -> List[MedicalRecord]:
        """Lấy danh sách MedicalRecord theo patient_id với phân trang"""
        return self.db.query(MedicalRecord).filter(
            MedicalRecord.patient_id == patient_id
        ).offset(skip).limit(limit).all()
    
    def count_medical_records(
        self,
        patient_id: Optional[UUID] = None,
        doctor_id: Optional[UUID] = None,
    ) -> int:        
        """Đếm tổng số lịch hẹn với các bộ lọc"""
        query = self.db.query(MedicalRecord)
        # Lọc theo bác sĩ
        if patient_id:
            query = query.filter(MedicalRecord.patient_id == patient_id)
        # Lọc theo bác sĩ
        if doctor_id:
            query = query.filter(MedicalRecord.doctor_id == doctor_id)
        return query.count()
    
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
    
    # def delete_medical_record(self, record_id: UUID) -> bool:
    #     db_record = self.get_medical_record_by_id(record_id)
    #     if not db_record:
    #         return False
    #     self.db.delete(db_record)
    #     self.db.commit()
    #     return True
