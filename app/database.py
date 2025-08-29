from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from app.core.config import settings

# Tạo logger để ghi log database
logger = logging.getLogger(__name__)

# Tạo engine - kết nối đến database
# echo=True để log tất cả SQL queries (chỉ dùng trong development)
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL queries khi debug=True
    pool_pre_ping=True,   # Kiểm tra connection trước khi sử dụng
    pool_recycle=300,     # Recycle connection sau 5 phút
)

# Tạo SessionLocal để tạo database sessions
SessionLocal = sessionmaker(
    autocommit=False,     # Không auto commit
    autoflush=False,      # Không auto flush
    bind=engine           # Bind với engine đã tạo
)

# Base class cho tất cả models
Base = declarative_base()

# Dependency để lấy session trong routes (sử dụng dependency injection)
def get_db():
    db = SessionLocal() # Tạo session mới
    try:
        yield db # Yield để sử dụng trong FastAPI Depends (dependency injection)
    finally:
        db.close() # Đóng session sau khi dùng



# Metadata để quản lý database schema
# metadata = MetaData()

# class DatabaseManager:
#     """
#     Database Manager class để quản lý kết nối database
#     Sử dụng Singleton pattern để đảm bảo chỉ có một instance
#     """
    
#     _instance = None
    
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(DatabaseManager, cls).__new__(cls)
#         return cls._instance
    
#     @staticmethod
#     def get_session() -> Generator[Session, None, None]:
#         """
#         Dependency để tạo database session cho mỗi request
#         Sử dụng context manager để đảm bảo session được đóng
#         """
#         session = SessionLocal()
#         try:
#             yield session
#         except Exception as e:
#             logger.error(f"Database session error: {e}")
#             session.rollback()
#             raise
#         finally:
#             session.close()
    
#     @staticmethod
#     def create_tables():
#         """Tạo tất cả tables trong database"""
#         try:
#             Base.metadata.create_all(bind=engine)
#             logger.info("Database tables created successfully")
#         except Exception as e:
#             logger.error(f"Error creating database tables: {e}")
#             raise
    
#     @staticmethod
#     def drop_tables():
#         """Xóa tất cả tables trong database"""
#         try:
#             Base.metadata.drop_all(bind=engine)
#             logger.info("Database tables dropped successfully")
#         except Exception as e:
#             logger.error(f"Error dropping database tables: {e}")
#             raise


# # Dependency để inject database session vào endpoints
# def get_db() -> Generator[Session, None, None]:
#     """Dependency function để sử dụng trong FastAPI endpoints"""
#     return DatabaseManager.get_session()