# Love Emotion Backend

Backend API cho ứng dụng Love Emotion.

## Công nghệ

- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic

## Cài đặt

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

## Chạy server

```bash
uvicorn app.main:app --reload --port 8000
```

API sẽ chạy tại http://localhost:8000

## API Documentation

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## Cấu trúc

- `app/routes/` - API endpoints
- `app/schemas/` - Pydantic schemas
- `app/models/` - Database models
- `app/services/` - Business logic
- `app/core/` - Core configuration
- `app/utils/` - Utility functions
