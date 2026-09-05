# Báo Cáo Gỡ Bỏ Domain Phân Tích Cảm Xúc Hẹn Hò (APT-004: Removed Domain)

Tài liệu này ghi nhận quá trình loại bỏ và cô lập domain phân tích cảm xúc tin nhắn tình cảm/hẹn hò khỏi backend hoạt động của hệ thống, nhằm chuẩn bị hạ tầng phục vụ dự án **Adaptive Programming Tutor (CodeSense AI)**.

---

## 1. Tóm Tắt Mục Tiêu & Kết Quả Đạt Được

- **Mục tiêu:**
  - Gỡ bỏ hoàn toàn logic nghiệp vụ tình cảm lãng mạn, các phân phối sắc thái cảm xúc, keyword matching hẹn hò, gợi ý câu trả lời làm lành/tán tỉnh, và các validator liên quan.
  - Bảo toàn 100% hạ tầng dùng chung (generic OpenAI-compatible LLM client, retry backoff, Vision OCR, Rate Limiter, Auth JWT/Firebase, Database connection & Session, Safety Filter, Consent & Privacy).
  - Deprecate endpoint `/api/analyze` một cách tường minh với mã trạng thái `410 Gone`.
  - Toàn bộ backend test suite (54/54 tests) và frontend test suite (24/24 tests) đều vượt qua.

---

## 2. Chi Tiết Các Thành Phần Đã Gỡ Bỏ Hoặc Cô Lập

### 2.1. Schemas & Models
| File | Trạng thái | Chi tiết gỡ bỏ |
| :--- | :--- | :--- |
| `backend/app/schemas/analyze_schema.py` | **Đã xóa hoàn toàn** | Đã loại bỏ `AnalyzeRequest`, `AnalyzeResponse`, `EmotionDistribution`, `EmotionCategory`, cùng các mô hình Pydantic phân tích sắc thái cảm xúc. |
| `backend/app/models/analysis_session.py` | **Giữ lại cấu trúc DB (cô lập)** | Giữ lại cấu trúc bảng database để không làm gãy migrations hiện tại và cascade delete của `/api/user-data`. `save_analysis` trong `db_store.py` được nới lỏng kiểu dữ liệu thành `Any` thay vì phụ thuộc schema cảm xúc. |

### 2.2. Logic Phân Tích & Prompts (AI Services)
| File | Trạng thái | Chi tiết thay đổi |
| :--- | :--- | :--- |
| `backend/app/services/ai_service.py` | **Tái cấu trúc (Refactored)** | Đã xóa bỏ toàn bộ từ khóa tình cảm (`affectionate_keywords`, `sulking_keywords`, `fatigue_keywords`, `cold_keywords`), hàm phân loại cảm xúc thủ công và bộ tạo phản hồi hòa giải. Chuyển thành `AIService` generic kết nối LLM client. |
| `backend/app/services/llm_client.py` | **Tái cấu trúc (Refactored)** | Loại bỏ phụ thuộc vào `SYSTEM_PROMPT` cảm xúc hẹn hò và `AnalyzeResponse`. Bổ sung method generic `chat_completion(messages, ...)` trả về response text thô hoặc cấu trúc JSON linh hoạt. |
| `backend/app/services/prompt_builder.py` | **Tái cấu trúc (Refactored)** | Xóa hàm `build_emotion_prompt`. Thay thế bằng `build_tutor_system_prompt` phục vụ hướng dẫn lập trình C# OOP. |
| `backend/app/services/analysis_policy.py` | **Đã xóa hoàn toàn** | Gỡ bỏ toàn bộ logic policy điều phối phân tích cảm xúc hẹn hò. |
| `backend/app/services/analysis_output_validator.py` | **Đã xóa hoàn toàn** | Gỡ bỏ các validator kiểm tra định dạng output cảm xúc, câu phản hồi tình cảm và lời khuyên hòa giải. |

### 2.3. Endpoints & Routes
| Endpoint | Phương thức | Trạng thái mới | Mô tả |
| :--- | :--- | :--- | :--- |
| `/api/analyze` | `POST`, `GET` | **Deprecated (HTTP 410 Gone)** | Trả về thông báo JSON: `{"detail": "The /api/analyze endpoint has been retired and replaced by the CodeSense AI Programming Tutor domain. Please use the new tutor APIs."}` |
| `/api/analyze/options` | `GET` | **Deprecated (HTTP 410 Gone)** | Endpoint tùy chọn phân tích cảm xúc cũ đã bị gỡ bỏ và trả về 410 Gone. |

