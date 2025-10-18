from sqlalchemy.orm import Session
from app.service_indications.models import ServiceIndication, ServiceIndicationDetail
from app.service_indications.schemas import ServiceIndicationCreate, ServiceIndicationUpdate, ServiceIndicationResponse, ServiceIndicationDetailCreate, ServiceIndicationDetailUpdate, ServiceIndicationDetailResponse, ServiceIndicationFullResponse
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException
from app.services.services import ServiceService

class ServiceIndicationService:
    def __init__(self, db: Session):
        self.db = db
        self.service_service = ServiceService(db)
    
    def create_service_indication(self, service_indication_in: ServiceIndicationCreate) -> ServiceIndication:
        """Tạo một ServiceIndication mới  với transaction built-in"""
        try: 
            db_service_indication = ServiceIndication(**service_indication_in.model_dump(exclude={'service_indication_details'}))
            self.db.add(db_service_indication)
            self.db.flush()
            self.db.refresh(db_service_indication)

            if service_indication_in.service_indication_details:
                for detail_in in service_indication_in.service_indication_details:
                    service = self.service_service.get_service_by_id(detail_in.service_id)
                    if not service:
                        # Sẽ trigger rollback tự động khi exception
                        raise HTTPException(status_code=404, detail=f"Service with id {detail_in.service_id} not found")
                    detail_create = ServiceIndicationDetailCreate(
                        service_indication_id=db_service_indication.id,
                        service_id=detail_in.service_id,
                        name=service.name,
                        quantity=detail_in.quantity
                    )
                    # self.create_service_indication_detail(detail_create)
                    db_service_indication_detail = ServiceIndicationDetail(**detail_create.model_dump())
                    self.db.add(db_service_indication_detail)
                    self.db.flush()
                    
            self.db.commit() # Commit tất cả
            return self.get_service_indication_by_id(db_service_indication.id)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=400, detail=f"Failed to create service indication: {str(e)}")
    
    # Lấy ServiceIndication theo ID
    def get_service_indication_by_id(self, service_indication_id: UUID) -> Optional[ServiceIndication]:
        """Lấy ServiceIndication theo ID"""
        service_indication = self.db.query(ServiceIndication).filter(ServiceIndication.id == service_indication_id).first()
        service_indication_details = self.get_service_indication_details(service_indication_id=service_indication.id)
        full_service_indication = ServiceIndicationFullResponse(
            id = service_indication.id,
            medical_record_id = service_indication.medical_record_id,
            notes = service_indication.notes,
            created_at = service_indication.created_at,
            services = service_indication_details,
        )
        return full_service_indication
    
    # Lấy ServiceIndication theo medical record ID
    def get_service_indication_by_medical_record_id(self, medical_record_id: UUID) -> Optional[ServiceIndication]:
        """Lấy ServiceIndication theo ID"""
        service_indication = self.db.query(ServiceIndication).filter(ServiceIndication.medical_record_id == medical_record_id).first()
        if not service_indication:
            return None
        service_indication_details = self.get_service_indication_details(service_indication_id=service_indication.id)
        full_service_indication = ServiceIndicationFullResponse(
            id = service_indication.id,
            medical_record_id = service_indication.medical_record_id,
            notes = service_indication.notes,
            created_at = service_indication.created_at,
            services = service_indication_details,
        )
        return full_service_indication
    
    # Lấy danh sách ServiceIndication với phân trang
    def get_service_indications(self, skip: int = 0, limit: int = 10) -> List[ServiceIndication]:
        """Lấy danh sách ServiceIndication với phân trang"""
        return self.db.query(ServiceIndication).offset(skip).limit(limit).all()
    
    # Đếm tổng số ServiceIndication
    def count_service_indications(self) -> int:
        """Đếm tổng số ServiceIndication"""
        return self.db.query(ServiceIndication).count()
    
    # Cập nhật ServiceIndication
    # def update_service_indication(self, service_indication_id: UUID, service_indication_in: ServiceIndicationUpdate) -> Optional[ServiceIndication]:
    #     """Cập nhật ServiceIndication"""
    #     db_service_indication = self.get_service_indication_by_id(service_indication_id)
    #     if not db_service_indication:
    #         return None
    #     update_data = service_indication_in.model_dump(exclude_unset=True)
    #     for field, value in update_data.items():
    #         setattr(db_service_indication, field, value)
    #     self.db.commit()
    #     self.db.refresh(db_service_indication)
    #     return db_service_indication

    
    # Tạo ServiceIndicationDetail mới
    def create_service_indication_detail(self, service_indication_detail_in: ServiceIndicationDetailCreate) -> ServiceIndicationDetail:
        """Tạo một ServiceIndicationDetail mới"""
        db_service_indication_detail = ServiceIndicationDetail(**service_indication_detail_in.model_dump())
        self.db.add(db_service_indication_detail)
        self.db.commit()
        self.db.refresh(db_service_indication_detail)
        return db_service_indication_detail
    

    # # Lấy ServiceIndicationDetail theo ID
    # def get_service_indication_detail_by_id(self, service_indication_detail_id: UUID) -> Optional[ServiceIndicationDetail]:
    #     """Lấy ServiceIndicationDetail theo ID"""
    #     return self.db.query(ServiceIndicationDetail).filter(ServiceIndicationDetail.id == service_indication_detail_id).first()


    # # Lấy danh sách ServiceIndicationDetail
    def get_service_indication_details(self, skip: int = 0, limit: int = 100, service_indication_id: Optional[UUID] = None) -> List[ServiceIndicationDetail]:
        """Lấy danh sách ServiceIndicationDetail với phân trang, optional[theo đơn thuốc]"""
        query = self.db.query(ServiceIndicationDetail)

        if(service_indication_id):
            query = query.filter(ServiceIndicationDetail.service_indication_id == service_indication_id)
        
        service_indication_details = query.offset(skip).limit(limit).all()
        return service_indication_details