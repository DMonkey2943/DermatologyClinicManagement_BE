from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.database import get_db
from app.patients.schemas import PatientCreate, PatientUpdate, PatientResponse
from app.patients.services import PatientService

router = APIRouter(
    prefix="/patients",    # Tất cả endpoint sẽ có prefix /patients
    tags=["patients"],      # Nhóm trong Swagger docs
    responses={404: {"description": "Patient not found"}}  # Response chung cho 404
)  # Router cho grouping routes


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
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
    return db_patient


@router.get("/{patient_id}", response_model=PatientResponse)
def read_patient(patient_id: UUID, db: Session = Depends(get_db)):
    repo = PatientService(db)
    db_patient = repo.get_patient_by_id(patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient


@router.get("/", response_model=List[PatientResponse])
def read_patients(
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),     # Query parameter với validation
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên hoặc số điện thoại"),
    db: Session = Depends(get_db)
):
    """
    Lấy danh sách bệnh nhân
    - Hỗ trợ tìm kiếm theo tên hoặc số điện thoại
    - Phân trang với skip và limit
    """
    repo = PatientService(db)
    if search:
        # Nếu có search term, sử dụng search function
        patients = repo.search_patients(search_term=search)
        return patients
    else:
        # Ngược lại, lấy danh sách thông thường
        patients = repo.get_patients(skip=skip, limit=limit)
        return patients


@router.put("/{patient_id}", response_model=PatientResponse)
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
    return db_patient


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