### 2.4. Tests Đã Gỡ Bỏ & Tái Cấu Trúc
| Test File | Trạng thái | Lý do |
| :--- | :--- | :--- |
| `backend/tests/test_analysis_benchmark.py` | **Đã xóa** | Chứa 20+ test cases benchmark phân loại cảm xúc hẹn hò cũ (giận dỗi, ngọt ngào, mệt mỏi...). |
| `backend/tests/test_analysis_quality.py` | **Đã xóa** | Test chất lượng phân loại sắc thái cảm xúc và gợi ý phản hồi tình cảm. |
| `backend/tests/test_analysis_output_validator.py` | **Đã xóa** | Test validator cho schema output cảm xúc cũ. |
| `backend/tests/test_analyze.py` | **Cập nhật** | Chuyển sang xác minh mã `410 Gone` cho `/api/analyze` và kiểm tra liveness/readiness của service. |
| `backend/tests/test_analyze_rate_limit.py` | **Cập nhật** | Chuyển sang kiểm thử trực tiếp `InMemoryRateLimiter` (sliding window, max requests, header reset, IP/user isolation) mà không cần đi qua endpoint phân tích cảm xúc cũ. |
| `backend/tests/test_ai_service_llm.py` | **Cập nhật** | Kiểm thử generic `chat_completion`, xử lý mock mode, timeout, retry khi HTTP 503. |
| `backend/tests/test_auth_schema_errors.py` | **Cập nhật** | Kiểm thử fallback guest khi thiếu cột `users.firebase_uid` và xử lý dependency injection chuẩn. |
| `backend/tests/test_profile_history_consent.py` | **Cập nhật** | Tạo helper `seed_history_session` độc lập ghi trực tiếp vào test session, tách biệt hoàn toàn khỏi `/api/analyze`. |

---

## 3. Danh Sách Hạ Tầng Dùng Chung Được Bảo Toàn (Preserved Infrastructure)

Hệ thống giữ nguyên vẹn 100% các module hạ tầng cốt lõi để tái sử dụng trực tiếp cho **CodeSense AI**:

1. **Generic LLM Client (`backend/app/services/llm_client.py`):**
   - Hỗ trợ bất kỳ OpenAI-compatible LLM endpoint nào (OpenAI, OpenRouter, v.v.).
   - Cơ chế exponential backoff retry với jitter (`_post_with_retries`).
   - Mock LLM mode phục vụ unit/integration testing offline.
2. **Vision / OCR Transport (`backend/app/services/llm_client.py`, `backend/app/routes/ocr.py`):**
   - Trích xuất chữ và code từ ảnh màn hình bài tập (`extract_chat_text_from_image`).
   - Endpoint `/api/ocr/vision` kiểm tra kích thước, mime type và rate limit an toàn.
3. **Xác thực & Người dùng (`backend/app/deps/auth.py`, `backend/app/routes/auth.py`):**
   - Quản lý session bằng JWT Access Token (`/api/token`, `/api/register`, `/api/me`).
   - Hỗ trợ xác thực kép Firebase ID Token và database user resolution.
4. **Cơ sở dữ liệu (`backend/app/database/connection.py`, `backend/app/database/session.py`):**
   - Async SQLAlchemy Engine + AsyncSessionLocal (hỗ trợ cả PostgreSQL production và SQLite shared in-memory test mode).
5. **Consent & Privacy Infrastructure (`backend/app/routes/consent.py`, `backend/app/routes/privacy.py`):**
   - Chính sách lưu trữ dữ liệu người dùng (`save_input`, `save_result`, `history_enabled`).
   - Quyền GDPR: xóa từng session, xóa lịch sử, xóa hồ sơ và xóa toàn bộ dữ liệu người dùng (`DELETE /api/user-data`).
6. **Rate Limiting (`backend/app/services/rate_limiter.py`):**
   - `InMemoryRateLimiter` kiểm soát tần suất gọi LLM dựa trên User ID hoặc IP Client.
7. **Bộ lọc an toàn chung (`backend/app/services/safety_filter.py`):**
   - Kiểm duyệt nội dung thô tục, độc hại chung không phụ thuộc vào ngữ cảnh tình cảm.

---

## 4. Kết Quả Kiểm Thử (Verification Summary)

### Backend:
- **Pytest:** 54/54 tests passed (100% pass, thời gian chạy ~20 giây).
- **Mã phản hồi `/api/analyze`:** `410 Gone`.
- **Health Check (`/health`, `/api/health`):** `200 OK` (`{"status": "healthy"}`).

### Frontend:
- **TypeScript Typecheck:** 0 lỗi (`tsc --noEmit`).
- **Vitest:** 24/24 tests passed (8 test files).
- **Next.js Production Build:** Hoàn thành tối ưu hóa 11/11 routes tĩnh thành công.
