from sqlalchemy.orm import Session
from app.services.models import Service
from app.services.schemas import ServiceCreate, ServiceUpdate, ServiceResponse
from uuid import UUID
from typing import List, Optional
from datetime import datetime

class ServiceService:
    def __init__(self, db: Session):
        self.db = db

    def create_service(self, service_in: ServiceCreate) -> Service:
        """Tạo một Service mới"""
        db_service = Service(**service_in.model_dump())
        self.db.add(db_service)
        self.db.commit()
        self.db.refresh(db_service)
        return db_service
    
    def get_service_by_id(self, service_id: UUID) -> Optional[Service]:
        """Lấy Service theo ID"""
        return self.db.query(Service).filter(Service.id == service_id).first()
    
    def get_services(self, skip: int = 0, limit: int = 10) -> List[Service]:
        """Lấy danh sách Service với phân trang"""
        return self.db.query(Service).filter(
            Service.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()
    
    def count_services(self) -> int:
        """Đếm tổng số Service"""
        return self.db.query(Service).filter(Service.deleted_at.is_(None)).count()
    
    def update_service(self, service_id: UUID, service_in: ServiceUpdate) -> Optional[Service]:
        db_service = self.get_service_by_id(service_id)
        if not db_service:
            return None

        update_data = service_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_service, field, value)

        self.db.commit()
        self.db.refresh(db_service)
        return db_service
    
    def delete_service(self, service_id: UUID) -> bool:
        db_service = self.get_service_by_id(service_id)
        if not db_service:
            return False
        db_service.deleted_at = datetime.utcnow()
        self.db.commit()
        return True

