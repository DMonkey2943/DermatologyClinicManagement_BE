from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import AuthCredentialDepend
from app.database import get_db
from app.core.response import ResponseBase
from app.reports.schemas import (
    ReportPeriodRequest,
    RevenueReport,
    RevenueBreakdownReport,
    PatientStatsReport,
    AppointmentStatsReport,
    DoctorStatsReport,
    MedicationStatsReport,
    ServiceStatsReport,
)
from app.reports.services import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    responses={404: {"description": "Not found"}}
)

# Tổng doanh thu
@router.post("/revenue/total", response_model=ResponseBase)
def report_revenue_total(
    CREDENTIALS: AuthCredentialDepend,
    payload: ReportPeriodRequest,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    repo = ReportService(DB)
    data = repo.revenue_total(payload)
    return ResponseBase(message="Báo cáo doanh thu tổng", data=data)

# Doanh thu từ medications
@router.post("/revenue/medications", response_model=ResponseBase)
def report_revenue_medications(
    CREDENTIALS: AuthCredentialDepend,
    payload: ReportPeriodRequest,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    repo = ReportService(DB)
    data = repo.revenue_medications(payload)
    return ResponseBase(message="Báo cáo doanh thu từ thuốc", data=data)

# Doanh thu từ services
@router.post("/revenue/services", response_model=ResponseBase)
def report_revenue_services(
    CREDENTIALS: AuthCredentialDepend,
    payload: ReportPeriodRequest,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    repo = ReportService(DB)
    data = repo.revenue_services(payload)
    return ResponseBase(message="Báo cáo doanh thu từ dịch vụ", data=data)

# Thống kê bệnh nhân
@router.post("/patients", response_model=ResponseBase)
def report_patients(
    CREDENTIALS: AuthCredentialDepend,
    payload: ReportPeriodRequest,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    repo = ReportService(DB)
    data = repo.patient_stats(payload)
    return ResponseBase(message="Báo cáo thống kê bệnh nhân", data=data)

# Thống kê lịch hẹn
@router.post("/appointments", response_model=ResponseBase)
def report_appointments(
    CREDENTIALS: AuthCredentialDepend,
    payload: ReportPeriodRequest,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    repo = ReportService(DB)
    data = repo.appointment_stats(payload)
    return ResponseBase(message="Báo cáo thống kê lịch hẹn", data=data)

# Thống kê theo bác sĩ
@router.post("/doctors", response_model=ResponseBase)
def report_doctors(
    CREDENTIALS: AuthCredentialDepend,
    payload: ReportPeriodRequest,
    DB: Session = Depends(get_db),    
    CURRENT_USER = None,
):
    repo = ReportService(DB)
    data = repo.doctor_stats(payload)
    return ResponseBase(message="Báo cáo thống kê theo bác sĩ", data=data)

# Thống kê thuốc
@router.post("/medications", response_model=ResponseBase)
def report_medications(
    CREDENTIALS: AuthCredentialDepend,
    payload: ReportPeriodRequest,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    repo = ReportService(DB)
    data = repo.medication_stats(payload)
    return ResponseBase(message="Báo cáo thống kê thuốc", data=data)

# Thống kê dịch vụ
@router.post("/services", response_model=ResponseBase)
def report_services(
    CREDENTIALS: AuthCredentialDepend,
    payload: ReportPeriodRequest,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    repo = ReportService(DB)
    data = repo.service_stats(payload)
    return ResponseBase(message="Báo cáo thống kê dịch vụ", data=data)
