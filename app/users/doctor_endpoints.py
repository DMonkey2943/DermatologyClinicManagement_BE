from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.dependencies import AuthCredentialDepend
from app.database import get_db
from app.users.schemas import UserCreate, UserUpdate, DoctorUpdate, DoctorResponse, DoctorCombinedCreate, DoctorCombinedUpdate
from app.users.services import UserService, DoctorService
from app.core.authentication import protected_route
from app.users.models import UserRoleEnum as RoleEnum
from app.core.response import PaginationMeta, ResponseBase, PaginatedResponse

router = APIRouter(
    prefix="/doctors",    # Tất cả endpoint sẽ có prefix /doctors
    tags=["doctors"],      # Nhóm trong Swagger docs
    responses={404: {"description": "Not found"}}  # Response chung cho 404
)  # Router cho grouping routes


@router.post("/", response_model=ResponseBase[DoctorResponse], status_code=status.HTTP_201_CREATED)
@protected_route([RoleEnum.ADMIN])
def create_doctor(
    CREDENTIALS: AuthCredentialDepend,
    doctor: DoctorCombinedCreate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo bác sĩ mới (bao gồm cả User và Doctor)
    - Kiểm tra email và username đã tồn tại chưa
    - Tự động hash password trước khi lưu
    - Tạo User với role DOCTOR và Doctor liên kết
    """
    repo = UserService(DB)
    doctor_repo = DoctorService(DB)

    # Kiểm tra email đã tồn tại
    if repo.get_user_by_email(doctor.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    # Kiểm tra username đã tồn tại
    if repo.get_user_by_username(doctor.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username đã được sử dụng"
        )

    db_doctor = doctor_repo.create_doctor(doctor)
    return ResponseBase(message="Doctor created successfully", data=db_doctor)


@router.get("/{doctor_id}", response_model=ResponseBase[DoctorResponse])
def read_doctor(
    CREDENTIALS: AuthCredentialDepend,
    doctor_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin bác sĩ theo ID
    - Bao gồm thông tin User liên kết
    """
    repo = DoctorService(DB)
    db_doctor = repo.get_doctor_by_id(doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return ResponseBase(message="Doctor retrieved successfully", data=db_doctor)


@router.get("/", response_model=PaginatedResponse[DoctorResponse])
@protected_route([RoleEnum.ADMIN])
def read_doctors(
    CREDENTIALS: AuthCredentialDepend,
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách bác sĩ với phân trang
    - Bao gồm thông tin User liên kết
    """
    repo = DoctorService(DB)
    doctors = repo.get_doctors(skip=skip, limit=limit)
    total = repo.count_doctors()
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Doctors retrieved successfully", data=doctors, meta=meta)


@router.put("/{doctor_id}", response_model=ResponseBase[DoctorResponse])
@protected_route([RoleEnum.ADMIN])
def update_doctor(
    CREDENTIALS: AuthCredentialDepend,
    doctor_id: UUID,
    doctor: DoctorCombinedUpdate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Cập nhật thông tin bác sĩ
    - Có thể cập nhật cả thông tin User và Doctor
    """
    repo = DoctorService(DB)
    db_doctor = repo.update_doctor(doctor_id=doctor_id, doctor_update=doctor)
    if db_doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )
    return ResponseBase(message="Doctor updated successfully", data=db_doctor)


@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
@protected_route([RoleEnum.ADMIN])
def delete_doctor(
    CREDENTIALS: AuthCredentialDepend,
    doctor_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Xóa bác sĩ (soft delete)
    - Xóa cả User và Doctor liên kết
    """
    repo = DoctorService(DB)
    success = repo.delete_doctor(doctor_id=doctor_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found"
        )