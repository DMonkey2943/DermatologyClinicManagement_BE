from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from typing import Any, List

def raise_validation_error(field: str, message: str, type: str = "value_error"):
    """
    Ném lỗi validation giống hệt Pydantic để được xử lý bởi exception handler.
    """
    error = {
        "type": type,
        "loc": ("body", field),  # giống Pydantic: loc[0] = "body", loc[1] = field_name
        "msg": f"Value error, {message}",
        "input": None,
        "ctx": {"error": {}}  # có thể thêm ctx nếu cần
    }
    raise RequestValidationError([error])