# Testing Guide

## Frontend

Frontend dùng Vitest, jsdom và React Testing Library.

Chạy test:

```powershell
cd frontend
npm run test
```

Các case hiện có cho `/analyze`:

- Render form: ô nhập đoạn chat, ô nhập bối cảnh cá nhân hóa và nút phân tích.
- Validate input: chat rỗng thì không gọi API, hiển thị lỗi và UI không crash.
- Submit thành công: mock `fetch`, kiểm tra trạng thái loading và hiển thị kết quả phân tích.
- API lỗi: hiển thị thông báo lỗi thân thiện và giữ lại nội dung người dùng đã nhập.

Test không gọi API thật và không phụ thuộc vào CSS.

## Backend

Backend dùng Pytest và FastAPI TestClient.

Chạy test:

```powershell
cd backend
venv\Scripts\activate
venv\Scripts\python.exe -m pytest tests
```

Các nhóm test:

- Analyze API và safety filter.
- Profile API.
- Consent API.
- History API, bao gồm không lưu mặc định, lưu kết quả không kèm chat, lưu chat khi có đồng ý và xóa dữ liệu.
- Database config, fallback SQLite dev và normalize URL PostgreSQL/Supabase.
- User data isolation: user A không đọc/sửa/xóa profile, history, consent hoặc user data của user B.

Backend tests dùng SQLite in-memory qua `tests/conftest.py`, nên không phụ thuộc `DATABASE_URL` production.
