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
from app.medications.schemas import MedicationCreate, MedicationUpdate, MedicationResponse
from app.medications.services import MedicationService

router = APIRouter(
    prefix="/medications",
    tags=["medications"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=ResponseBase[MedicationResponse], status_code=status.HTTP_201_CREATED)
@protected_route([RoleEnum.ADMIN])
def create_medication(
    CREDENTIALS: AuthCredentialDepend,
    medication: MedicationCreate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo thuốc mới
    - Chỉ ADMIN mới có quyền tạo thuốc
    - Trả về thông tin thuốc vừa tạo
    """
    repo = MedicationService(DB)
    db_medication = repo.create_medication(medication)
    return ResponseBase(message="Thuốc được tạo thành công", data=db_medication)

@router.get("/{medication_id}", response_model=ResponseBase[MedicationResponse])
def read_medication(
    CREDENTIALS: AuthCredentialDepend,
    medication_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin thuốc theo ID
    - Bất kỳ ai cũng có thể xem thông tin thuốc
    """
    repo = MedicationService(DB)
    db_medication = repo.get_medication_by_id(medication_id)
    if db_medication is None:
        raise HTTPException(status_code=404, detail="Thuốc không tồn tại")
    return ResponseBase(message="Lấy thông tin thuốc thành công", data=db_medication)

@router.get("/", response_model=PaginatedResponse[MedicationResponse])
def read_medications(
    CREDENTIALS: AuthCredentialDepend,
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi lấy về"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách thuốc với phân trang
    - Bất kỳ ai cũng có thể xem danh sách thuốc
    - Trả về danh sách thuốc cùng với thông tin phân trang
    """
    repo = MedicationService(DB)
    total = repo.count_medications()
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    medications = repo.get_medications(skip=skip, limit=limit)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách thuốc thành công", data=medications, meta=meta)

@router.put("/{medication_id}", response_model=ResponseBase[MedicationResponse])
@protected_route([RoleEnum.ADMIN])
def update_medication(
    CREDENTIALS: AuthCredentialDepend,
    medication_id: UUID,
    medication: MedicationUpdate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Cập nhật thông tin thuốc
    - Chỉ ADMIN mới có quyền cập nhật thuốc
    - Trả về thông tin thuốc sau khi cập nhật
    """
    repo = MedicationService(DB)
    db_medication = repo.update_medication(medication_id, medication)
    if db_medication is None:
        raise HTTPException(status_code=404, detail="Thuốc không tồn tại")
    return ResponseBase(message="Cập nhật thông tin thuốc thành công", data=db_medication)

@router.delete("/{medication_id}", status_code=status.HTTP_204_NO_CONTENT)
@protected_route([RoleEnum.ADMIN])
def delete_medication(
    CREDENTIALS: AuthCredentialDepend,
    medication_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Xoá thuốc (soft delete)
    - Chỉ ADMIN mới có quyền xoá thuốc
    - Trả về 204 No Content nếu xoá thành công
    """
    repo = MedicationService(DB)
    success = repo.delete_medication(medication_id)
    if not success:
        raise HTTPException(status_code=404, detail="Thuốc không tồn tại")
    return ResponseBase(message="Xoá thuốc thành công", data=None)