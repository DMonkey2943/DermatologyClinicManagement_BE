from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """
    Lớp Settings kế thừa BaseSettings để quản lý cấu hình ứng dụng
    Sử dụng pydantic-settings để tự động load từ environment variables
    """
    
    # Database configuration
    database_url: str = Field(..., env="DATABASE_URL")
    postgres_user: str = Field(..., env="POSTGRES_USER")
    postgres_password: str = Field(..., env="POSTGRES_PASSWORD") 
    postgres_db: str = Field(..., env="POSTGRES_DB")
    postgres_host: str = Field(default="localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, env="POSTGRES_PORT")
    
    # JWT configuration
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # App configuration
    app_name: str = Field(default="Acne Clinic API", env="APP_NAME")
    debug: bool = Field(default=False, env="DEBUG")
    
    class Config:
        """Cấu hình để load từ file .env"""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Singleton pattern - chỉ tạo một instance duy nhất
settings = Settings()