from typing import Any, Callable
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, class_mapper
from starlette.concurrency import run_in_threadpool
from inspect import iscoroutinefunction
from app.auth.patients.jwt_handler import verify_patient_token, TokenExpiredError, TokenInvalidError
from app.patients.models import Patient

def to_dict(obj):   # Chuyển SQLAlchemy model thành dict
    return {c.key: getattr(obj, c.key) for c in class_mapper(obj.__class__).columns}

def patient_protected_route() -> Callable:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                token = (kwargs.get("CREDENTIALS") or "").credentials
                db: Session = kwargs.get("DB")
                payload = verify_patient_token(token)
                current_patient = db.query(Patient).filter(
                    Patient.id == payload.get("id"),
                    Patient.deleted_at.is_(None)
                ).first()
                if not current_patient:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Patient not found",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                kwargs["CURRENT_PATIENT"] = current_patient
                if iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return await run_in_threadpool(func, *args, **kwargs)
            except TokenExpiredError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except TokenInvalidError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=str(e),
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return wrapper
    return decorator