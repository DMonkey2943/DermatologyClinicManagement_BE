# Backend for Skin Clinic Management

## Setup
- Create venv: python -m venv venv
- Activate venv
- pip install -r requirements.txt
- Setup DB in .env
- Run migrations: alembic upgrade head
- Run app: uvicorn app.main:app --reload

## Structure
- app/: Core application code
- alembic/: Migrations