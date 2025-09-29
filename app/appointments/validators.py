from datetime import date, time

def validate_appointment_date(value: date) -> date:
    """Validate ngày hẹn phải từ hôm nay trở đi"""
    today = date.today()
    if value < today:
        raise ValueError(f"Ngày hẹn ({value}) phải từ hôm nay trở đi.")
    return value

def validate_appointment_time(value: time) -> time:
    """Validate giờ hẹn"""

    # Giờ hợp lệ cho Thứ Hai - Thứ Sáu
    weekday_morning_start = time(11, 0)  # 11:00
    weekday_morning_end = time(13, 0)    # 13:00
    weekday_evening_start = time(17, 0)  # 17:00
    weekday_evening_end = time(20, 0)    # 20:00
    if not (
        (weekday_morning_start <= value <= weekday_morning_end) or
        (weekday_evening_start <= value <= weekday_evening_end)
    ):
        raise ValueError(
            f"Giờ hẹn ({value}) phải từ 11:00-13:00 hoặc 17:00-20:00."
        )
    
    return value

# def validate_appointment_time_for_date(appointment_time: time, appointment_date: date) -> time:
#     """Validate giờ hẹn dựa trên ngày trong tuần"""
#     if not appointment_date:
#         raise ValueError("Ngày hẹn không được để trống.")

#     # Xác định ngày trong tuần (0 = Thứ Hai, 6 = Chủ Nhật)
#     weekday = appointment_date.weekday()

#     # Giờ hợp lệ cho Thứ Hai - Thứ Sáu
#     weekday_morning_start = time(11, 0)  # 11:00
#     weekday_morning_end = time(13, 0)    # 13:00
#     weekday_evening_start = time(17, 0)  # 17:00
#     weekday_evening_end = time(20, 0)    # 20:00

#     # Giờ hợp lệ cho Thứ Bảy - Chủ Nhật
#     weekend_morning_start = time(8, 0)   # 08:00
#     weekend_morning_end = time(13, 0)    # 13:00
#     weekend_evening_start = time(17, 0)  # 17:00
#     weekend_evening_end = time(20, 0)    # 20:00

#     if weekday <= 4:  # Thứ Hai - Thứ Sáu
#         if not (
#             (weekday_morning_start <= appointment_time <= weekday_morning_end) or
#             (weekday_evening_start <= appointment_time <= weekday_evening_end)
#         ):
#             raise ValueError(
#                 f"Giờ hẹn ({appointment_time}) phải từ 11:00-13:00 hoặc 17:00-20:00 vào các ngày trong tuần."
#             )
#     else:  # Thứ Bảy - Chủ Nhật
#         if not (
#             (weekend_morning_start <= appointment_time <= weekend_morning_end) or
#             (weekend_evening_start <= appointment_time <= weekend_evening_end)
#         ):
#             raise ValueError(
#                 f"Giờ hẹn ({appointment_time}) phải từ 08:00-13:00 or 17:00-20:00 vào cuối tuần."
#             )

#     return appointment_time


