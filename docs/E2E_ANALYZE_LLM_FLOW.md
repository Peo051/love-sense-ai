# E2E Analyze LLM Flow - Hướng dẫn Test

## Tổng quan

Tài liệu này mô tả luồng phân tích cảm xúc end-to-end từ frontend → backend → LLM service → safety filter → frontend hiển thị kết quả.

## Kiến trúc luồng

```
Frontend (/analyze)
    ↓ POST /api/analyze
Backend (FastAPI)
    ↓ preprocess_text()
    ↓ SafetyFilter.is_safe()
    ↓ AIService.analyze_emotion()
        ↓ (if LLM_MOCK_MODE=true) → mock response
        ↓ (if LLM_MOCK_MODE=false) → OpenAICompatibleLLMClient
            ↓ POST {LLM_BASE_URL}/chat/completions
9Router / LLM Provider
    ↓ JSON response
Backend
    ↓ _parse_response() + _normalize_result()
    ↓ (optional) save to history
    ↓ return AnalyzeResponse
Frontend
    ↓ Display result in AnalysisResultPanel
```

## Cấu hình Backend

### File: `backend/.env`

```env
# Application
APP_ENV=development
FRONTEND_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/loveemotion

# AI Service
AI_SERVICE_URL=http://localhost:8001

# LLM Configuration
LLM_PROVIDER=9router
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=
LLM_MODEL=api_models_all
LLM_MOCK_MODE=true
LLM_TIMEOUT_SECONDS=30.0

# Security
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000
```

### Chế độ hoạt động

1. **Mock Mode (mặc định)**: `LLM_MOCK_MODE=true`
   - Backend trả về mock response dựa trên keyword matching
   - Không cần 9Router hoặc API key
   - Dùng cho automated tests và development

2. **Real LLM Mode**: `LLM_MOCK_MODE=false`
   - Backend gọi LLM thật qua 9Router
   - Cần cấu hình đầy đủ: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`
   - Dùng cho manual testing và production

## Test với 9Router Local

### Bước 1: Cài đặt và chạy 9Router

```bash
# Tải 9Router từ https://github.com/9router/9router
# Hoặc cài đặt theo hướng dẫn của 9Router

# Chạy 9Router local trên port 20128
9router --port 20128
```

### Bước 2: Cấu hình Backend

Cập nhật `backend/.env`:

```env
LLM_PROVIDER=9router
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=
LLM_MODEL=api_models_all
LLM_MOCK_MODE=false
```

**⚠️ Lưu ý bảo mật:**
- Không commit file `.env` vào git
- Không hard-code API key trong code
- File `.env` đã được thêm vào `.gitignore`

### Bước 3: Chạy Backend

```bash
cd backend

# Kích hoạt virtual environment (Windows)
.\venv\Scripts\Activate.ps1

# Chạy backend server
uvicorn app.main:app --reload --port 8000
```

### Bước 4: Chạy Frontend

```bash
cd frontend

# Cài đặt dependencies (nếu chưa)
npm install

# Chạy development server
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

### Bước 5: Test E2E Flow

1. Mở trình duyệt: http://localhost:3000/analyze

2. Nhập đoạn chat mẫu:
   ```
   Em sao vậy?
   Không sao.
   Anh thấy em hơi lạ.
   Em mệt thôi.
   ```

3. Nhập bối cảnh cá nhân hóa:
   ```
   Người yêu thường im lặng khi mệt, không thích bị hỏi dồn.
   ```

4. Click "Phân tích"

5. Kiểm tra kết quả hiển thị:
   - ✅ `overall_emotion`: Cảm xúc tổng quan
   - ✅ `confidence`: Độ tin cậy (%)
   - ✅ `emotion_distribution`: Phân bố cảm xúc (bar chart)
   - ✅ `summary`: Tóm tắt phân tích
   - ✅ `context_note`: Ghi chú theo bối cảnh
   - ✅ `suggested_reply`: Gợi ý phản hồi
   - ✅ `warning`: Cảnh báo an toàn

### Bước 6: Test Error Handling

#### Test 1: LLM không khả dụng

```bash
# Tắt 9Router
# Hoặc đặt LLM_BASE_URL sai
```

**Kết quả mong đợi:**
- Frontend hiển thị error message: "Không thể phân tích đoạn chat lúc này."
- Backend trả HTTP 502 với detail: "LLM provider chưa sẵn sàng."

#### Test 2: LLM timeout

```bash
# Đặt LLM_TIMEOUT_SECONDS=1 trong .env
```

**Kết quả mong đợi:**
- Frontend hiển thị error message
- Backend log timeout error

#### Test 3: LLM trả JSON không hợp lệ

