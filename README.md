# Love Emotion Web 💕

Ứng dụng web phân tích cảm xúc trong các cuộc trò chuyện tình yêu sử dụng AI.

## Tính năng

- 🎯 Phân tích cảm xúc từ tin nhắn tiếng Việt
- 💬 Đề xuất câu trả lời phù hợp
- 📊 Biểu đồ cảm xúc chi tiết
- 📝 Lưu lịch sử phân tích
- 👤 Quản lý profile người dùng và người yêu
- 🔒 Bảo mật và riêng tư

## Công nghệ

- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **Backend:** FastAPI, Python, SQLAlchemy
- **AI Service:** FastAPI, Python, NLP
- **Database:** PostgreSQL
- **Authentication:** JWT

## Cấu trúc dự án

```
love-emotion-web/
├── frontend/          # Next.js frontend
├── backend/           # FastAPI backend API
├── ai-service/        # AI emotion analysis service
├── database/          # Database schema & migrations
├── docs/              # Documentation
└── README.md
```

## Quick Start

### Yêu cầu

- Python 3.10 hoặc 3.11 (⚠️ KHÔNG dùng 3.13)
- Node.js 18+
- PostgreSQL 14+ (optional)

### Setup nhanh với scripts

```powershell
# Setup Backend
.\setup-backend.ps1

# Setup AI Service  
.\setup-ai-service.ps1

# Setup Frontend
.\setup-frontend.ps1
```

### Hoặc setup thủ công

Xem hướng dẫn chi tiết trong [SETUP.md](SETUP.md)

## Chạy ứng dụng

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

## Truy cập

- 🌐 Frontend: http://localhost:3000
- 📡 Backend API: http://localhost:8000/docs
- 🤖 AI Service: http://localhost:8001/docs

## Lỗi thường gặp

### Python 3.13 không tương thích
Dùng Python 3.10 hoặc 3.11

### psql không tìm thấy
Cài đặt PostgreSQL và thêm vào PATH

### uvicorn không tìm thấy
Đảm bảo đã activate virtual environment

Xem thêm trong [SETUP.md](SETUP.md)

## Documentation

- [Setup Guide](SETUP.md) - Hướng dẫn cài đặt chi tiết
- [Backend README](backend/README.md) - Backend API documentation
- [AI Service README](ai-service/README.md) - AI service documentation
- [Database README](database/README.md) - Database schema & migrations

## License

MIT License
