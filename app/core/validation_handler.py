from typing import Any, Dict, List
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# Optional: map internal field names -> user-friendly labels
FIELD_LABELS: Dict[str, str] = {
    "username": "Tên đăng nhập",
    "password": "Mật khẩu",
    "full_name": "Họ tên",
    "phone_number": "Số điện thoại",
    "email": "Email",    
    "gender": "Giới tính",
    "dob": "Ngày sinh",
    "role": "Vai trò",
    "name": "Tên",
    "price": "Giá",
    "stock_quantity": "Số lượng tồn kho",
    # thêm các field khác khi cần...
}

# Override messages cho một vài field / error_type nếu muốn
# Format: CUSTOM_MESSAGES[field][error_type] = "..." or callable(ctx)->str
# CUSTOM_MESSAGES: Dict[str, Dict[str, Any]] = {
    # ví dụ: override mặc định cho password khi missing
    # "password": {"value_error.missing": "Mật khẩu không được để trống"},
# }

def get_field_label(field_key: str) -> str:
    return FIELD_LABELS.get(field_key, field_key)


# def extract_field_from_loc(loc: List[Any]) -> str:
#     """
#     Lấy tên field từ loc; loại bỏ 'body', 'query', 'path', 'header' nếu có.
#     Nếu nested -> join bằng '.' (ví dụ items.0.name).
#     Args:
#         loc: List of location components from Pydantic error.
#     Returns:
#         Formatted field name as a string.
#     """
#     if not loc:
#         return ""
#     filtered = [str(x) for x in loc if x not in ("body", "query", "path", "header")]
#     return ".".join(filtered) if filtered else ".".join(map(str, loc))


def generate_default_message(err: Dict[str, Any]) -> str:
    """
    Sinh thông báo mặc định dựa trên err['type'] và ctx.
    Args:
        err: Pydantic error dictionary containing type, loc, ctx, and msg.
    Returns:
        Formatted error message in Vietnamese.
    """
    err_type = err.get("type", "")
    ctx = err.get("ctx", {}) or {}
    # raw_field = extract_field_from_loc(err.get("loc", []))
    raw_field = err['loc'][1]
    label = get_field_label(raw_field)

    # Handle specific error types
    error_messages = {
        "missing": f"{label} không được để trống",
        "string_too_short": f"{label} phải từ {ctx.get('min_length', 0)} ký tự", #constr(min_length=...)
        "string_too_long": f"{label} không được vượt quá {ctx.get('max_length', 0)} ký tự", #constr(max_length=...)
        "enum": f"{label} có dữ liệu không hợp lệ",
        "string_pattern_mismatch": f"{label} có định dạng không hợp lệ",
        "date_from_datetime_parsing": f"{label} có định dạng Ngày không hợp lệ",
        "float_parsing": f"{label} có định dạng không hợp lệ",
        "int_parsing": f"{label} có định dạng không hợp lệ",
        "int_from_float": f"{label} có định dạng không hợp lệ",
    }

    if err_type in error_messages:
        return error_messages[err_type]

    # Handle custom ValueError messages
    if err_type == "value_error":
        if(err['loc'][1] == "email"):
            return f"{label} không đúng định dạng"
        msg = err.get("msg", "")
        if msg:
            return msg.lstrip("Value error,").strip()
        return f"{label} không hợp lệ"

    # Fallback for unhandled errors
    msg = err.get("msg", f"{label} lỗi validation")
    return f"{err_type} - {msg}" 


def map_error_to_message(err: Dict[str, Any]) -> str:
    """
    Map error -> message with priority:
    1) CUSTOM_MESSAGES override for field + error type
    2) CUSTOM_MESSAGES override for field + 'default'
    3) default generator
    4) fallback to err['msg']
    Args:
        err: Pydantic error dictionary containing type, loc, ctx, and msg.
    Returns:
        Formatted error message in Vietnamese.
    """
    # loc = err.get("loc", [])
    # raw_field = extract_field_from_loc(loc)
    # 1) field-specific overrides
    # field_map = CUSTOM_MESSAGES.get(raw_field)
    # if field_map:
    #     # exact error type override
    #     err_type = err.get("type", "")
    #     if err_type in field_map:
    #         spec = field_map[err_type]
    #         return spec(err.get("ctx", {}) or {}) if callable(spec) else spec
    #     # default override for this field
    #     if "default" in field_map:
    #         spec = field_map["default"]
    #         return spec(err.get("ctx", {}) or {}) if callable(spec) else spec

    # 2) generate default message
    return generate_default_message(err)


def validation_handler_errors_out(exc: RequestValidationError):
    errors_out: List[Dict[str, str]] = []
    for err in exc.errors():
        # field = extract_field_from_loc(err.get("loc", []))
        # msg = map_error_to_message(err)
        errors_out.append({
            "field": err['loc'][1], 
            "msg": map_error_to_message(err)}
        )

    return errors_out

