import re
from datetime import date
from typing import Any
from app.utils.helper import raise_validation_error

# Regex chính xác theo yêu cầu (các đầu số Việt Nam bạn đưa)
PHONE_PATTERN = re.compile(
    r'^(032|033|034|035|036|037|038|039|096|097|098|086|083|084|085|081|082|088|091|094|070|079|077|076|078|090|093|089|056|058|092|059|099)[0-9]{7}$'
)

# Password: min 8, ít nhất 1 số, 1 chữ hoa, 1 chữ thường, 1 ký tự đặc biệt
PASSWORD_PATTERN = re.compile(
    r'^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$'
)


def validate_dob_at_least_18(value: Any) -> Any:
    if value is None:
        return value
    if not isinstance(value, (date,)):
        raise ValueError("Ngày sinh không hợp lệ")
    today = date.today()
    if value > today:
        raise ValueError("Ngày sinh không hợp lệ")
    # tính tuổi chính xác
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValueError("Người dùng phải từ 18 tuổi trở lên")
    return value

def validate_valid_dob(value: Any) -> Any:
    if value is None:
        return value
    if not isinstance(value, (date,)):
        raise ValueError("Ngày sinh không hợp lệ")
    today = date.today()
    if value > today:
        raise ValueError("Ngày sinh không hợp lệ")



def validate_phone_number(value: Any) -> str:
    if value is None:
        return value
    if not isinstance(value, str):
        raise ValueError("Số điện thoại không hợp lệ")
    if not PHONE_PATTERN.match(value):
        raise ValueError("Số điện thoại không hợp lệ")
    return value


def validate_password(value: Any) -> str:
    if value is None:
        return value
    if not isinstance(value, str):
        raise ValueError("Mật khẩu có dữ liệu không hợp lệ")
    if len(value) < 8:
        # Mình trả message cụ thể cho min
        raise ValueError("Mật khẩu phải từ 8 ký tự trở lên")
    # if not PASSWORD_PATTERN.match(value):
    #     # Một thông báo chung, bạn có thể tách ra chi tiết hơn nếu muốn
    #     raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt")
    return value


# MULTIPART/FORM-DATA
def validate_dob_at_least_18_form_data(value: Any) -> Any:
    if value is None:
        return value
    if not isinstance(value, (date,)):
        raise_validation_error("dob", "Ngày sinh không hợp lệ")
    today = date.today()
    if value > today:
        raise_validation_error("dob", "Ngày sinh không hợp lệ")
    # tính tuổi chính xác
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise_validation_error("dob", "Người dùng phải từ 18 tuổi trở lên")
    return value

def validate_valid_dob_form_data(value: Any) -> Any:
    if value is None:
        return value
    if not isinstance(value, (date,)):
        raise_validation_error("dob", "Ngày sinh không hợp lệ")
    today = date.today()
    if value > today:
        raise_validation_error("dob", "Ngày sinh không hợp lệ")

def validate_phone_number_form_data(value: Any) -> str:
    if value is None:
        return value
    if not isinstance(value, str):
        raise_validation_error("phone_number","Số điện thoại không hợp lệ")
    if not PHONE_PATTERN.match(value):
        raise_validation_error("phone_number","Số điện thoại không hợp lệ")
    return value


def validate_password_form_data(value: Any) -> str:
    if value is None:
        return value
    if not isinstance(value, str):
        raise_validation_error("password","Mật khẩu có dữ liệu không hợp lệ")
    if len(value) < 8:
        # Mình trả message cụ thể cho min
        raise_validation_error("password","Mật khẩu phải từ 8 ký tự trở lên")
    # if not PASSWORD_PATTERN.match(value):
    #     # Một thông báo chung, bạn có thể tách ra chi tiết hơn nếu muốn
    #     raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa, 1 chữ thường, 1 số và 1 ký tự đặc biệt")
    return value

