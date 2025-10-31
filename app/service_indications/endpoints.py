from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.core.dependencies import AuthCredentialDepend
from app.database import get_db
from app.core.authentication import protected_route
from app.users.models import UserRoleEnum as RoleEnum
from app.core.response import PaginationMeta, ResponseBase, PaginatedResponse
from app.service_indications.schemas import ServiceIndicationCreate, ServiceIndicationDetailCreate, ServiceIndicationResponse, ServiceIndicationDetailResponse, ServiceIndicationFullResponse, ServiceIndicationUpdate
from app.service_indications.services import ServiceIndicationService

router = APIRouter(
    prefix="/service-indications",
    tags=["service-indications"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=ResponseBase[ServiceIndicationFullResponse], status_code=status.HTTP_201_CREATED)
@protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
def create_service_indication(
    CREDENTIALS: AuthCredentialDepend,
    record: ServiceIndicationCreate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo phiếu chỉ định dịch vụ mới
    - Chỉ ADMIN và DOCTOR mới có quyền tạo phiếu chỉ định dịch vụ
    - Trả về thông tin phiếu chỉ định dịch vụ vừa tạo
    """
    repo = ServiceIndicationService(DB)
    db_record = repo.create_service_indication(record)
    return ResponseBase(message="Phiếu chỉ định dịch vụ được tạo thành công", data=db_record)

# @router.post("/detail", response_model=ResponseBase[ServiceIndicationDetailResponse], status_code=status.HTTP_201_CREATED)
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def create_service_indication_detail(
#     CREDENTIALS: AuthCredentialDepend,
#     record: ServiceIndicationDetailCreate,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Tạo chi tiết phiếu chỉ định dịch vụ mới
#     - Chỉ ADMIN và DOCTOR mới có quyền tạo chi tiết phiếu chỉ định dịch vụ
#     - Trả về thông tin chi tiết phiếu chỉ định dịch vụ vừa tạo
#     """
#     repo = ServiceIndicationService(DB)
#     db_record = repo.create_service_indication_detail(record)
#     return ResponseBase(message="chi tiết Phiếu chỉ định dịch vụ được tạo thành công", data=db_record)

@router.get("/{service_indication_id}", response_model=ResponseBase[ServiceIndicationFullResponse])
def read_service_indication(
    CREDENTIALS: AuthCredentialDepend,
    service_indication_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin phiếu chỉ định dịch vụ theo ID
    - Bất kỳ ai cũng có thể xem thông tin phiếu chỉ định dịch vụ
    """
    repo = ServiceIndicationService(DB)
    db_record = repo.get_service_indication_by_id(service_indication_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Phiếu chỉ định dịch vụ không tồn tại")
    return ResponseBase(message="Lấy thông tin Phiếu chỉ định dịch vụ thành công", data=db_record)

@router.get("/", response_model=PaginatedResponse[ServiceIndicationResponse])
def read_service_indications(
    CREDENTIALS: AuthCredentialDepend,
    # patient_id: Optional[UUID] = Query(None, description="ID bệnh nhân để lọc"),
    # doctor_id: Optional[UUID] = Query(None, description="ID bác sĩ (user_id) để lọc"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi lấy về"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách phiếu chỉ định dịch vụ với phân trang
    - Bất kỳ ai cũng có thể xem danh sách phiếu chỉ định dịch vụ
    """
    repo = ServiceIndicationService(DB)
    total = repo.count_service_indications()    
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    records = repo.get_service_indications(skip=skip, limit=limit)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách phiếu chỉ định dịch vụ thành công", data=records, meta=meta)

@router.put("/{record_id}", response_model=ResponseBase[ServiceIndicationFullResponse])
@protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
def update_service_indication(
    CREDENTIALS: AuthCredentialDepend,
    record_id: UUID,
    record: ServiceIndicationUpdate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Cập nhật phiếu chỉ định dịch vụ 
    - Chỉ ADMIN và DOCTOR mới có quyền cập nhật phiếu chỉ định dịch vụ
    - Trả về thông tin phiếu chỉ định dịch vụ vừa cập nhật
    """
    repo = ServiceIndicationService(DB)
    db_record = repo.update_service_indication(record_id, record)
    return ResponseBase(message="phiếu chỉ định dịch vụ được cập nhật thành công", data=db_record)

# @router.delete("/{record_id}", response_model=ResponseBase[None])
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def delete_medical_record(
#     CREDENTIALS: AuthCredentialDepend,
#     record_id: UUID,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Xóa phiếu chỉ định dịch vụ
#     - Chỉ ADMIN và DOCTOR mới có quyền xóa phiếu chỉ định dịch vụ
#     - Trả về thông báo xóa thành công
#     """
#     repo = ServiceIndicationService(DB)
#     success = repo.delete_medical_record(record_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="phiếu chỉ định dịch vụ không tồn tại")
#     return ResponseBase(message="Xóa phiếu chỉ định dịch vụ thành công", data=None)