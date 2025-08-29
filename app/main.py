from fastapi import FastAPI
from app.users.endpoints import router as users_router

app = FastAPI(title="Skin Clinic API")  # Tạo app FastAPI với title

app.include_router(users_router)    # Include routes từ users

@app.get("/")
def read_root():
    return {"message": "Welcome to Skin Clinic Backend"}