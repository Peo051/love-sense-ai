# Love Emotion Web

Love Emotion Web là web app hỗ trợ phân tích sắc thái cảm xúc trong đoạn hội thoại tình cảm. Ứng dụng chỉ phân tích nội dung người dùng nhập thủ công, không đọc trộm tin nhắn, không kết luận chắc chắn cảm xúc của người khác và không lưu nội dung chat mặc định.

## Hiện có

- Frontend Next.js: `/`, `/analyze`, `/profile`, `/history`, `/privacy`.
- Backend FastAPI: `/health`, `/api/analyze`, `/api/profile`, `/api/history`, `/api/consent`, `/api/user-data`.
- Mock AI response có cảnh báo an toàn.
- Hồ sơ cá nhân hóa và lịch sử phân tích dùng in-memory store cho giai đoạn sau MVP.
- Consent rõ ràng: lưu kết quả và lưu nội dung chat là hai lựa chọn riêng.
- Test frontend cho form `/analyze`.
- Test backend cho analyze, safety, profile, history và consent.

## Cấu trúc

```text
love-emotion-web/
├── frontend/      # Next.js + TypeScript + Tailwind CSS
├── backend/       # FastAPI + Pydantic
├── ai-service/    # Thử nghiệm AI service, chưa cần cho MVP
├── database/      # Schema/migrations chuẩn bị cho PostgreSQL
├── docs/          # Tài liệu dự án
└── README.md
```

## Chạy backend

```powershell
cd backend
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Kiểm tra: `http://localhost:8000/health`

## Chạy frontend

```powershell
cd frontend
npm install
npm run dev
```

Mở: `http://localhost:3000/analyze`

## Test

Backend:

```powershell
cd backend
venv\Scripts\activate
python -m pytest tests
```

Frontend:

```powershell
cd frontend
npm run test
npm run typecheck
npm run build
npm audit
```

## Tài liệu

- [Testing Guide](docs/TESTING.md)
- [Project Guide](docs/PROJECT_GUIDE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [Roadmap](docs/ROADMAP.md)
