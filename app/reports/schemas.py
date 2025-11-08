from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date

# Request để lọc theo khoảng thời gian hoặc theo period type
class ReportPeriodRequest(BaseModel):
    period_type: Optional[str] = None  # one of: day, week, month, year
    selected_date: Optional[date] = None        # reference date for period_type
    start_date: Optional[date] = None  # explicit range start
    end_date: Optional[date] = None    # explicit range end

class RevenueComparisonRequest(BaseModel):
    period_type: str  # "week", "month", "quarter", "year"
    reference_date: date  # ngày tham chiếu để tính khoảng thời gian

class RevenueDataPoint(BaseModel):
    label: str  # tên của điểm dữ liệu (Thứ 2, Tuần 1, Tháng 1, etc)
    date: date  # ngày đại diện
    total: float
    medications: float
    services: float

class RevenueComparisonReport(BaseModel):
    period_type: str
    start_date: date
    end_date: date
    data_points: List[RevenueDataPoint]
    total_revenue: float
    total_medications: float
    total_services: float

# Các schema response đơn giản cho từng báo cáo
class RevenueReport(BaseModel):
    total: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class BreakdownItem(BaseModel):
    key: Any
    value: float

class RevenueBreakdownReport(BaseModel):
    total: float
    breakdown: List[BreakdownItem] = []
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class PatientStatsReport(BaseModel):
    total_patients: int
    new_patients: int
    revisits: int
    age_distribution: Dict[str, int] = {}
    gender_distribution: Dict[str, int] = {}

class AppointmentStatsReport(BaseModel):
    counts_by_status: Dict[str, int] = {}
    attendance_rate: Optional[float] = None
    cancel_rate: Optional[float] = None
    # avg_advance_days: Optional[float] = None
    # popular_time_slot: Optional[str] = None

class DoctorStatsItem(BaseModel):
    doctor_id: str
    doctor_name: Optional[str]
    patients_seen: int
    revenue: float
    revisit_rate: Optional[float]

class DoctorStatsReport(BaseModel):
    items: List[DoctorStatsItem] = []

class MedicationStatsReport(BaseModel):
    top_prescribed: List[BreakdownItem] = []
    inventory_value: float
    low_stock: List[Dict[str, Any]] = []

class ServiceStatsReport(BaseModel):
    top_services: List[BreakdownItem] = []

class PatientRecordItem(BaseModel):
    patient_id: str
    patient_name: str
    record_count: int

class MedicalRecordStatsReport(BaseModel):
    total_medical_records: int
    top_patients: List[PatientRecordItem] = []
