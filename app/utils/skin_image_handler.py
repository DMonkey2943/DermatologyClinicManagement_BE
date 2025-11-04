import os
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import shutil
import time

class SkinImageHandler:
    """Class xử lý upload và lưu trữ file ảnh da bệnh nhân"""
    
    # Cấu hình thư mục và file
    UPLOAD_DIR = "static/uploads/skin-images"  # Thư mục lưu ảnh
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB - Giới hạn kích thước file
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}  # Định dạng cho phép
    IMAGE_SIZE = (800, 800)  # Kích thước resize ảnh (chiều rộng, chiều cao)
    
    def __init__(self):
        """Khởi tạo và tạo thư mục upload nếu chưa tồn tại"""
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    
    def validate_image(self, file: UploadFile) -> None:
        """
        Kiểm tra tính hợp lệ của file ảnh
        
        Args:
            file: File upload từ request
            
        Raises:
            HTTPException: Nếu file không hợp lệ
        """
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có file nào được upload"
            )
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chỉ chấp nhận file ảnh: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File quá lớn. Kích thước tối đa: {self.MAX_FILE_SIZE / (1024*1024)}MB"
            )
    
    def generate_unique_filename(self, medical_record_id: str, image_type: str, original_filename: str) -> str:
        """
        Tạo tên file unique theo định dạng medical_record_id_image_type.extension
        
        Args:
            medical_record_id: ID của phiên khám
            image_type: Loại ảnh (LEFT, RIGHT, FRONT)
            original_filename: Tên file gốc
            
        Returns:
            Tên file mới (ví dụ: 4faca6bd-feaf-4a62-88d4-73c797f5b9b2_LEFT.jpg)
        """
        # Lấy timestamp dạng mili-giây
        timestamp = int(time.time() * 1000)

        file_ext = os.path.splitext(original_filename)[1].lower()
        filename = f"{medical_record_id}_{image_type}_{timestamp}{file_ext}"
        return filename
    
    def resize_image(self, image_path: str) -> None:
        """
        Resize ảnh để tiết kiệm dung lượng và thống nhất kích thước
        
        Args:
            image_path: Đường dẫn đến file ảnh
        """
        try:
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")
                
                img.thumbnail(self.IMAGE_SIZE, Image.Resampling.LANCZOS)
                img.save(image_path, optimize=True, quality=85)
                
        except Exception as e:
            if os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lỗi khi xử lý ảnh: {str(e)}"
            )
    
    async def save_upload_file(self, file: UploadFile, medical_record_id: str, image_type: str) -> str:
        """
        Lưu file upload vào server
        
        Args:
            file: File upload từ request
            medical_record_id: ID của phiên khám
            image_type: Loại ảnh (LEFT, RIGHT, FRONT)
            
        Returns:
            URL đường dẫn đến file ảnh (ví dụ: /static/uploads/skin-images/4faca6bd-feaf-4a62-88d4-73c797f5b9b2_LEFT.jpg)
        """
        self.validate_image(file)
        
        filename = self.generate_unique_filename(medical_record_id, image_type, file.filename)
        file_path = os.path.join(self.UPLOAD_DIR, filename)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # self.resize_image(file_path)
            
            return f"/{file_path.replace(os.sep, '/')}"
            
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi lưu file: {str(e)}"
            )
        finally:
            file.file.close()
    
    async def delete_file(self, file_url: Optional[str]) -> None:
        """
        Xóa file ảnh khỏi server
        
        Args:
            file_url: URL của file cần xóa (ví dụ: /static/uploads/skin-images/abc123.jpg)
        """
        if not file_url:
            return
        
        file_path = file_url.lstrip("/")
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Lỗi khi xóa file {file_path}: {str(e)}")

# Tạo instance để sử dụng trong toàn bộ app
skin_image_handler = SkinImageHandler()