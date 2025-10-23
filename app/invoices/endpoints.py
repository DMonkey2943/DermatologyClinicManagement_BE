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
from app.invoices.schemas import InvoiceCreate, InvoiceResponse, InvoiceFullResponse
from app.invoices.services import InvoiceService

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=ResponseBase[InvoiceResponse], status_code=status.HTTP_201_CREATED)
def create_invoice(
    CREDENTIALS: AuthCredentialDepend,
    record: InvoiceCreate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo hóa đơn mới
    - Trả về thông tin hóa đơn vừa tạo
    """
    repo = InvoiceService(DB)
    db_record = repo.create_invoice(record)
    return ResponseBase(message="Hóa đơn được tạo thành công", data=db_record)

# @router.post("/detail", response_model=ResponseBase[InvoiceDetailResponse], status_code=status.HTTP_201_CREATED)
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def create_invoice_detail(
#     CREDENTIALS: AuthCredentialDepend,
#     record: InvoiceDetailCreate,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Tạo chi tiết hóa đơn mới
#     - Chỉ ADMIN và DOCTOR mới có quyền tạo chi tiết hóa đơn
#     - Trả về thông tin chi tiết hóa đơn vừa tạo
#     """
#     repo = InvoiceService(DB)
#     db_record = repo.create_invoice_detail(record)
#     return ResponseBase(message="chi tiết Hóa đơn được tạo thành công", data=db_record)

@router.get("/{invoice_id}", response_model=ResponseBase[InvoiceFullResponse])
def read_invoice(
    CREDENTIALS: AuthCredentialDepend,
    invoice_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin hóa đơn theo ID
    - Bất kỳ ai cũng có thể xem thông tin hóa đơn
    """
    repo = InvoiceService(DB)
    db_record = repo.get_invoice_by_id(invoice_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Hóa đơn không tồn tại")
    return ResponseBase(message="Lấy thông tin Hóa đơn thành công", data=db_record)

@router.get("/", response_model=PaginatedResponse[InvoiceResponse])
def read_invoices(
    CREDENTIALS: AuthCredentialDepend,
    # patient_id: Optional[UUID] = Query(None, description="ID bệnh nhân để lọc"),
    # doctor_id: Optional[UUID] = Query(None, description="ID bác sĩ (user_id) để lọc"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi lấy về"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách hóa đơn với phân trang
    - Bất kỳ ai cũng có thể xem danh sách hóa đơn
    """
    repo = InvoiceService(DB)
    total = repo.count_invoices()    
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    records = repo.get_invoices(skip=skip, limit=limit)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách hóa đơn thành công", data=records, meta=meta)

# @router.put("/{record_id}", response_model=ResponseBase[InvoiceResponse])
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def update_medical_record(
#     CREDENTIALS: AuthCredentialDepend,
#     record_id: UUID,
#     record: MedicalRecordUpdate,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Cập nhật thông tin hóa đơn
#     - Chỉ ADMIN và DOCTOR mới có quyền cập nhật hóa đơn
#     - Trả về thông tin hóa đơn vừa cập nhật
#     """
#     repo = InvoiceService(DB)
#     db_record = repo.update_medical_record(record_id, record)
#     if db_record is None:
#         raise HTTPException(status_code=404, detail="hóa đơn không tồn tại")
#     return ResponseBase(message="Cập nhật hóa đơn thành công", data=db_record)

# @router.delete("/{record_id}", response_model=ResponseBase[None])
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def delete_medical_record(
#     CREDENTIALS: AuthCredentialDepend,
#     record_id: UUID,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Xóa hóa đơn
#     - Chỉ ADMIN và DOCTOR mới có quyền xóa hóa đơn
#     - Trả về thông báo xóa thành công
#     """
#     repo = InvoiceService(DB)
#     success = repo.delete_medical_record(record_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="hóa đơn không tồn tại")
#     return ResponseBase(message="Xóa hóa đơn thành công", data=None)