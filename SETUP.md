# Love Emotion Web - Hướng dẫn Setup

## Yêu cầu hệ thống

- Python 3.10 hoặc 3.11 (KHÔNG dùng 3.13)
- Node.js 18+ và npm
- PostgreSQL 14+ (optional - có thể setup sau)

## 1. Setup Backend

```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt venv
venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server (không cần database ngay)
uvicorn app.main:app --reload --port 8000
```

Backend sẽ chạy tại: http://localhost:8000

## 2. Setup AI Service

```bash
cd ai-service

# Tạo virtual environment
python -m venv venv

# Kích hoạt venv
venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
uvicorn app.main:app --reload --port 8001
```

AI Service sẽ chạy tại: http://localhost:8001

## 3. Setup Frontend

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

## 4. Setup Database (Optional)

### Cài đặt PostgreSQL

1. Tải PostgreSQL từ: https://www.postgresql.org/download/windows/
2. Cài đặt và nhớ password cho user `postgres`
3. Thêm PostgreSQL vào PATH:
   - Mặc định: `C:\Program Files\PostgreSQL\16\bin`

### Tạo Database

```bash
# Mở PowerShell mới sau khi cài PostgreSQL
psql -U postgres

# Trong psql console:
CREATE DATABASE loveemotion;
\q
```

### Chạy Migrations

```bash
# Chạy schema
psql -U postgres -d loveemotion -f database/schema.sql

# Hoặc chạy từng migration
psql -U postgres -d loveemotion -f database/migrations/001_create_users.sql
psql -U postgres -d loveemotion -f database/migrations/002_create_profiles.sql
psql -U postgres -d loveemotion -f database/migrations/003_create_partner_profiles.sql
psql -U postgres -d loveemotion -f database/migrations/004_create_preferences.sql
psql -U postgres -d loveemotion -f database/migrations/005_create_analysis_sessions.sql

# Seed data (optional)
psql -U postgres -d loveemotion -f database/seed.sql
```

### Cập nhật Backend .env

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/loveemotion
```

## Lỗi thường gặp

### 1. Python 3.13 không tương thích
**Lỗi:** `numpy==1.26.0` không tìm thấy

**Giải pháp:** Dùng Python 3.10 hoặc 3.11
```bash
python --version  # Kiểm tra version
```

### 2. psycopg2-binary lỗi build
**Giải pháp:** Đã thay bằng `asyncpg` trong requirements.txt

### 3. psql không tìm thấy
**Giải pháp:** 
- Cài đặt PostgreSQL
- Thêm `C:\Program Files\PostgreSQL\16\bin` vào PATH
- Khởi động lại PowerShell

### 4. uvicorn không tìm thấy
**Giải pháp:** Đảm bảo đã activate virtual environment
```bash
venv\Scripts\activate
pip install uvicorn
```

## Chạy toàn bộ hệ thống

Mở 3 terminal riêng biệt:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - AI Service:**
```bash
cd ai-service
venv\Scripts\activate
uvicorn app.main:app --reload --port 8001
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

## Kiểm tra

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs
- AI Service: http://localhost:8001/docs

## Lưu ý

- Database là optional, các service vẫn chạy được mà không cần database
- Có thể setup database sau khi đã test các service
- Nếu không dùng database, comment out các route cần database trong backend
