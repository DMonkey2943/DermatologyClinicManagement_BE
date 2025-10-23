from sqlalchemy.orm import Session
from app.prescriptions.models import Prescription, PrescriptionDetail
from app.prescriptions.schemas import PrescriptionCreate, PrescriptionUpdate, PrescriptionResponse, PrescriptionDetailCreate, PrescriptionDetailUpdate, PrescriptionDetailResponse, PrescriptionFullResponse
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from app.medications.services import MedicationService
from app.patients.services import PatientService

class PrescriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.medication_service = MedicationService(db)
    
    def create_prescription(self, prescription_in: PrescriptionCreate) -> Prescription:
        """Tạo một Prescription mới với transaction built-in"""
        try:
            db_prescription = Prescription(**prescription_in.model_dump(exclude={'prescription_details'}))
            self.db.add(db_prescription)
            self.db.flush()
            self.db.refresh(db_prescription)

            if prescription_in.prescription_details:
                for detail_in in prescription_in.prescription_details:
                    medication = self.medication_service.get_medication_by_id(detail_in.medication_id)
                    if not medication:
                        # Sẽ trigger rollback tự động khi exception
                        raise HTTPException(status_code=404, detail=f"Medication with id {detail_in.medication_id} not found")
                    detail_create = PrescriptionDetailCreate(
                        prescription_id=db_prescription.id,
                        medication_id=detail_in.medication_id,
                        name=medication.name,
                        dosage_form=medication.dosage_form,
                        quantity=detail_in.quantity,
                        dosage=detail_in.dosage,
                        unit_price=medication.price,
                        total_price=medication.price*detail_in.quantity,
                    )
                    db_prescription_detail = PrescriptionDetail(**detail_create.model_dump())
                    self.db.add(db_prescription_detail)
                    self.db.flush()
            
            self.db.commit()  # Commit tất cả
            return self.get_prescription_by_id(db_prescription.id)
        except Exception as e:
            self.db.rollback()  # Rollback tự động khi có exception
            raise HTTPException(status_code=400, detail=f"Failed to create prescription: {str(e)}")

    
    # Lấy Prescription theo ID
    def get_prescription_by_id(self, prescription_id: UUID) -> Optional[Prescription]:
        """Lấy Prescription theo ID"""
        prescription = self.db.query(Prescription).filter(Prescription.id == prescription_id).first()
        prescription_details = self.get_prescription_details(prescription_id=prescription.id)
        full_prescription = PrescriptionFullResponse(
            id = prescription.id,
            medical_record_id = prescription.medical_record_id,
            notes = prescription.notes,
            created_at = prescription.created_at,
            medications = prescription_details,
        )
        return full_prescription
    
    # Lấy Prescription theo medical record ID
    def get_prescription_by_medical_record_id(self, medical_record_id: UUID) -> Optional[Prescription]:
        """Lấy Prescription theo ID"""
        prescription = self.db.query(Prescription).filter(Prescription.medical_record_id == medical_record_id).first()
        if not prescription:
            return None
        prescription_details = self.get_prescription_details(prescription_id=prescription.id)
        full_prescription = PrescriptionFullResponse(
            id = prescription.id,
            medical_record_id = prescription.medical_record_id,
            notes = prescription.notes,
            created_at = prescription.created_at,
            medications = prescription_details,
        )
        return full_prescription
    
    # Lấy danh sách Prescription với phân trang
    def get_prescriptions(self, skip: int = 0, limit: int = 10) -> List[Prescription]:
        """Lấy danh sách Prescription với phân trang"""
        return self.db.query(Prescription).offset(skip).limit(limit).all()
    
    # Đếm tổng số Prescription
    def count_prescriptions(self) -> int:
        """Đếm tổng số Prescription"""
        return self.db.query(Prescription).count()
    
    # Cập nhật Prescription
    # def update_prescription(self, prescription_id: UUID, prescription_in: PrescriptionUpdate) -> Optional[Prescription]:
    #     """Cập nhật Prescription"""
    #     db_prescription = self.get_prescription_by_id(prescription_id)
    #     if not db_prescription:
    #         return None
    #     update_data = prescription_in.model_dump(exclude_unset=True)
    #     for field, value in update_data.items():
    #         setattr(db_prescription, field, value)
    #     self.db.commit()
    #     self.db.refresh(db_prescription)
    #     return db_prescription

    
    # Tạo PrescriptionDetail mới
    def create_prescription_detail(self, prescription_detail_in: PrescriptionDetailCreate) -> PrescriptionDetail:
        """Tạo một PrescriptionDetail mới"""
        db_prescription_detail = PrescriptionDetail(**prescription_detail_in.model_dump())
        self.db.add(db_prescription_detail)
        self.db.commit()
        self.db.refresh(db_prescription_detail)
        return db_prescription_detail
    

    # Lấy PrescriptionDetail theo ID
    def get_prescription_detail_by_id(self, prescription_detail_id: UUID) -> Optional[PrescriptionDetail]:
        """Lấy PrescriptionDetail theo ID"""
        return self.db.query(PrescriptionDetail).filter(PrescriptionDetail.id == prescription_detail_id).first()


    # Lấy danh sách PrescriptionDetail
    def get_prescription_details(self, skip: int = 0, limit: int = 100, prescription_id: Optional[UUID] = None) -> List[PrescriptionDetail]:
        """Lấy danh sách PrescriptionDetail với phân trang, optional[theo đơn thuốc]"""
        query = self.db.query(PrescriptionDetail)

        if(prescription_id):
            query = query.filter(PrescriptionDetail.prescription_id == prescription_id)
        
        prescription_details = query.offset(skip).limit(limit).all()
        return prescription_details