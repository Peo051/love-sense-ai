# Love Emotion Web - Documentation

## 📚 Available Documents

### Setup & Configuration
- **[SETUP.md](../SETUP.md)** - Hướng dẫn cài đặt và chạy dự án
  - Backend setup (Python, FastAPI)
  - Frontend setup (Next.js, TypeScript)
  - Testing instructions
  - LLM configuration (optional)

### E2E Flow & Testing
- **[E2E_ANALYZE_LLM_FLOW.md](E2E_ANALYZE_LLM_FLOW.md)** - Hướng dẫn chi tiết luồng phân tích E2E
  - Architecture diagram
  - Mock mode vs Real LLM mode
  - Testing with 9Router local
  - Error handling & troubleshooting
  - Response schema & safety features

- **[E2E_FLOW_REPORT.md](E2E_FLOW_REPORT.md)** - Báo cáo hoàn thành E2E flow
  - Branch information
  - Files changed
  - Test results
  - Security checklist
  - Commit details

- **[ANALYSIS_QUALITY_BENCHMARK.md](ANALYSIS_QUALITY_BENCHMARK.md)** - Synthetic regression benchmark for emotion analysis quality.
  - Expected/disallowed label checks
  - Confidence range checks
  - Safety note that benchmark cases are not ground truth

- **[PRIVACY_DESIGN.md](PRIVACY_DESIGN.md)** - Thiết kế consent, lưu/xóa dữ liệu và logging an toàn.

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Checklist biến môi trường, database, test/build và deploy demo.

## 🚀 Quick Start

### Development (Mock Mode)
```bash
# Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm run dev
```

### Testing with Real LLM (9Router)
```bash
# 1. Configure backend/.env
LLM_MOCK_MODE=false
LLM_BASE_URL=http://localhost:20128/v1
LLM_API_KEY=

# 2. Run 9Router
9router --port 20128

# 3. Run backend & frontend (same as above)
```

## 🧪 Testing

```bash
# Backend tests
cd backend
.\venv\Scripts\python.exe -m pytest tests -v

# Frontend tests
cd frontend
npm test
npm run typecheck
npm run build
```

## 🔒 Security

- ✅ `.env` file gitignored
- ✅ No API keys hard-coded
- ✅ Mock mode default for safe testing
- ✅ Privacy-first design

## 📖 More Information

For detailed information about specific topics, see the individual documentation files listed above.
