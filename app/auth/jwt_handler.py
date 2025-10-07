import json
import jwt
from datetime import datetime, timedelta
from datetime import timezone
from typing import Optional
from fastapi import HTTPException, status

from pydantic import BaseModel

from app.core.config import settings
from app.users.models import User

ALGORITHM = settings.algorithm
SECRET_KEY = settings.secret_key
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.access_token_expire_minutes)
REFRESH_TOKEN_EXPIRE_DAYS = int(settings.refresh_token_expire_days)

def create_access_token(data_model: BaseModel, expires_delta: Optional[timedelta] = None) -> str:
    """"Tạo JWT access token
    Args:
        data_model: Pydantic model chứa dữ liệu payload
        expires_delta: Thời gian hết hạn tùy chỉnh (nếu không truyền sẽ dùng mặc định)
    Returns: JWT access token string"""
    json_str = data_model.model_dump_json() # Chuyển model thành JSON string
    to_encode = json.loads(json_str) # Chuyển JSON string thành dict
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta # Nếu có truyền thời gian hết hạn tùy chỉnh
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire}) # Thêm thời gian hết hạn vào payload

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Mã hóa JWT
    return encoded_jwt


def create_refresh_token(data_model: BaseModel) -> str:
    """Tạo JWT refresh token
    Args:
        data_model: Pydantic model chứa dữ liệu payload
    Returns: JWT refresh token string"""
    json_str = data_model.model_dump_json()  
    to_encode = json.loads(json_str)
    
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class TokenExpiredError(Exception):
    """Exception cho token hết hạn."""
    pass

class TokenInvalidError(Exception):
    """Exception cho token không hợp lệ."""
    pass

def verify_token(token: str) -> dict:
    """"Xác thực và giải mã JWT token
    Args:
        token: JWT token string
    Returns: Payload của token dưới dạng dict nếu hợp lệ, ngược lại raise Exception"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # Giải mã token
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token expired") # Token hết hạn
    except jwt.PyJWTError:
        raise TokenInvalidError("Token invalid") # Token không hợp lệ

def get_user_id_from_token(token: str) -> int:
    """Lấy user_id từ JWT token
    Args:
        token: JWT token string
    Returns: user_id nếu token hợp lệ"""
    try:
        payload = verify_token(token)
        user_id = payload.get("id")  # Giả sử bạn lưu user id trong payload
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

