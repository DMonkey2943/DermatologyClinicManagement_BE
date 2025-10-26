from sqlalchemy.orm import Session
# from app.invoices.models import Prescription, PrescriptionDetail
# from app.invoices.schemas import PrescriptionCreate, PrescriptionUpdate, PrescriptionResponse, PrescriptionDetailCreate, PrescriptionDetailUpdate, PrescriptionDetailResponse, PrescriptionFullResponse
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from app.appointments.services import AppointmentService
from app.invoices.models import Invoice
from app.invoices.schemas import InvoiceCreate, InvoiceFullResponse
from app.patients.services import PatientService
from app.prescriptions.services import PrescriptionService
from app.service_indications.services import ServiceIndicationService
from app.users.services import UserService
from app.medications.services import MedicationService
from app.medical_records.services import MedicalRecordService

class InvoiceService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.patient_service = PatientService(db)
        self.prescription_service = PrescriptionService(db)
        self.service_indication_service = ServiceIndicationService(db)
        self.medication_service = MedicationService(db)
        self.medical_record_service = MedicalRecordService(db)
        self.appointment_service = AppointmentService(db)
    
    def create_invoice(self, invoice_in: InvoiceCreate) -> Invoice:
        """Tạo một Invoice mới và cập nhật medical_record thành PAID và trừ stock medications.
        Toàn bộ thao tác nằm trong một transaction: nếu có lỗi sẽ rollback.
        """
        try:
            db_invoice = Invoice(**invoice_in.model_dump())
            self.db.add(db_invoice)
            self.db.flush()  # ensure db_invoice.id available if needed

            # Lấy prescription liên quan tới medical_record để trừ stock
            prescription = self.prescription_service.get_prescription_by_medical_record_id(invoice_in.medical_record_id)
            if prescription and getattr(prescription, "medications", None):
                for detail in prescription.medications:
                    med = self.medication_service.get_medication_by_id(detail.medication_id)
                    if not med:
                        # sẽ trigger rollback
                        raise HTTPException(status_code=404, detail=f"Thuốc với id {detail.medication_id} không tìm thấy")
                    # Kiểm tra trường stock_quantity tồn tại và đủ
                    if getattr(med, "stock_quantity", None) is None:
                        raise HTTPException(status_code=400, detail=f"Medication stock information unavailable for {med.id}")
                    if med.stock_quantity < detail.quantity:
                        raise HTTPException(status_code=400, detail=f"Số lượng tồn kho của thuốc này không đủ {med.id}")
                    med.stock_quantity = med.stock_quantity - detail.quantity
                    self.db.add(med)

            # Cập nhật medical_record status = "PAID"
            medical_record = self.medical_record_service.get_medical_record_by_id(invoice_in.medical_record_id)
            if not medical_record:
                raise HTTPException(status_code=404, detail="Phiên khám không tồn tại")
            medical_record.status = "PAID"
            self.db.add(medical_record)

            # Cập nhật appointment status = "COMPLETED"
            appointment = self.appointment_service.get_appointment_by_id(medical_record.appointment_id)
            if not appointment:
                raise HTTPException(status_code=404, detail="Lịch hẹn khám không tồn tại")
            appointment.status = "COMPLETED"
            self.db.add(appointment)

            # Commit tất cả thay đổi cùng lúc
            self.db.commit()
            self.db.refresh(db_invoice)
            return self.get_invoice_by_id(db_invoice.id)
        except HTTPException:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Lỗi tạo hóa đơn: {str(e)}")
    
    # Lấy Invoice theo ID
    def get_invoice_by_id(self, invoice_id: UUID) -> Optional[Invoice]:
        """Lấy Invoice theo ID"""
        invoice = self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
        patient = self.patient_service.get_patient_by_id(invoice.patient_id)
        doctor = self.user_service.get_user_by_id(invoice.doctor_id)
        created_by = self.user_service.get_user_by_id(invoice.created_by)
        prescription = self.prescription_service.get_prescription_by_medical_record_id(invoice.medical_record_id)
        service_indication = self.service_indication_service.get_service_indication_by_medical_record_id(invoice.medical_record_id)
        full_invoice = InvoiceFullResponse(
            id = invoice.id,
            medical_record_id = invoice.medical_record_id,
            patient_id = invoice.patient_id,
            doctor_id = invoice.doctor_id,
            created_by = invoice.created_by,
            service_subtotal = invoice.service_subtotal,
            medication_subtotal = invoice.medication_subtotal,
            total_amount = invoice.total_amount,
            discount_amount = invoice.discount_amount,
            final_amount = invoice.final_amount,
            notes = invoice.notes,
            created_at = invoice.created_at,
            patient=patient,
            doctor=doctor,
            created_by_user=created_by,
            medications = prescription.medications,
            services = service_indication.services,
        )
        return full_invoice
    
    # Lấy Invoice theo medical record ID
    def get_invoice_by_medical_record_id(self, medical_record_id: UUID) -> Optional[Invoice]:
        """Lấy Invoice theo ID"""
        invoice = self.db.query(Invoice).filter(Invoice.medical_record_id == medical_record_id).first()
        if not invoice:
            return None
        patient = self.patient_service.get_patient_by_id(invoice.patient_id)
        doctor = self.user_service.get_user_by_id(invoice.doctor_id)
        created_by = self.user_service.get_user_by_id(invoice.created_by)
        prescription = self.prescription_service.get_prescription_by_medical_record_id(invoice.medical_record_id)
        service_indication = self.service_indication_service.get_service_indication_by_medical_record_id(invoice.medical_record_id)
        full_invoice = InvoiceFullResponse(
            id = invoice.id,
            medical_record_id = invoice.medical_record_id,
            patient_id = invoice.patient_id,
            doctor_id = invoice.doctor_id,
            created_by = invoice.created_by,
            service_subtotal = invoice.service_subtotal,
            medication_subtotal = invoice.medication_subtotal,
            total_amount = invoice.total_amount,
            discount_amount = invoice.discount_amount,
            final_amount = invoice.final_amount,
            notes = invoice.notes,
            created_at = invoice.created_at,
            patient=patient,
            doctor=doctor,
            created_by_user=created_by,
            medications = prescription.medications,
            services = service_indication.services,
        )
        return full_invoice
    
    # Lấy danh sách Invoice với phân trang
    def get_invoices(self, skip: int = 0, limit: int = 10) -> List[Invoice]:
        """Lấy danh sách Invoice với phân trang"""
        return self.db.query(Invoice).offset(skip).limit(limit).all()
    
    # Đếm tổng số Invoice
    def count_invoices(self) -> int:
        """Đếm tổng số Invoice"""
        return self.db.query(Invoice).count()
    
    # Cập nhật Prescription
    # def update_invoice(self, invoice_id: UUID, invoice_in: PrescriptionUpdate) -> Optional[Prescription]:
    #     """Cập nhật Prescription"""
    #     db_invoice = self.get_invoice_by_id(invoice_id)
    #     if not db_invoice:
    #         return None
    #     update_data = invoice_in.model_dump(exclude_unset=True)
    #     for field, value in update_data.items():
    #         setattr(db_invoice, field, value)
    #     self.db.commit()
    #     self.db.refresh(db_invoice)
    #     return db_invoice