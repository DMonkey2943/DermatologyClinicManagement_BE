from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from app.core.dependencies import AuthCredentialDepend
from app.database import get_db
from app.users.schemas import UserCreate, UserUpdate, UserResponse
from app.users.services import UserService
from app.core.authentication import protected_route
from app.users.models import GenderEnum, UserRoleEnum as RoleEnum
from app.core.response import PaginationMeta, ResponseBase, PaginatedResponse
from app.users.validators import (
    validate_dob_at_least_18_form_data,
    validate_phone_number_form_data,
    validate_password_form_data,
)

router = APIRouter(
    prefix="/users",    # Tất cả endpoint sẽ có prefix /users
    tags=["users"],      # Nhóm trong Swagger docs
    responses={404: {"description": "Not found"}}  # Response chung cho 404
)  # Router cho grouping routes


@router.post("/", response_model=ResponseBase[UserResponse], status_code=status.HTTP_201_CREATED)
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
    return ResponseBase(message="User created successfully", data=db_user)

@router.post("/avatar", response_model=ResponseBase, status_code=status.HTTP_201_CREATED)
async def create_user_with_avatar(
    CREDENTIALS: AuthCredentialDepend,
    # Form data thay vì JSON body
    username: str = Form(..., min_length=4, max_length=50, pattern=r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'),
    full_name: str = Form(..., min_length=2, max_length=50),
    password: str = Form(...),
    dob: Optional[date] = Form(None),
    gender: Optional[GenderEnum] = Form(None),
    phone_number: Optional[str] = Form(None),
    email: EmailStr = Form(...),
    role: RoleEnum = Form(RoleEnum.STAFF),
    # File upload - optional
    avatar: Optional[UploadFile] = File(None),
    # Dependencies
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Tạo người dùng mới với avatar
    - Nhận form data + file upload
    - Upload avatar trước, sau đó tạo user với avatar_url
    """
    repo = UserService(DB)
    validate_dob_at_least_18_form_data(dob)
    validate_phone_number_form_data(phone_number)
    validate_password_form_data(password)
    
    # Kiểm tra email đã tồn tại
    if repo.get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    
    # Kiểm tra username đã tồn tại
    if repo.get_user_by_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username đã được sử dụng"
        )
    
    # Kiểm tra số điện thoại đã tồn tại
    if repo.get_user_by_phone_number(phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại đã được sử dụng"
        )
    
    # Tạo user schema với avatar_url
    user_data = UserCreate(
        username=username,
        password=password,
        full_name=full_name,
        email=email,
        phone_number=phone_number,
        dob=dob,
        gender=gender,
        role=role
    )
    
    # Tạo user trong database
    db_user = await repo.create_user_with_avatar(user_data, avatar)
    
    return ResponseBase(
        message="Tạo user thành công",
        data=UserResponse.model_validate(db_user)
    )


@router.get("/{user_id}", response_model=ResponseBase[UserResponse])
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
    return ResponseBase(message="User retrieved successfully", data=db_user)


@router.get("/", response_model=PaginatedResponse[UserResponse])
@protected_route([RoleEnum.ADMIN])
def read_users(
	CREDENTIALS: AuthCredentialDepend,
	skip: int = Query(0, ge=0, description="Số bản ghi bỏ qua"),
	limit: int = Query(100, ge=1, le=100, description="Số bản ghi tối đa"),
	q: Optional[str] = Query(None, description="Search query: tìm theo full_name (không phân biệt hoa thường) hoặc username hoặc phone_number"),
	DB: Session = Depends(get_db),
	CURRENT_USER = None,
):
    """
    Lấy danh sách người dùng với phân trang
    - skip: số bản ghi bỏ qua (mặc định 0)
    - limit: số bản ghi tối đa (mặc định 100, max 100)
    """
    repo = UserService(DB)
    users = repo.get_users(skip=skip, limit=limit, q=q)
    total = repo.count_users(q=q)
    page = (skip // limit) + 1
    total_pages = (total // limit) + (1 if total % limit else 0)
    meta = PaginationMeta(total=total, page=page, limit=limit, total_pages=total_pages)
    return PaginatedResponse(message="Users retrieved successfully", data=users, meta=meta)  # Wrap với pagination


@router.put("/{user_id}", response_model=ResponseBase[UserResponse])
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
    return ResponseBase(message="User updated successfully", data=db_user)

@router.put("/avatar/{user_id}", response_model=ResponseBase)
async def update_user(
    user_id: UUID,
    CREDENTIALS: AuthCredentialDepend,
    username: Optional[str] = Form(None, min_length=4, max_length=50, pattern=r'^[a-zA-Z0-9][a-zA-Z0-9_-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'),
    full_name: Optional[str] = Form(None, min_length=2, max_length=50),
    # password: Optional[str] = Form(None),
    dob: Optional[date] = Form(None),
    gender: Optional[GenderEnum] = Form(None),
    phone_number: Optional[str] = Form(None),
    email: Optional[EmailStr] = Form(None),
    role: Optional[RoleEnum] = Form(None),
    avatar: Optional[UploadFile] = File(None),
    DB: Session = Depends(get_db),
    CURRENT_USER = None,
):
    """
    Cập nhật thông tin người dùng, bao gồm avatar
    - Nhận form data + file upload
    - Nếu có avatar mới, xóa avatar cũ (nếu tồn tại) trước khi lưu avatar mới
    """
    repo = UserService(DB)
    
    # Kiểm tra user tồn tại
    db_user = repo.get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy người dùng"
        )
    
    # Validate dữ liệu đầu vào
    if dob:
        validate_dob_at_least_18_form_data(dob)
    if phone_number:
        validate_phone_number_form_data(phone_number)
    # if password:
    #     validate_password_form_data(password)
    
    # Kiểm tra email đã tồn tại (nếu cập nhật email)
    if email and email != db_user.email and repo.get_user_by_email(email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng"
        )
    
    # Kiểm tra username đã tồn tại (nếu cập nhật username)
    if username and username != db_user.username and repo.get_user_by_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username đã được sử dụng"
        )
    
    # Kiểm tra số điện thoại đã tồn tại (nếu cập nhật số điện thoại)
    if phone_number and phone_number != db_user.phone_number and repo.get_user_by_phone_number(phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Số điện thoại đã được sử dụng"
        )
    
    # Tạo user schema cho cập nhật
    user_data = UserUpdate(
        username=username or db_user.username,
        # password=password or db_user.password,
        full_name=full_name or db_user.full_name,
        email=email or db_user.email,
        phone_number=phone_number or db_user.phone_number,
        dob=dob or db_user.dob,
        gender=gender or db_user.gender,
        role=role or db_user.role
    )
    
    # Cập nhật user trong database
    updated_user = await repo.update_user_with_avatar(user_id, user_data, avatar)
    
    return ResponseBase(
        message="Cập nhật user thành công",
        data=UserResponse.model_validate(updated_user)
    )


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
