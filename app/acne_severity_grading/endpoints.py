from fastapi import APIRouter, UploadFile, File
from app.acne_severity_grading.ai_model import acne_classifier

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