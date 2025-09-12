from typing import List, Any, Callable
from functools import wraps
from inspect import iscoroutinefunction

from fastapi import HTTPException, status
from starlette.concurrency import run_in_threadpool   # FastAPI sẵn có
from sqlalchemy.orm import Session, joinedload, class_mapper
import jwt
from app.auth.jwt_handler import verify_token
from app.users.models import UserRoleEnum, User
from sqlalchemy import and_
 
def to_dict(obj):   # Chuyển SQLAlchemy model thành dict
    return {c.key: getattr(obj, c.key) for c in class_mapper(obj.__class__).columns}


def protected_route(roles: List[UserRoleEnum]) -> Callable[[Callable[..., Any]], Callable[..., Any]]: 
    """
    Decorator cho phép gắn kiểm tra JWT + phân quyền vào cả endpoint sync và async.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)    # Giữ nguyên metadata của func gốc
        async def wrapper(*args, **kwargs):                 # wrapper luôn async
            try:
                # Lấy các dependency đã khai báo trong endpoint
                token = (kwargs.get("CREDENTIALS") or "").credentials
                db: Session = kwargs.get("DB")

                payload = verify_token(token)
                current_user = db.query(User)\
                                  .filter(and_(User.id == payload.get("id"), User.deleted_at.is_(None)))\
                                  .first()  # Lấy user từ DB
                
                if current_user is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                
                #if current_user is not None and current_user.intern_profile is not None:
                    #current_user.title = current_user.intern_profile.suggested_position

                kwargs["CURRENT_USER"] = current_user      # nhét vào kwargs để endpoint dùng

                if current_user is None or current_user.role not in roles:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Invalid system role!",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
 
                # Gọi endpoint gốc – sync hay async đều OK
                if iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return await run_in_threadpool(func, *args, **kwargs)

            except jwt.InvalidSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token signature",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return wrapper
    return decorator