**Kết quả mong đợi:**
- Backend normalize response hoặc trả fallback
- Frontend vẫn hiển thị được kết quả an toàn

## Chạy Automated Tests

### Backend Tests

```bash
cd backend
.\venv\Scripts\python.exe -m pytest tests -v
```

**Test coverage:**
- ✅ Mock mode (default)
- ✅ Real LLM mode (with mocked httpx)
- ✅ LLM configuration validation
- ✅ Warning message normalization
- ✅ Error handling

### Frontend Tests

```bash
cd frontend
npm test
```

### TypeScript Type Check

```bash
cd frontend
npm run typecheck
```

### Production Build

```bash
cd frontend
npm run build
```

## Response Schema

### AnalyzeResponse

```typescript
interface AnalyzeResponse {
  overall_emotion: string;        // "mệt mỏi / né tránh nhẹ"
  confidence: number;             // 0.0 - 1.0
  emotion_distribution: {         // Tổng = 1.0
    [emotion: string]: number;    // 0.0 - 1.0
  };
  summary: string;                // Tóm tắt phân tích
  context_note: string;           // Ghi chú theo bối cảnh
  suggested_reply: string;        // Gợi ý phản hồi
  warning: string;                // Cảnh báo an toàn
}
```

### Example Response

```json
{
  "overall_emotion": "mệt mỏi / né tránh nhẹ",
  "confidence": 0.72,
  "emotion_distribution": {
    "mệt_mỏi": 0.35,
    "né_tránh": 0.25,
    "buồn": 0.20,
    "trung_lập": 0.20
  },
  "summary": "Đoạn chat có thể cho thấy người kia đang mệt hoặc chưa muốn trao đổi nhiều. Không đủ dữ liệu để kết luận chắc chắn cảm xúc thật sự.",
  "context_note": "Nếu người này thường im lặng khi mệt, nên phản hồi nhẹ nhàng thay vì hỏi dồn.",
  "suggested_reply": "Anh hiểu rồi, em nghỉ một chút nha. Khi nào em muốn nói thì anh vẫn ở đây nghe em.",
  "warning": "Kết quả chỉ là tham khảo, không thay thế việc hỏi thăm trực tiếp."
}
```

## Safety Features

### 1. Input Validation
- Preprocess text (remove extra whitespace, normalize)
- Safety filter (block inappropriate content)
- Max length: 8000 characters

### 2. LLM Response Validation
- JSON schema validation với Pydantic
- Normalize confidence (0.0 - 1.0)
- Normalize emotion distribution (0.0 - 1.0)
- Force warning message nếu LLM không trả đúng

### 3. Error Handling
- Graceful fallback khi LLM lỗi
- User-friendly error messages
- No sensitive data in error logs

### 4. Privacy
- Không lưu chat text mặc định
- Chỉ lưu khi user đồng ý rõ ràng
- `.env` file được gitignore

## Troubleshooting

### Backend không kết nối được 9Router

**Triệu chứng:**
```
LLMClientError: Không thể kết nối LLM provider.
```

**Giải pháp:**
1. Kiểm tra 9Router đang chạy: `curl http://localhost:20128/v1/models`
2. Kiểm tra `LLM_BASE_URL` trong `.env`
3. Kiểm tra firewall/antivirus

### Frontend không hiển thị kết quả

**Triệu chứng:**
- Spinner quay mãi
- Không có error message

**Giải pháp:**
1. Mở DevTools → Network tab
2. Kiểm tra request `/api/analyze`
3. Kiểm tra backend logs
4. Kiểm tra CORS settings

### Tests fail với "ModuleNotFoundError"

**Triệu chứng:**
```
ModuleNotFoundError: No module named 'sqlalchemy'
```

**Giải pháp:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\venv\Scripts\python.exe -m pytest tests -v
```

## Checklist trước khi commit

- [ ] Backend tests pass: `pytest tests -v`
- [ ] Frontend tests pass: `npm test`
- [ ] TypeScript check pass: `npm run typecheck`
- [ ] Frontend build pass: `npm run build`
- [ ] `.env` không được commit
- [ ] Không có API key hard-coded
- [ ] `LLM_MOCK_MODE=true` trong `.env.example`
- [ ] Documentation updated

## Next Steps

1. ✅ E2E flow hoàn chỉnh
2. ✅ Mock mode cho automated tests
3. ✅ Real LLM mode cho manual testing
4. ✅ Error handling và fallback
5. ✅ Safety validation
6. 🔄 Performance monitoring
7. 🔄 Rate limiting
8. 🔄 Caching strategy
9. 🔄 A/B testing framework
10. 🔄 Analytics integration
