from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.medical_records.models import MedicalRecord, SkinImage
from app.medical_records.schemas import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse, SkinImageCreate, SkinImageResponse
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, UploadFile, status
from app.users.services import UserService
from app.patients.services import PatientService
from app.utils.skin_image_handler import skin_image_handler

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
    
    def get_medical_record_by_appointment_id(self, appointment_id: UUID) -> Optional[MedicalRecord]:
        """Lấy MedicalRecord theo ID"""
        return self.db.query(MedicalRecord).filter(MedicalRecord.appointment_id == appointment_id).first()
    
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
        
        # ✅ Thêm sắp xếp theo created_at giảm dần
        query = query.order_by(MedicalRecord.created_at.desc())
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
    
    def get_medical_records_by_patient(self, patient_id: UUID, skip: int = 0, limit: int = 5) -> List[MedicalRecord]:
        """Lấy danh sách MedicalRecord theo patient_id với phân trang"""
        return self.db.query(MedicalRecord).filter(and_(
            MedicalRecord.patient_id == patient_id,
            MedicalRecord.status == 'PAID'
        )).order_by(MedicalRecord.created_at.desc()).offset(skip).limit(limit).all()
    
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
    
    def count_medical_records_by_patient(
        self,
        patient_id: Optional[UUID] = None,
    ) -> int:        
        """Đếm tổng số lịch hẹn của bệnh nhân"""
        query = self.db.query(MedicalRecord).filter(and_(
            MedicalRecord.patient_id == patient_id,
            MedicalRecord.status == 'PAID'
        ))
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

    async def upload_skin_image(self, data_in: SkinImageCreate, skin_image: UploadFile) -> SkinImage:
        """
        Upload ảnh da bệnh nhân cho phiên khám
        
        Args:
            data_in: Dữ liệu tạo SkinImage (medical_record_id, image_type)
            skin_image: File ảnh upload
            
        Returns:
            Đối tượng SkinImage đã lưu
            
        Raises:
            HTTPException: Nếu có lỗi trong quá trình xử lý
        """
        # Kiểm tra xem ảnh đã tồn tại với medical_record_id và image_type
        existing_image = self.db.query(SkinImage).filter(
            SkinImage.medical_record_id == data_in.medical_record_id,
            SkinImage.image_type == data_in.image_type
        ).first()
        
        # Lưu ảnh mới và lấy đường dẫn
        new_image_path = await skin_image_handler.save_upload_file(
            file=skin_image,
            medical_record_id=str(data_in.medical_record_id),
            image_type=data_in.image_type
        )
        
        try:
            if existing_image:
                # Cập nhật đường dẫn ảnh mới trước
                old_image_path = existing_image.image_path  # Lưu đường dẫn ảnh cũ
                existing_image.image_path = new_image_path
                self.db.commit()
                self.db.refresh(existing_image)
                
                # Xóa ảnh cũ sau khi commit thành công
                if old_image_path:
                    await skin_image_handler.delete_file(old_image_path)
                
                return existing_image
            else:
                # Tạo bản ghi mới
                new_skin_image = SkinImage(
                    medical_record_id=data_in.medical_record_id,
                    image_type=data_in.image_type,
                    image_path=new_image_path
                )
                self.db.add(new_skin_image)
                self.db.commit()
                self.db.refresh(new_skin_image)
                return new_skin_image
        except Exception as e:
            # Nếu có lỗi, xóa ảnh mới vừa upload và rollback
            await skin_image_handler.delete_file(new_image_path)
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi lưu ảnh vào database: {str(e)}"
            )
    

    def get_skin_images(self, medical_record_id: UUID) -> List[SkinImageResponse]:
        """
        Lấy danh sách ảnh da của phiên khám
        
        Args:
            medical_record_id: ID của phiên khám
            
        Returns:
            Danh sách SkinImageResponse
            
        Raises:
            HTTPException: Nếu không tìm thấy phiên khám
        """
        images = self.db.query(SkinImage).filter(
            SkinImage.medical_record_id == medical_record_id
        ).all()
        
        if not images:
            return []
        
        return [SkinImageResponse.model_validate(image) for image in images]

    async def delete_skin_image(self, image_id: UUID) -> None:
        """
        Xóa ảnh da bệnh nhân
        
        Args:
            image_id: ID của ảnh cần xóa
            
        Raises:
            HTTPException: Nếu không tìm thấy ảnh
        """
        image = self.db.query(SkinImage).filter(SkinImage.id == image_id).first()
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy ảnh"
            )
        
        try:
            # Xóa file ảnh trên server
            await skin_image_handler.delete_file(image.image_path)
            # Xóa bản ghi trong database
            self.db.delete(image)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi xóa ảnh: {str(e)}"
            )