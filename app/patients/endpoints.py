from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.patients.schemas import PatientCreate, PatientUpdate, PatientResponse
from app.patients.services import PatientService
from app.core.response import ResponseBase, PaginationMeta, PaginatedResponse

router = APIRouter(
    prefix="/patients",    # Tất cả endpoint sẽ có prefix /patients
    tags=["patients"],      # Nhóm trong Swagger docs
    responses={404: {"description": "Patient not found"}}  # Response chung cho 404
)  # Router cho grouping routes


@router.post("/", response_model=ResponseBase[PatientResponse], status_code=status.HTTP_201_CREATED)
def create_patient(
    patient: PatientCreate,                   # Request body sử dụng schema UserCreate
    db: Session = Depends(get_db)       # Dependency injection cho database
):
    """
    Tạo bệnh nhân mới
    - Validate dữ liệu đầu vào qua schema
    - Trả về thông tin bệnh nhân vừa tạo
    """

    repo = PatientService(db)  # Tạo repository instance
    db_patient = repo.create_patient(patient)
    return ResponseBase(message="Thêm bệnh nhân mới thành công", data=db_patient)  # Wrap response


@router.get("/{patient_id}", response_model=ResponseBase[PatientResponse])
def read_patient(patient_id: UUID, db: Session = Depends(get_db)):
    repo = PatientService(db)
    db_patient = repo.get_patient_by_id(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return ResponseBase(message="Lấy thông tin bệnh nhân thành công", data=db_patient)  # Wrap response


# @router.get("/", response_model=PaginatedResponse[PatientResponse])
# def read_patients(
#     skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
#     limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
#     search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc số điện thoại"),
#     db: Session = Depends(get_db)
# ):
#     """
#     Lấy danh sách bệnh nhân
#     - Hỗ trợ tìm kiếm theo tên hoặc số điện thoại
#     - Phân trang với skip và limit
#     """
#     repo = PatientService(db)
#     if search:
#         patients = repo.search_patients(search_term=search, skip=skip, limit=limit)
#         total = repo.count_patients(search_term=search)  # Đếm tổng số bệnh nhân khớp với search
#     else:
#         patients = repo.get_patients(skip=skip, limit=limit)
#         total = repo.count_patients()  # Đếm tất cả bệnh nhân
#     page = (skip // limit) + 1
#     total_pages = (total // limit) + (1 if total % limit else 0)
#     meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
#     return PaginatedResponse(
#         message="Patients retrieved successfully",
#         data=patients,
#         meta=meta
#     )  # Wrap với pagination

@router.get("/", response_model=PaginatedResponse[PatientResponse])
def read_patients(
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    q: Optional[str] = Query(None, description="Search query: tìm theo full_name (không phân biệt hoa thường) hoặc phone_number"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách bệnh nhân
    - Hỗ trợ tìm kiếm theo tên hoặc số điện thoại
    - Phân trang với skip và limit
    """
    repo = PatientService(db)
    patients = repo.get_patients(skip=skip, limit=limit, q=q)
    total = repo.count_patients(search_term=q)  # Đếm tổng số bệnh nhân khớp với search
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(
        message="Patients retrieved successfully",
        data=patients,
        meta=meta
    )  # Wrap với pagination

@router.put("/{patient_id}", response_model=ResponseBase[PatientResponse])
def update_patient(
    patient_id: UUID,
    patient: PatientUpdate,                   # Request body cho update
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin bệnh nhân"""
    repo = PatientService(db)
    db_patient = repo.update_patient(patient_id=patient_id, patient_update=patient)
    if db_patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    return ResponseBase(message="Cập nhật thông tin bệnh nhân thành công", data=db_patient)


@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    patient_id: UUID,
    db: Session = Depends(get_db)
):
    """Xóa bệnh nhân (soft delete)"""
    repo = PatientService(db)
    success = repo.delete_patient(patient_id=patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
