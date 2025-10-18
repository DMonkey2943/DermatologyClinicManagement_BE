from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import date
from app.core.dependencies import AuthCredentialDepend
from app.database import get_db
from app.core.authentication import protected_route
from app.prescriptions.schemas import PrescriptionFullResponse
from app.prescriptions.services import PrescriptionService
from app.service_indications.schemas import ServiceIndicationFullResponse
from app.service_indications.services import ServiceIndicationService
from app.users.models import UserRoleEnum as RoleEnum
from app.core.response import PaginationMeta, ResponseBase, PaginatedResponse
from app.medical_records.schemas import MedicalRecordCreate, MedicalRecordUpdate, MedicalRecordResponse
from app.medical_records.services import MedicalRecordService

router = APIRouter(
    prefix="/medical_records",
    tags=["medical_records"],
    responses={404: {"description": "Not found"}}
)

@router.post("/", response_model=ResponseBase[MedicalRecordResponse], status_code=status.HTTP_201_CREATED)
@protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
def create_medical_record(
    CREDENTIALS: AuthCredentialDepend,
    record: MedicalRecordCreate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo hồ sơ khám bệnh mới
    - Chỉ ADMIN và DOCTOR mới có quyền tạo hồ sơ khám bệnh
    - Trả về thông tin hồ sơ khám bệnh vừa tạo
    """
    repo = MedicalRecordService(DB)
    db_record = repo.create_medical_record(record)
    return ResponseBase(message="Hồ sơ khám bệnh được tạo thành công", data=db_record)

@router.get("/{record_id}/prescription", response_model=ResponseBase[PrescriptionFullResponse])
def read_prescription_by_medical_record_id(
    CREDENTIALS: AuthCredentialDepend,
    record_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin đơn thuốc theo medical record ID
    - Bất kỳ ai cũng có thể xem thông tin đơn thuốc
    """
    repo = PrescriptionService(DB)
    db_record = repo.get_prescription_by_medical_record_id(record_id)
    if db_record is None:
        return ResponseBase(message="Phiên khám này không có Đơn thuốc", data=None) #Trả về data rỗng khi không có Đơn thuốc
    return ResponseBase(message="Lấy thông tin Đơn thuốc thành công", data=db_record)

@router.get("/{record_id}/service-indication", response_model=ResponseBase[Optional[ServiceIndicationFullResponse]])
def read_service_indication_by_medical_record_id(
    CREDENTIALS: AuthCredentialDepend,
    record_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin Phiếu chỉ định dịch vụ theo medical record ID
    - Bất kỳ ai cũng có thể xem thông tin Phiếu chỉ định dịch vụ
    """
    repo = ServiceIndicationService(DB)
    db_record = repo.get_service_indication_by_medical_record_id(record_id)
    if db_record is None:
        return ResponseBase(message="Phiên khám này không có Phiếu chỉ định dịch vụ", data=None) #Trả về data rỗng khi không có phiếu chỉ định dv
    return ResponseBase(message="Lấy thông tin Phiếu chỉ định dịch vụ thành công", data=db_record)

@router.get("/{record_id}", response_model=ResponseBase[MedicalRecordResponse])
def read_medical_record(
    CREDENTIALS: AuthCredentialDepend,
    record_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy thông tin hồ sơ khám bệnh theo ID
    - Bất kỳ ai cũng có thể xem thông tin hồ sơ khám bệnh
    """
    repo = MedicalRecordService(DB)
    db_record = repo.get_medical_record_by_id(record_id)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Hồ sơ khám bệnh không tồn tại")
    return ResponseBase(message="Lấy thông tin hồ sơ khám bệnh thành công", data=db_record)

@router.get("/", response_model=PaginatedResponse[MedicalRecordResponse])
def read_medical_records(
    CREDENTIALS: AuthCredentialDepend,
    patient_id: Optional[UUID] = Query(None, description="ID bệnh nhân để lọc"),
    doctor_id: Optional[UUID] = Query(None, description="ID bác sĩ (user_id) để lọc"),
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi lấy về"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách hồ sơ khám bệnh với phân trang
    - Bất kỳ ai cũng có thể xem danh sách hồ sơ khám bệnh
    """
    repo = MedicalRecordService(DB)
    total = repo.count_medical_records(patient_id=patient_id, doctor_id=doctor_id)    
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    records = repo.get_medical_records(skip=skip, limit=limit, patient_id=patient_id, doctor_id=doctor_id)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách hồ sơ khám bệnh thành công", data=records, meta=meta)

@router.get("/patient/{patient_id}", response_model=PaginatedResponse[MedicalRecordResponse])
def read_medical_records_by_patient(
    CREDENTIALS: AuthCredentialDepend,
    patient_id: UUID,
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
    limit: int = Query(10, ge=1, le=100, description="Số bản ghi lấy về"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách hồ sơ khám bệnh theo patient_id với phân trang
    - Bất kỳ ai cũng có thể xem danh sách hồ sơ khám bệnh của bệnh nhân
    """
    repo = MedicalRecordService(DB)
    total = repo.count_medical_records()
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    records = repo.get_medical_records_by_patient(patient_id=patient_id, skip=skip, limit=limit)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Lấy danh sách hồ sơ khám bệnh của bệnh nhân thành công", data=records, meta=meta)

@router.put("/{record_id}", response_model=ResponseBase[MedicalRecordResponse])
@protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
def update_medical_record(
    CREDENTIALS: AuthCredentialDepend,
    record_id: UUID,
    record: MedicalRecordUpdate,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Cập nhật thông tin hồ sơ khám bệnh
    - Chỉ ADMIN và DOCTOR mới có quyền cập nhật hồ sơ khám bệnh
    - Trả về thông tin hồ sơ khám bệnh vừa cập nhật
    """
    repo = MedicalRecordService(DB)
    db_record = repo.update_medical_record(record_id, record)
    if db_record is None:
        raise HTTPException(status_code=404, detail="Hồ sơ khám bệnh không tồn tại")
    return ResponseBase(message="Cập nhật hồ sơ khám bệnh thành công", data=db_record)

# @router.delete("/{record_id}", response_model=ResponseBase[None])
# @protected_route([RoleEnum.ADMIN, RoleEnum.DOCTOR])
# def delete_medical_record(
#     CREDENTIALS: AuthCredentialDepend,
#     record_id: UUID,
#     DB: Session = Depends(get_db),
#     CURRENT_USER = None,
# ):
#     """
#     Xóa hồ sơ khám bệnh
#     - Chỉ ADMIN và DOCTOR mới có quyền xóa hồ sơ khám bệnh
#     - Trả về thông báo xóa thành công
#     """
#     repo = MedicalRecordService(DB)
#     success = repo.delete_medical_record(record_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Hồ sơ khám bệnh không tồn tại")
#     return ResponseBase(message="Xóa hồ sơ khám bệnh thành công", data=None)