from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import date, datetime, timedelta
from typing import Tuple, Optional, List, Dict, Any
from calendar import monthrange
from app.invoices.models import Invoice
from app.prescriptions.models import PrescriptionDetail
from app.medications.models import Medication
from app.patients.models import Patient
from app.appointments.models import Appointment
from app.medical_records.models import MedicalRecord
from app.users.models import User
from app.reports.schemas import (
    ReportPeriodRequest,
)

class ReportService:
    """
    Service để thực hiện các báo cáo.
    Ghi chú: một số báo cáo (ví dụ breakdown theo từng service) phụ thuộc model chi tiết dịch vụ.
    Nếu model đó không tồn tại, hàm sẽ trả về dữ liệu rỗng thay vì raise lỗi.
    """
    def __init__(self, db: Session):
        self.db = db

    # Helper: tính khoảng start/end từ request
    def _resolve_period(self, req: ReportPeriodRequest) -> Tuple[date, date]:
        # Nếu người dùng đưa explicit range thì dùng luôn
        if req.start_date and req.end_date:
            return req.start_date, req.end_date
        # Nếu period_type + date được cung cấp -> tính theo day/week/month/year
        ref = req.selected_date or date.today()
        pt = (req.period_type or "day").lower()
        if pt == "day":
            return ref, ref
        if pt == "week":
            # tuần bắt đầu thứ Hai
            start = ref - timedelta(days=ref.weekday())
            end = start + timedelta(days=6)
            return start, end
        if pt == "month":
            start = ref.replace(day=1)
            # next month trick
            if start.month == 12:
                next_month = start.replace(year=start.year+1, month=1, day=1)
            else:
                next_month = start.replace(month=start.month+1, day=1)
            end = next_month - timedelta(days=1)
            return start, end
        if pt == "year":
            start = ref.replace(month=1, day=1)
            end = ref.replace(month=12, day=31)
            return start, end
        # default day
        return ref, ref
    
    def revenue_comparison(self, req) -> Dict[str, Any]:
        """
        So sánh doanh thu theo các khoảng thời gian
        """
        
        ref_date = req.reference_date or date.today()
        period_type = req.period_type.lower()
        
        data_points = []
        
        if period_type == "week":
            # Tuần bắt đầu từ thứ Hai
            start = ref_date - timedelta(days=ref_date.weekday())
            end = start + timedelta(days=6)

            # Tên ngày trong tuần
            weekdays = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
            
            # Lấy dữ liệu cho từng ngày trong tuần
            for i in range(7):
                day = start + timedelta(days=i)
                # day_name = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"][i]

                # Định dạng label: dd/mm/yy (weekday)
                day_label = f"{day.strftime('%d/%m/%y')} ({weekdays[i]})"
                
                total = self.db.query(func.coalesce(func.sum(Invoice.final_amount), 0)).filter(
                    func.date(Invoice.created_at) == day
                ).scalar() or 0.0
                
                medications = self.db.query(func.coalesce(func.sum(Invoice.medication_subtotal), 0)).filter(
                    func.date(Invoice.created_at) == day
                ).scalar() or 0.0
                
                services = self.db.query(func.coalesce(func.sum(Invoice.service_subtotal), 0)).filter(
                    func.date(Invoice.created_at) == day
                ).scalar() or 0.0
                
                data_points.append({
                    "label": day_label,
                    "date": day,
                    "total": float(total),
                    "medications": float(medications),
                    "services": float(services)
                })
        
        elif period_type == "month":
            # Lấy tháng hiện tại
            start = ref_date.replace(day=1)
            last_day = monthrange(start.year, start.month)[1]
            end = start.replace(day=last_day)
            
            # Lấy dữ liệu cho từng ngày trong tháng
            for day in range(1, last_day + 1):
                current_day = start.replace(day=day)
                
                total = self.db.query(func.coalesce(func.sum(Invoice.final_amount), 0)).filter(
                    func.date(Invoice.created_at) == current_day
                ).scalar() or 0.0
                
                medications = self.db.query(func.coalesce(func.sum(Invoice.medication_subtotal), 0)).filter(
                    func.date(Invoice.created_at) == current_day
                ).scalar() or 0.0
                
                services = self.db.query(func.coalesce(func.sum(Invoice.service_subtotal), 0)).filter(
                    func.date(Invoice.created_at) == current_day
                ).scalar() or 0.0
                
                data_points.append({
                    "label": f"Ngày {day}",
                    "date": current_day,
                    "total": float(total),
                    "medications": float(medications),
                    "services": float(services)
                })
        
        elif period_type == "quarter":
            # Xác định quý
            quarter = (ref_date.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            start = ref_date.replace(month=start_month, day=1)
            
            # Lấy dữ liệu cho từng tuần trong quý (khoảng 13 tuần)
            week_num = 1
            current_week_start = start - timedelta(days=start.weekday())
            
            for i in range(13):
                week_start = current_week_start + timedelta(weeks=i)
                week_end = week_start + timedelta(days=6)
                
                # Chỉ lấy tuần nằm trong quý
                if week_start.month > start_month + 2:
                    break

                # Định dạng label: Tuần {week_num} (dd/mm-dd/mm/yy)
                week_label = f"Tuần {week_num} ({week_start.strftime('%d/%m')}-{week_end.strftime('%d/%m/%y')})"
                
                total = self.db.query(func.coalesce(func.sum(Invoice.final_amount), 0)).filter(
                    func.date(Invoice.created_at).between(week_start, week_end)
                ).scalar() or 0.0
                
                medications = self.db.query(func.coalesce(func.sum(Invoice.medication_subtotal), 0)).filter(
                    func.date(Invoice.created_at).between(week_start, week_end)
                ).scalar() or 0.0
                
                services = self.db.query(func.coalesce(func.sum(Invoice.service_subtotal), 0)).filter(
                    func.date(Invoice.created_at).between(week_start, week_end)
                ).scalar() or 0.0
                
                data_points.append({
                    "label": f"Tuần {week_num}",
                    # "label": week_label,
                    "date": week_start,
                    "total": float(total),
                    "medications": float(medications),
                    "services": float(services)
                })
                week_num += 1
            
            end = start.replace(month=start_month + 2)
            end = end.replace(day=monthrange(end.year, end.month)[1])
        
        elif period_type == "year":
            # Lấy năm hiện tại
            start = ref_date.replace(month=1, day=1)
            end = ref_date.replace(month=12, day=31)
            
            # Lấy dữ liệu cho từng tháng trong năm
            month_names = ["Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
                        "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12"]
            
            for month in range(1, 13):
                month_start = start.replace(month=month, day=1)
                month_end = month_start.replace(day=monthrange(start.year, month)[1])
                
                total = self.db.query(func.coalesce(func.sum(Invoice.final_amount), 0)).filter(
                    func.date(Invoice.created_at).between(month_start, month_end)
                ).scalar() or 0.0
                
                medications = self.db.query(func.coalesce(func.sum(Invoice.medication_subtotal), 0)).filter(
                    func.date(Invoice.created_at).between(month_start, month_end)
                ).scalar() or 0.0
                
                services = self.db.query(func.coalesce(func.sum(Invoice.service_subtotal), 0)).filter(
                    func.date(Invoice.created_at).between(month_start, month_end)
                ).scalar() or 0.0
                
                data_points.append({
                    "label": month_names[month - 1],
                    "date": month_start,
                    "total": float(total),
                    "medications": float(medications),
                    "services": float(services)
                })
        
        # Tính tổng
        total_revenue = sum(dp["total"] for dp in data_points)
        total_medications = sum(dp["medications"] for dp in data_points)
        total_services = sum(dp["services"] for dp in data_points)
        
        return {
            "period_type": period_type,
            "start_date": start,
            "end_date": end,
            "data_points": data_points,
            "total_revenue": float(total_revenue),
            "total_medications": float(total_medications),
            "total_services": float(total_services)
        }

    # ---------------------------
    # Doanh thu tổng
    # ---------------------------
    def revenue_total(self, req: ReportPeriodRequest) -> Dict[str, Any]:
        start, end = self._resolve_period(req)
        q = self.db.query(func.coalesce(func.sum(Invoice.final_amount), 0)).filter(
            func.date(Invoice.created_at).between(start, end)
        )
        total = q.scalar() or 0.0
        return {"total": float(total), "start_date": start, "end_date": end}

    # ---------------------------
    # Doanh thu từ medications
    # ---------------------------
    def revenue_medications(self, req: ReportPeriodRequest) -> Dict[str, Any]:
        start, end = self._resolve_period(req)
        q = self.db.query(func.coalesce(func.sum(Invoice.medication_subtotal), 0)).filter(
            func.date(Invoice.created_at).between(start, end)
        )
        total = q.scalar() or 0.0
        # Có thể bổ sung breakdown theo thuốc bằng cách join PrescriptionDetail nếu cần
        return {"total": float(total), "start_date": start, "end_date": end}

    # ---------------------------
    # Doanh thu từ services
    # ---------------------------
    def revenue_services(self, req: ReportPeriodRequest) -> Dict[str, Any]:
        start, end = self._resolve_period(req)
        q = self.db.query(func.coalesce(func.sum(Invoice.service_subtotal), 0)).filter(
            func.date(Invoice.created_at).between(start, end)
        )
        total = q.scalar() or 0.0
        return {"total": float(total), "start_date": start, "end_date": end}

    # ---------------------------
    # Thống kê bệnh nhân
    # ---------------------------
    def patient_stats(self, req: ReportPeriodRequest) -> Dict[str, Any]:
        start, end = self._resolve_period(req)
        # Tổng số bệnh nhân đã đăng ký
        total_patients = self.db.query(func.count(Patient.id)).scalar() or 0
        # Bệnh nhân mới trong khoảng
        new_patients = self.db.query(func.count(Patient.id)).filter(
            func.date(Patient.created_at).between(start, end)
        ).scalar() or 0
        # Số bệnh nhân tái khám: tính những bệnh nhân có >=2 medical records (toàn bộ thời gian)
        sub = self.db.query(MedicalRecord.patient_id, func.count(MedicalRecord.id).label("cnt")).group_by(MedicalRecord.patient_id).subquery()
        revisits = self.db.query(func.count(sub.c.patient_id)).filter(sub.c.cnt >= 2).scalar() or 0

        # Phân bố tuổi + giới tính (lấy snapshot tại end date)
        age_buckets = {"0-17":0,"18-30":0,"31-45":0,"46-60":0,"61+":0}
        gender_dist: Dict[str,int] = {}
        patients = self.db.query(Patient).all()
        for p in patients:
            # cố gắng tính tuổi nếu có birth_date
            bd = getattr(p, "dob", None)
            if bd:
                try:
                    age = (end - bd).days // 365
                except Exception:
                    age = None
            else:
                age = None
            if age is not None:
                if age <= 17:
                    age_buckets["0-17"] += 1
                elif age <= 30:
                    age_buckets["18-30"] += 1
                elif age <= 45:
                    age_buckets["31-45"] += 1
                elif age <= 60:
                    age_buckets["46-60"] += 1
                else:
                    age_buckets["61+"] += 1
            g = getattr(p, "gender", "unknown") or "unknown"
            gender_dist[g] = gender_dist.get(g, 0) + 1

        return {
            "total_patients": int(total_patients),
            "new_patients": int(new_patients),
            "revisits": int(revisits),
            "age_distribution": age_buckets,
            "gender_distribution": gender_dist
        }

    # ---------------------------
    # Thống kê lịch hẹn
    # ---------------------------
    def appointment_stats(self, req: ReportPeriodRequest) -> Dict[str, Any]:
        start, end = self._resolve_period(req)
        q = self.db.query(Appointment).filter(func.date(Appointment.appointment_date).between(start, end))
        total = q.count()
        # counts by status
        counts = dict(self.db.query(Appointment.status, func.count(Appointment.id)).filter(
            func.date(Appointment.appointment_date).between(start, end)
        ).group_by(Appointment.status).all())
        # attendance / cancel rates
        attended = self.db.query(func.count(Appointment.id)).filter(
            func.date(Appointment.appointment_date).between(start, end),
            Appointment.status == "COMPLETED"
        ).scalar() or 0
        cancelled = self.db.query(func.count(Appointment.id)).filter(
            func.date(Appointment.appointment_date).between(start, end),
            Appointment.status == "CANCELLED"
        ).scalar() or 0
        attendance_rate = (attended/total) if total>0 else None
        cancel_rate = (cancelled/total) if total>0 else None
        # # avg advance booking (days between created_at and appointment_date)
        # adv_q = self.db.query(func.avg(func.julianday(Appointment.appointment_date) - func.julianday(Appointment.created_at))).filter(
        #     func.date(Appointment.appointment_date).between(start, end)
        # ).scalar()
        # avg_advance_days = float(adv_q) if adv_q is not None else None
        # # popular time slot
        # popular = self.db.query(Appointment.time_slot, func.count(Appointment.id)).filter(
        #     func.date(Appointment.appointment_date).between(start, end)
        # ).group_by(Appointment.time_slot).order_by(func.count(Appointment.id).desc()).first()
        # popular_slot = popular[0] if popular else None

        return {
            "counts_by_status": counts,
            "attendance_rate": attendance_rate,
            "cancel_rate": cancel_rate,
            # "avg_advance_days": avg_advance_days,
            # "popular_time_slot": popular_slot
        }

    # ---------------------------
    # Thống kê theo bác sĩ
    # ---------------------------
    def doctor_stats(self, req: ReportPeriodRequest) -> Dict[str, Any]:
        start, end = self._resolve_period(req)
        # Số lượng bệnh nhân đã khám và doanh thu do bác sĩ tạo ra trong khoảng
        # patients_seen: distinct medical_records.patient_id where medical_record.doctor_id = doctor
        mr_q = self.db.query(
            MedicalRecord.doctor_id,
            func.count(distinct(MedicalRecord.patient_id)).label("patients_seen")
        ).filter(func.date(MedicalRecord.created_at).between(start, end)).group_by(MedicalRecord.doctor_id).subquery()

        revenue_q = self.db.query(
            Invoice.doctor_id,
            func.coalesce(func.sum(Invoice.final_amount), 0).label("revenue")
        ).filter(func.date(Invoice.created_at).between(start, end)).group_by(Invoice.doctor_id).subquery()

        # join doctors present in either subquery
        results = []
        doctor_ids = set()
        for row in self.db.query(mr_q).all():
            doctor_ids.add(row[0])
        for row in self.db.query(revenue_q).all():
            doctor_ids.add(row[0])

        for did in doctor_ids:
            doc = self.db.query(User).filter(User.id == did).first()
            patients_seen = self.db.query(func.count(distinct(MedicalRecord.patient_id))).filter(
                MedicalRecord.doctor_id == did,
                func.date(MedicalRecord.created_at).between(start, end)
            ).scalar() or 0
            revenue = self.db.query(func.coalesce(func.sum(Invoice.final_amount), 0)).filter(
                Invoice.doctor_id == did,
                func.date(Invoice.created_at).between(start, end)
            ).scalar() or 0.0
            # revisit rate for this doctor's patients: among patients seen by this doctor in period, how many have >1 visit with same doctor across history
            sub = self.db.query(MedicalRecord.patient_id, func.count(MedicalRecord.id).label("cnt")).filter(
                MedicalRecord.doctor_id == did
            ).group_by(MedicalRecord.patient_id).subquery()
            revisits_count = self.db.query(func.count(sub.c.patient_id)).filter(sub.c.cnt >= 2).scalar() or 0
            patients_total_for_doctor = int(patients_seen)
            revisit_rate = (revisits_count / patients_total_for_doctor) if patients_total_for_doctor>0 else None

            results.append({
                "doctor_id": str(did),
                "doctor_name": getattr(doc, "full_name", None) if doc else None,
                "patients_seen": int(patients_seen),
                "revenue": float(revenue),
                "revisit_rate": revisit_rate
            })

        return {"items": results}

    # ---------------------------
    # Thống kê thuốc
    # ---------------------------
    def medication_stats(self, req: ReportPeriodRequest) -> Dict[str, Any]:
        start, end = self._resolve_period(req)
        # Top thuốc được kê đơn nhiều nhất (dựa trên PrescriptionDetail.quantity)
        top = self.db.query(
            PrescriptionDetail.medication_id,
            func.coalesce(func.sum(PrescriptionDetail.quantity), 0).label("qty")
        ).join(Medication, PrescriptionDetail.medication_id == Medication.id).group_by(PrescriptionDetail.medication_id).order_by(func.sum(PrescriptionDetail.quantity).desc()).limit(20).all()

        top_list = [{"key": str(row[0]), "value": int(row[1])} for row in top]

        # Giá trị tồn kho hiện tại = sum(price * stock_quantity)
        inv_q = self.db.query(func.coalesce(func.sum(func.coalesce(Medication.price,0)*func.coalesce(Medication.stock_quantity,0)), 0)).scalar() or 0.0

        # Thuốc sắp hết: cố gắng dùng trường min_stock nếu tồn tại, ngược lại dùng threshold 50
        meds = self.db.query(Medication).all()
        low = []
        for m in meds:
            stock = getattr(m, "stock_quantity", None)
            if stock is None:
                continue
            min_stock = getattr(m, "min_stock", None)
            threshold = min_stock if (min_stock is not None) else 50
            if stock <= threshold:
                low.append({
                    "medication_id": str(m.id),
                    "name": getattr(m, "name", None),
                    "stock_quantity": stock,
                    "threshold": threshold
                })

        return {
            "top_prescribed": top_list,
            "inventory_value": float(inv_q),
            "low_stock": low
        }

    # ---------------------------
    # Thống kê dịch vụ
    # ---------------------------
    def service_stats(self, req: ReportPeriodRequest) -> Dict[str, Any]:
        start, end = self._resolve_period(req)
        from app.services.models import Service
        from app.service_indications.models import ServiceIndicationDetail
        top = self.db.query(
            ServiceIndicationDetail.service_id,
            func.coalesce(func.sum(ServiceIndicationDetail.quantity), 0).label("qty")
        ).group_by(ServiceIndicationDetail.service_id).order_by(func.sum(ServiceIndicationDetail.quantity).desc()).limit(20).all()
        top_list = []
        for row in top:
            svc = self.db.query(Service).filter(Service.id == row[0]).first()
            top_list.append({"key": getattr(svc, "name", str(row[0])), "value": int(row[1])})
        return {"top_services": top_list}