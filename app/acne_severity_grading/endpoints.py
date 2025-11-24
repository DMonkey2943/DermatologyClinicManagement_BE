from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from app.acne_severity_grading.ai_model import acne_classifier
import os
from pathlib import Path

from app.core.response import ResponseBase

router = APIRouter(
    prefix="/ai-predict-acne-severity",    # Tất cả endpoint sẽ có prefix /users
    tags=["ai-predict-acne-severity"],      # Nhóm trong Swagger docs
    responses={404: {"description": "Not found"}}  # Response chung cho 404
)

@router.post("/")
async def predict_acne(file: UploadFile = File(...)):
    # Đọc bytes của ảnh
    image_bytes = await file.read()
    # Dự đoán
    result = acne_classifier.predict(image_bytes)
    return {"Severity": result}


# Đường dẫn thư mục static (có thể lấy từ env để linh hoạt)
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # root project
STATIC_DIR = BASE_DIR 

@router.post("/from-image-path", response_model=ResponseBase)
async def predict_acne_from_path(image_path: str = Body(..., embed=True)):
    """
    Nhận image_path từ FE (đúng như lưu trong DB)
    Ví dụ: "/static/uploads/skin-images/de1ceff3-..._FRONT_....png"
    """
    # Ghép thành đường dẫn thực tế trên server
    file_path = STATIC_DIR / image_path.lstrip("/")  # bỏ / đầu nếu có

    # Kiểm tra file có tồn tại không
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Ảnh không tồn tại: {file_path}"
        )
    
    if not file_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Đường dẫn không phải là file"
        )

    try:
        # Đọc file ảnh dưới dạng bytes
        with open(file_path, "rb") as f:
            image_bytes = f.read()

        # Chạy model AI
        severity = acne_classifier.predict(image_bytes)

        # Có thể map lại tên cho đẹp hơn
        severity_map = {
            # "no_acne": "Không có mụn",
            "Mild": "Nhẹ",
            "Moderate": "Trung bình",
            "Severe": "Nặng",
            "Very Severe": "Rất nặng",
        }
        display_severity = severity_map.get(severity, severity)

        result = {
            "image_path": image_path,
            "severity": severity,                    # giá trị gốc từ model
            "severity_display": display_severity,    # hiển thị tiếng Việt
            "message": f"Phát hiện: {display_severity}"
        }
        return ResponseBase(message="Đánh giá mức độ nghiêm trọng của mụn với AI thành công", data=result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi xử lý ảnh AI: {str(e)}"
        )