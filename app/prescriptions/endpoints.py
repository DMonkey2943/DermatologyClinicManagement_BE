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
from app.prescriptions.schemas import PrescriptionCreate, PrescriptionDetailCreate, PrescriptionResponse, PrescriptionDetailResponse, PrescriptionFullResponse
from app.prescriptions.services import PrescriptionService

router = APIRouter(
    prefix="/prescriptions",
    tags=["prescriptions"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=ResponseBase[PrescriptionFullResponse], status_code=status.HTTP_201_CREATED)
@protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
def create_prescription(
    CREDENTIALS: AuthCredentialDepend,
    record: PrescriptionCreate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo đơn thuốc mới
    - Chỉ ADMIN và DOCTOR mới có quyền tạo đơn thuốc
    - Trả về thông tin đơn thuốc vừa tạo
    """
    repo = PrescriptionService(DB)
    db_record = repo.create_prescription(record)
    return ResponseBase(message="Đơn thuốc được tạo thành công", data=db_record)

# @router.post("/detail", response_model=ResponseBase[PrescriptionDetailResponse], status_code=status.HTTP_201_CREATED)
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def create_prescription_detail(
#     CREDENTIALS: AuthCredentialDepend,
#     record: PrescriptionDetailCreate,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Tạo chi tiết đơn thuốc mới
#     - Chỉ ADMIN và DOCTOR mới có quyền tạo chi tiết đơn thuốc
#     - Trả về thông tin chi tiết đơn thuốc vừa tạo
#     """
#     repo = PrescriptionService(DB)
#     db_record = repo.create_prescription_detail(record)
#     return ResponseBase(message="chi tiết Đơn thuốc được tạo thành công", data=db_record)

@router.get("/{prescription_id}", response_model=ResponseBase[PrescriptionFullResponse])
def read_prescription(
    CREDENTIALS: AuthCredentialDepend,
    prescription_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin đơn thuốc theo ID
    - Bất kỳ ai cũng có thể xem thông tin đơn thuốc
    """
    repo = PrescriptionService(DB)
    db_record = repo.get_prescription_by_id(prescription_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Đơn thuốc không tồn tại")
    return ResponseBase(message="Lấy thông tin Đơn thuốc thành công", data=db_record)

@router.get("/", response_model=PaginatedResponse[PrescriptionResponse])
def read_prescriptions(
    CREDENTIALS: AuthCredentialDepend,
    # patient_id: Optional[UUID] = Query(None, description="ID bệnh nhân để lọc"),
    # doctor_id: Optional[UUID] = Query(None, description="ID bác sĩ (user_id) để lọc"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi lấy về"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách đơn thuốc với phân trang
    - Bất kỳ ai cũng có thể xem danh sách đơn thuốc
    """
    repo = PrescriptionService(DB)
    total = repo.count_prescriptions()    
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    records = repo.get_prescriptions(skip=skip, limit=limit)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách đơn thuốc thành công", data=records, meta=meta)

# @router.put("/{record_id}", response_model=ResponseBase[PrescriptionResponse])
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def update_medical_record(
#     CREDENTIALS: AuthCredentialDepend,
#     record_id: UUID,
#     record: MedicalRecordUpdate,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Cập nhật thông tin đơn thuốc
#     - Chỉ ADMIN và DOCTOR mới có quyền cập nhật đơn thuốc
#     - Trả về thông tin đơn thuốc vừa cập nhật
#     """
#     repo = PrescriptionService(DB)
#     db_record = repo.update_medical_record(record_id, record)
#     if db_record is None:
#         raise HTTPException(status_code=404, detail="đơn thuốc không tồn tại")
#     return ResponseBase(message="Cập nhật đơn thuốc thành công", data=db_record)

# @router.delete("/{record_id}", response_model=ResponseBase[None])
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def delete_medical_record(
#     CREDENTIALS: AuthCredentialDepend,
#     record_id: UUID,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Xóa đơn thuốc
#     - Chỉ ADMIN và DOCTOR mới có quyền xóa đơn thuốc
#     - Trả về thông báo xóa thành công
#     """
#     repo = PrescriptionService(DB)
#     success = repo.delete_medical_record(record_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="đơn thuốc không tồn tại")
#     return ResponseBase(message="Xóa đơn thuốc thành công", data=None)