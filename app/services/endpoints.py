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
from app.services.schemas import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services.services import ServiceService

router = APIRouter(
    prefix="/services",
    tags=["services"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=ResponseBase[ServiceResponse], status_code=status.HTTP_201_CREATED)
@protected_route([RoleEnum.ADMIN])
def create_service(
    CREDENTIALS: AuthCredentialDepend,
    service: ServiceCreate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo dịch vụ mới
    - Chỉ ADMIN mới có quyền tạo dịch vụ
    - Trả về thông tin dịch vụ vừa tạo
    """
    repo = ServiceService(DB)
    db_service = repo.create_service(service)
    return ResponseBase(message="Dịch vụ được tạo thành công", data=db_service)

@router.get("/{service_id}", response_model=ResponseBase[ServiceResponse])
def read_service(
    CREDENTIALS: AuthCredentialDepend,
    service_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin dịch vụ theo ID
    - Bất kỳ ai cũng có thể xem thông tin dịch vụ
    """
    repo = ServiceService(DB)
    db_service = repo.get_service_by_id(service_id)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    return ResponseBase(message="Lấy thông tin dịch vụ thành công", data=db_service)

@router.get("/", response_model=PaginatedResponse[ServiceResponse])
def read_services(
    CREDENTIALS: AuthCredentialDepend,
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi lấy về"),
    q: Optional[str] = Query(None, description="Từ khoá tìm kiếm theo tên dịch vụ"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách dịch vụ với phân trang
    - Bất kỳ ai cũng có thể xem danh sách dịch vụ
    - Trả về danh sách dịch vụ cùng với thông tin phân trang
    """
    repo = ServiceService(DB)
    services = repo.get_services(skip=skip, limit=limit, q=q)
    total = repo.count_services(q=q)
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách dịch vụ thành công", data=services, meta=meta)

@router.put("/{service_id}", response_model=ResponseBase[ServiceResponse])
@protected_route([RoleEnum.ADMIN])
def update_service(
    CREDENTIALS: AuthCredentialDepend,
    service_id: UUID,
    service: ServiceUpdate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Cập nhật thông tin dịch vụ
    - Chỉ ADMIN mới có quyền cập nhật dịch vụ
    - Trả về thông tin dịch vụ sau khi cập nhật
    """
    repo = ServiceService(DB)
    db_service = repo.update_service(service_id, service)
    if db_service is None:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    return ResponseBase(message="Cập nhật thông tin dịch vụ thành công", data=db_service)

@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
@protected_route([RoleEnum.ADMIN])
def delete_service(
    CREDENTIALS: AuthCredentialDepend,
    service_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Xoá dịch vụ (soft delete)
    - Chỉ ADMIN mới có quyền xoá dịch vụ
    - Trả về 204 No Content nếu xoá thành công
    """
    repo = ServiceService(DB)
    success = repo.delete_service(service_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dịch vụ không tồn tại")
    return ResponseBase(message="Xoá dịch vụ thành công", data=None)