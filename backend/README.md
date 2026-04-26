# Love Emotion Backend

Backend FastAPI cho Love Emotion Web.

## Công nghệ

- FastAPI
- Pydantic
- Uvicorn
- Pytest

Database thật chưa bắt buộc. Các module Profile, History và Consent hiện dùng in-memory store để phát triển sau MVP.

## Cài đặt

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Chạy server

```powershell
uvicorn app.main:app --reload --port 8000
```

API chạy tại `http://localhost:8000`.

## Endpoint chính

- `GET /health`
- `GET /api/health`
- `POST /api/analyze`
- `GET|POST|DELETE /api/profile`
- `GET /api/history`
- `GET|DELETE /api/history/{id}`
- `DELETE /api/history`
- `GET|POST /api/consent`
- `DELETE /api/user-data`

Swagger UI: `http://localhost:8000/docs`

## Quy tắc lưu dữ liệu

- Không lưu nội dung chat mặc định.
- `save_result=true` chỉ lưu kết quả tổng hợp.
- `save_input=true` mới lưu `chat_text`.
- `history_enabled=false` trong consent sẽ chặn lưu lịch sử.

## Test

```powershell
python -m pytest tests
```
