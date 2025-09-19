from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, timedelta
from fastapi import HTTPException
from app.appointments.models import Appointment, AppointmentStatusEnum
from app.appointments.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.users.services import UserService
from app.patients.services import PatientService
from app.users.models import UserRoleEnum

class AppointmentService:
    """Service class để xử lý logic liên quan đến Appointment"""
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
        self.patient_service = PatientService(db)

    def create_appointment(self, appointment_in: AppointmentCreate) -> AppointmentResponse:
        """Tạo lịch hẹn mới"""
        # Kiểm tra xem patient_id có tồn tại
        patient = self.patient_service.get_patient_by_id(appointment_in.patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Bệnh nhân không tồn tại")

        # Kiểm tra xem doctor_id (user_id của bác sĩ) có tồn tại và có vai trò DOCTOR
        doctor = self.user_service.get_user_by_id(appointment_in.doctor_id)
        if not doctor:
            raise HTTPException(status_code=404, detail="Bác sĩ không tồn tại")
        if doctor.role != UserRoleEnum.DOCTOR:
            raise HTTPException(status_code=400, detail="User không phải là bác sĩ: "+str(doctor.role))

        # Kiểm tra xem created_by (user_id của người tạo) có tồn tại
        created_by_user = self.user_service.get_user_by_id(appointment_in.created_by)
        if not created_by_user:
            raise HTTPException(status_code=404, detail="Nhân viên không tồn tại")

        # Tạo đối tượng Appointment
        db_appointment = Appointment(
            patient_id=appointment_in.patient_id,
            doctor_id=appointment_in.doctor_id,
            created_by=appointment_in.created_by,
            appointment_date=appointment_in.appointment_date,
            time_slot=appointment_in.time_slot,
            status=appointment_in.status,
            notes=appointment_in.notes
        )

        # Thêm vào database
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)

        # Tạo response với thông tin liên quan
        return AppointmentResponse(
            id=db_appointment.id,
            patient_id=db_appointment.patient_id,
            doctor_id=db_appointment.doctor_id,
            created_by=db_appointment.created_by,
            appointment_date=db_appointment.appointment_date,
            time_slot=db_appointment.time_slot,
            status=db_appointment.status,
            notes=db_appointment.notes,
            created_at=db_appointment.created_at,
            patient=patient,
            doctor=doctor
        )

    def get_appointment_by_id(self, appointment_id: UUID) -> Optional[AppointmentResponse]:
        """Lấy lịch hẹn theo ID"""
        db_appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not db_appointment:
            return None

        # Lấy thông tin bệnh nhân và bác sĩ
        patient = self.patient_service.get_patient_by_id(db_appointment.patient_id)
        doctor = self.user_service.get_user_by_id(db_appointment.doctor_id)

        return AppointmentResponse(
            id=db_appointment.id,
            patient_id=db_appointment.patient_id,
            doctor_id=db_appointment.doctor_id,
            created_by=db_appointment.created_by,
            appointment_date=db_appointment.appointment_date,
            time_slot=db_appointment.time_slot,
            status=db_appointment.status,
            notes=db_appointment.notes,
            created_at=db_appointment.created_at,
            patient=patient,
            doctor=doctor
        )

    def get_appointments(
        self,
        doctor_id: Optional[UUID] = None,
        appointment_date: Optional[date] = None,
        week_start: Optional[date] = None,
        month: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[AppointmentResponse]:
        """Lấy danh sách lịch hẹn với phân trang và các bộ lọc"""
        query = self.db.query(Appointment)

        # Lọc theo bác sĩ
        if doctor_id:
            doctor = self.user_service.get_user_by_id(doctor_id)
            if not doctor:
                raise HTTPException(status_code=404, detail="Bác sĩ không tồn tại")
            if doctor.role != "DOCTOR":
                raise HTTPException(status_code=400, detail="User không phải là bác sĩ")
            query = query.filter(Appointment.doctor_id == doctor_id)

        # Lọc theo ngày
        if appointment_date:
            query = query.filter(Appointment.appointment_date == appointment_date)

        # Lọc theo tuần
        if week_start:
            week_end = week_start + timedelta(days=6)
            query = query.filter(Appointment.appointment_date.between(week_start, week_end))

        # Lọc theo tháng
        if month:
            try:
                # Phân tích định dạng YYYY-MM
                year, month_num = map(int, month.split('-'))
                start_date = date(year, month_num, 1)
                # Tính ngày cuối tháng
                next_month = start_date.replace(month=month_num % 12 + 1, day=1) if month_num < 12 else start_date.replace(year=year + 1, month=1, day=1)
                end_date = next_month - timedelta(days=1)
                query = query.filter(Appointment.appointment_date.between(start_date, end_date))
            except ValueError:
                raise HTTPException(status_code=400, detail="Định dạng tháng không hợp lệ, sử dụng YYYY-MM")

        # Áp dụng phân trang
        appointments = query.offset(skip).limit(limit).all()
        result = []
        for appointment in appointments:
            patient = self.patient_service.get_patient_by_id(appointment.patient_id)
            doctor = self.user_service.get_user_by_id(appointment.doctor_id)
            result.append(AppointmentResponse(
                id=appointment.id,
                patient_id=appointment.patient_id,
                doctor_id=appointment.doctor_id,
                created_by=appointment.created_by,
                appointment_date=appointment.appointment_date,
                time_slot=appointment.time_slot,
                status=appointment.status,
                notes=appointment.notes,
                created_at=appointment.created_at,
                patient=patient,
                doctor=doctor
            ))
        return result

    def count_appointments(
        self,
        doctor_id: Optional[UUID] = None,
        appointment_date: Optional[date] = None,
        week_start: Optional[date] = None,
        month: Optional[str] = None
    ) -> int:
        """Đếm tổng số lịch hẹn với các bộ lọc"""
        query = self.db.query(Appointment)

        # Lọc theo bác sĩ
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)

        # Lọc theo ngày
        if appointment_date:
            query = query.filter(Appointment.appointment_date == appointment_date)

        # Lọc theo tuần
        if week_start:
            week_end = week_start + timedelta(days=6)
            query = query.filter(Appointment.appointment_date.between(week_start, week_end))

        # Lọc theo tháng
        if month:
            try:
                year, month_num = map(int, month.split('-'))
                start_date = date(year, month_num, 1)
                next_month = start_date.replace(month=month_num % 12 + 1, day=1) if month_num < 12 else start_date.replace(year=year + 1, month=1, day=1)
                end_date = next_month - timedelta(days=1)
                query = query.filter(Appointment.appointment_date.between(start_date, end_date))
            except ValueError:
                raise HTTPException(status_code=400, detail="Định dạng tháng không hợp lệ, sử dụng YYYY-MM")

        return query.count()

    def update_appointment(self, appointment_id: UUID, appointment_update: AppointmentUpdate) -> Optional[AppointmentResponse]:
        """Cập nhật thông tin lịch hẹn"""
        db_appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
        if not db_appointment:
            return None

        # Cập nhật các trường được cung cấp
        update_data = appointment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_appointment, field, value)

        self.db.commit()
        self.db.refresh(db_appointment)

        # Lấy thông tin bệnh nhân và bác sĩ
        patient = self.patient_service.get_patient_by_id(db_appointment.patient_id)
        doctor = self.user_service.get_user_by_id(db_appointment.doctor_id)

        return AppointmentResponse(
            id=db_appointment.id,
            patient_id=db_appointment.patient_id,
            doctor_id=db_appointment.doctor_id,
            created_by=db_appointment.created_by,
            appointment_date=db_appointment.appointment_date,
            time_slot=db_appointment.time_slot,
            status=db_appointment.status,
            notes=db_appointment.notes,
            created_at=db_appointment.created_at,
            patient=patient,
            doctor=doctor
        )

    # def delete_appointment(self, appointment_id: UUID) -> bool:
    #     """Xóa lịch hẹn"""
    #     db_appointment = self.db.query(Appointment).filter(Appointment.id == appointment_id).first()
    #     if not db_appointment:
    #         return False

    #     self.db.delete(db_appointment)
    #     self.db.commit()
    #     return True