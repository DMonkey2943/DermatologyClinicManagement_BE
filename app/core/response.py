from typing import Generic, TypeVar, Optional, List, Dict, Any
from pydantic import BaseModel

T = TypeVar('T')  # Generic type cho data

class ResponseBase(BaseModel, Generic[T]):
    """
    Response cơ bản cho thành công.
    - success: Luôn là "True" (có thể override nếu cần).
    - message: Thông điệp tùy chọn (ví dụ: "User created successfully").
    - data: Dữ liệu chính (có thể là object, list, hoặc None).
    """
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    """
    Response cho thất bại.
    - success: Luôn là "False".
    - message: Thông điệp lỗi chính.
    - details: Chi tiết lỗi (có thể là dict, list, hoặc None cho các field cụ thể).
    """
    success: bool = False
    message: str
    details: Optional[Dict[str, Any] | List[Any] | str] = None

class PaginationMeta(BaseModel):
    """
    Metadata cho phân trang.
    """
    total: int  # Tổng số bản ghi
    page: int   # Trang hiện tại (bắt đầu từ 1)
    limit: int  # Số bản ghi mỗi trang
    total_pages: Optional[int] = None  # Tổng số trang (tùy chọn, có thể tính toán)

class PaginatedResponse(ResponseBase[List[T]]):
    """
    Response cho danh sách với phân trang, kế thừa từ ResponseBase.
    - data: List các items.
    - meta: Thông tin phân trang.
    """
    meta: Optional[PaginationMeta] = None