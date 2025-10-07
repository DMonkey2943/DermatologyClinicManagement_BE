from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.dependencies import AuthCredentialDepend
from app.database import get_db
from app.users.schemas import UserLogin, UserResponse
from app.users.services import UserService
from app.auth.jwt_handler import create_access_token, create_refresh_token, verify_token, get_user_id_from_token
from app.core.response import ResponseBase
from app.users.schemas import UserTokenData, LoginResponseData, RefreshTokenData

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter(
    prefix="/auth",    # Tất cả endpoint sẽ có prefix /auth
    tags=["auth"],      # Nhóm trong Swagger docs
    responses={404: {"description": "Not found"}}  # Response chung cho 404
)  # Router cho grouping routes

# Cấu hình HTTPBearer cho Swagger
# security = HTTPBearer(
#     bearerFormat="JWT",
#     description="Enter JWT token"
# )

@router.post("/login", response_model=ResponseBase[LoginResponseData])
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_data    = user.model_dump() # Chuyển Pydantic model thành dict
    repo = UserService(db)  # Tạo repository instance    
    validated_user    = repo.validate_login(user_data)

    # if validated_user is None:
    #     raise HTTPException(status_code=401, detail="Invalid credentials")

    if validated_user:
        access_token    = create_access_token(validated_user)
        refresh_token   = create_refresh_token(validated_user)

        data_login = {"user": validated_user, "access_token": access_token, "refresh_token": refresh_token}
        return ResponseBase(message="Login successfully", data=data_login)


@router.post("/refresh")
def refresh_token(data: RefreshTokenData):
    try:
        payload = verify_token(data.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=403, detail="Invalid refresh token")
    
    token_data = UserTokenData(**payload)
    new_access_token = create_access_token(token_data)

    return {"access_token": new_access_token, "token_type": "bearer"}

@router.get("/me", response_model=ResponseBase[UserResponse])
def get_current_user(
    CREDENTIALS: AuthCredentialDepend,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    # Lấy token từ Authorization header
    token = CREDENTIALS.credentials
    
    # Lấy user_id từ token
    user_id = get_user_id_from_token(token)
    
    # Lấy thông tin user từ database
    user_service = UserService(DB)
    user = user_service.get_user_by_id(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Kiểm tra user có active không (nếu có field này)
    if hasattr(user, 'is_active') and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return ResponseBase(message="Lấy thông tin tài khoản thành công", data=user)  # Wrap response
