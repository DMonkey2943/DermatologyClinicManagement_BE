from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.core.dependencies import AuthCredentialDepend
from app.database import get_db
from app.users.schemas import UserCreate, UserUpdate, UserResponse
from app.users.services import UserService
from app.core.authentication import protected_route
from app.users.models import UserRoleEnum as RoleEnum

router = APIRouter(
    prefix="/users",    # Tất cả endpoint sẽ có prefix /users
    tags=["users"],      # Nhóm trong Swagger docs
    responses={404: {"description": "Not found"}}  # Response chung cho 404
)  # Router cho grouping routes


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    CREDENTIALS: AuthCredentialDepend,
    user: UserCreate,                   # Request body sử dụng schema UserCreate
    DB: Session = Depends(get_db),       # Dependency injection cho database
    CURRENT_USER = None,
):
    """
    Tạo người dùng mới
    - Kiểm tra email và username đã tồn tại chưa
    - Tự động hash password trước khi lưu
    - Trả về thông tin user (không có password)
    """
    repo = UserService(DB)  # Tạo repository instance

    # Kiểm tra email đã tồn tại
    if repo.get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    # Kiểm tra username đã tồn tại
    if repo.get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username đã được sử dụng"
        )
    db_user = repo.create_user(user)
    return db_user


@router.get("/{user_id}", response_model=UserResponse)
def read_user(
    CREDENTIALS: AuthCredentialDepend,
    user_id: UUID, 
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    repo = UserService(DB)
    db_user = repo.get_user_by_id(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/", response_model=List[UserResponse])
@protected_route([RoleEnum.ADMIN])
def read_users(
    CREDENTIALS: AuthCredentialDepend,
    skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),     # Query parameter với validation
    limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Lấy danh sách người dùng với phân trang
    - skip: số bản ghi bỏ qua (mặc định 0)
    - limit: số bản ghi tối đa (mặc định 100, max 100)
    """
    repo = UserService(DB)
    users = repo.get_users(skip=skip, limit=limit)
    return users


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    CREDENTIALS: AuthCredentialDepend,
    user_id: UUID,
    user: UserUpdate,                   # Request body cho update
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Cập nhật thông tin người dùng
    - Chỉ cập nhật các trường được cung cấp
    - Trả về 404 nếu không tìm thấy user
    """
    repo = UserService(DB)
    db_user = repo.update_user(user_id=user_id, user_update=user)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    CREDENTIALS: AuthCredentialDepend,
    user_id: UUID,
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Xóa người dùng (soft delete)
    - Set deleted_at và is_active = False
    - Trả về 404 nếu không tìm thấy
    - Trả về 204 (No Content) nếu thành công
    """
    repo = UserService(DB)
    success = repo.delete_user(user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
