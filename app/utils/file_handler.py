import os
import time
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import shutil
from datetime import datetime

class FileHandler:
    """Class xử lý upload và lưu trữ file ảnh"""
    
    # Cấu hình thư mục và file
    UPLOAD_DIR = "static/uploads/avatars"  # Thư mục lưu ảnh đại diện
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB - Giới hạn kích thước file
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}  # Định dạng cho phép
    IMAGE_SIZE = (500, 500)  # Kích thước resize ảnh (chiều rộng, chiều cao)
    
    def __init__(self):
        """Khởi tạo và tạo thư mục upload nếu chưa tồn tại"""
        # Tạo thư mục uploads/avatars nếu chưa có
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    
    def validate_image(self, file: UploadFile) -> None:
        """
        Kiểm tra tính hợp lệ của file ảnh
        
        Args:
            file: File upload từ request
            
        Raises:
            HTTPException: Nếu file không hợp lệ
        """
        # Kiểm tra file có tồn tại không
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không có file nào được upload"
            )
        
        # Lấy phần mở rộng của file (ví dụ: .jpg, .png)
        file_ext = os.path.splitext(file.filename)[1].lower()
        
        # Kiểm tra định dạng file có được phép không
        if file_ext not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Chỉ chấp nhận file ảnh: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        # Kiểm tra kích thước file
        file.file.seek(0, 2)  # Di chuyển con trỏ đến cuối file
        file_size = file.file.tell()  # Lấy vị trí hiện tại = kích thước file
        file.file.seek(0)  # Đưa con trỏ về đầu file
        
        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File quá lớn. Kích thước tối đa: {self.MAX_FILE_SIZE / (1024*1024)}MB"
            )
    
    def generate_unique_filename(self, original_filename: str) -> str:
        """
        Tạo tên file unique để tránh trùng lặp
        
        Args:
            original_filename: Tên file gốc
            
        Returns:
            Tên file mới với UUID (ví dụ: abc123-456def.jpg)
        """
         # Lấy timestamp dạng mili-giây
        timestamp = int(time.time() * 1000)

        # Lấy tên gốc và phần mở rộng
        original_name, ext = os.path.splitext(original_filename)

        # Chuẩn hóa tên gốc: bỏ khoảng trắng, ký tự đặc biệt
        safe_name = original_name.replace(" ", "_")
        
        # Nối lại thành tên file unique
        filename = f"{timestamp}_{safe_name}{ext}"
        
        return filename
    
    def resize_image(self, image_path: str) -> None:
        """
        Resize ảnh để tiết kiệm dung lượng và thống nhất kích thước
        
        Args:
            image_path: Đường dẫn đến file ảnh
        """
        try:
            # Mở ảnh bằng PIL
            with Image.open(image_path) as img:
                # Chuyển sang RGB nếu ảnh có alpha channel (PNG)
                if img.mode in ("RGBA", "LA", "P"):
                    img = img.convert("RGB")
                
                # Resize ảnh với thuật toán LANCZOS (chất lượng cao)
                # thumbnail() giữ tỷ lệ ảnh, fit vào kích thước tối đa
                img.thumbnail(self.IMAGE_SIZE, Image.Resampling.LANCZOS)
                
                # Lưu lại ảnh đã resize, optimize=True để giảm dung lượng
                img.save(image_path, optimize=True, quality=85)
                
        except Exception as e:
            # Nếu lỗi, xóa file đã upload và báo lỗi
            if os.path.exists(image_path):
                os.remove(image_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Lỗi khi xử lý ảnh: {str(e)}"
            )
    
    async def save_upload_file(self, file: UploadFile) -> str:
        """
        Lưu file upload vào server
        
        Args:
            file: File upload từ request
            
        Returns:
            URL đường dẫn đến file ảnh (ví dụ: /uploads/avatars/abc123.jpg)
        """
        # Bước 1: Validate file
        self.validate_image(file)
        
        # Bước 2: Tạo tên file unique
        filename = self.generate_unique_filename(file.filename)
        
        # Bước 3: Tạo đường dẫn đầy đủ đến file
        file_path = os.path.join(self.UPLOAD_DIR, filename)
        
        try:
            # Bước 4: Lưu file vào server
            # Mở file ở chế độ write binary
            with open(file_path, "wb") as buffer:
                # Copy nội dung từ file upload vào file trên server
                shutil.copyfileobj(file.file, buffer)
            
            # Bước 5: Resize ảnh để tối ưu
            # self.resize_image(file_path)
            
            # Bước 6: Trả về URL tương đối (dùng để lưu vào database)
            # Ví dụ: /uploads/avatars/abc123.jpg
            return f"/{file_path.replace(os.sep, '/')}"
            
        except Exception as e:
            # Nếu có lỗi, xóa file đã tạo (nếu có)
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Lỗi khi lưu file: {str(e)}"
            )
        finally:
            # Đóng file upload
            file.file.close()
    
    def delete_file(self, file_url: Optional[str]) -> None:
        """
        Xóa file ảnh khỏi server
        
        Args:
            file_url: URL của file cần xóa (ví dụ: /uploads/avatars/abc123.jpg)
        """
        if not file_url:
            return
        
        # Chuyển URL thành đường dẫn file trên server
        # Bỏ dấu "/" ở đầu để tạo relative path
        file_path = file_url.lstrip("/")
        
        # Xóa file nếu tồn tại
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Log lỗi nhưng không raise exception
                # Vì việc xóa file không quan trọng bằng cập nhật DB
                print(f"Lỗi khi xóa file {file_path}: {str(e)}")


# Tạo instance để sử dụng trong toàn bộ app
file_handler = FileHandler()