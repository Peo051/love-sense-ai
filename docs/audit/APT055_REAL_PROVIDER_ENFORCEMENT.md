# BÁO CÁO KIỂM TOÁN KIẾN TRÚC: BẮT BUỘC CẤU HÌNH REAL PROVIDER CHO ĐÁNH GIÁ NGHIÊN CỨU (APT-055)

- **Mã nhiệm vụ**: `APT-055`
- **Tiêu đề**: Enforce Real Provider for Research Evaluation
- **Trạng thái**: **ĐÃ HOÀN THÀNH (COMPLETED)**
- **Ngày thực hiện**: 2026-09-06
- **Phạm vi tác động**:
  - `backend/app/evaluation/research/provider.py`
  - `backend/app/evaluation/research/runner.py`
  - `backend/app/evaluation/research/__init__.py`
  - `backend/app/services/llm_client.py`
  - `scripts/run_evaluation.py`
  - `backend/tests/test_research_provider_enforcement.py`

---

## 1. BỐI CẢNH VÀ MỤC TIÊU

Theo kết luận của **APT-047** và **APT-054**, một trong những nguyên nhân khiến kết quả nghiên cứu V1 bị vô hiệu hóa hoàn toàn là runner đánh giá có thể tự kích hoạt hoặc ngầm chuyển đổi sang chế độ mock/canned khi thiếu provider thật, hoặc sinh dữ liệu giả định mà không hề thực hiện bất kỳ lệnh gọi LLM thực tế nào qua mạng.

**Mục tiêu của APT-055**:
1. Thiết lập cơ chế **Fail-Closed Preflight Validation**: Nghiên cứu đánh giá phải thất bại ngay lập tức trước khi đọc hoặc xử lý bất kỳ mẫu dữ liệu nào nếu cấu hình provider không hợp lệ.
2. Ném ra ngoại lệ `ResearchProviderConfigurationError` khi:
   - Thiếu API key hoặc thông tin xác thực.
   - Provider bị rỗng, là mock, fake, hoặc không được hỗ trợ.
   - Model rỗng hoặc mang định danh mock/fake (`mock-tutor-v1`, `canned`).
   - Sử dụng `FakeTestProvider` trong Research Mode.
3. Bảo mật thông tin xác thực: **Tuyệt đối không in, xuất hoặc ghi log API key** khi kiểm tra.
4. CLI nghiên cứu (`scripts/run_evaluation.py`) phải trả về mã thoát khác 0 (`exit code != 0`).
5. Phân định rõ ràng: Cho phép sử dụng mocked HTTP transport xung quanh interface Provider THẬT (`ResearchProvider`) phục vụ kiểm thử đơn vị độc lập mạng, nhưng nghiêm cấm mock suy luận ở tầng runner/prediction.

---

## 2. TRIỂN KHAI KỸ THUẬT

### 2.1. Ngoại lệ `ResearchProviderConfigurationError`
Được định nghĩa tại `app.evaluation.research.provider`:
```python
class ResearchProviderConfigurationError(TypeError, ValueError):
    """Ngoại lệ khi cấu hình LLM Provider phục vụ nghiên cứu không hợp lệ."""
    pass
```
*Ghi chú*: Kế thừa cả `TypeError` và `ValueError` giúp đảm bảo khả năng tương thích hồi quy hoàn hảo với các bài kiểm thử của APT-054.

### 2.2. Hàm Preflight Validation: `validate_research_provider()`
Được thực thi tại 2 chốt chặn quan trọng:
1. Ngay trong `ResearchRunner.__init__`: Ngăn runner khởi tạo khi cấu hình sai.
2. Ngay đầu hàm `ResearchRunner.run()`: Trước khi tải dataset và trước khi lặp qua các mẫu.

Quy trình xác thực:
- **Provider Validation**: Chuẩn hóa chữ thường, từ chối rỗng, từ chối `"mock"` và `"fake"`, chỉ chấp nhận real providers (`"openai"`, `"azure"`).
- **Model Validation**: Từ chối rỗng, từ chối định danh giả lập (`"mock-tutor-v1"`, `"fake"`, v.v.).
- **Fake Provider Guard**: Chặn đứng `FakeTestProvider`, `DeterministicFakeProvider`, `LeakingFakeProvider` nếu không kích hoạt `allow_test_doubles=True`.
- **Credential Presence**: Xác thực có API key trong biến môi trường (`OPENAI_API_KEY`, `AZURE_OPENAI_API_KEY`) hoặc cấu hình. Tuyệt đối không in hay ghi log giá trị API key.

### 2.3. Hỗ trợ Mocked HTTP Transport cho Real Provider Interface
Cập nhật `OpenAICompatibleLLMClient` và `OpenAIResearchProvider` cho phép nhận `transport: httpx.AsyncBaseTransport`. Điều này cho phép:
- Sử dụng `httpx.MockTransport` trong kiểm thử đơn vị.
- Toàn bộ pipeline suy luận (Pydantic serialization, Firewall, HTTP request payload, response JSON parsing, Non-gold validator) được thực thi nguyên bản trên `ResearchProvider`, không tạo ra bất kỳ đường tắt (shortcut) giả mạo nào.

### 2.4. Cập nhật CLI Nghiên cứu (`scripts/run_evaluation.py`)
Bắt ngoại lệ `ResearchProviderConfigurationError`:
```python
except ResearchProviderConfigurationError as exc:
    sys.stderr.write(f"\n[RESEARCH CONFIGURATION ERROR] {str(exc)}\n")
    sys.exit(1)
```

---

## 3. KẾT QUẢ KIỂM ĐỊNH (VERIFICATION RESULTS)

Bộ kiểm thử độc lập [`backend/tests/test_research_provider_enforcement.py`](file:///e:/App/Love%20Emotion%20Web/backend/tests/test_research_provider_enforcement.py) kiểm chứng toàn bộ các trường hợp yêu cầu:

| Test Case | Mô tả kiểm chứng | Kết quả |
| :--- | :--- | :---: |
| `test_missing_api_key` | Thiếu API key ném `ResearchProviderConfigurationError` và không rò rỉ credential | **PASSED** |
| `test_invalid_provider` | Provider rỗng, mock, fake, hoặc lạ ném `ResearchProviderConfigurationError` | **PASSED** |
| `test_missing_model` | Model rỗng, None, hoặc `mock-tutor-v1` ném `ResearchProviderConfigurationError` | **PASSED** |
| `test_fake_provider_rejected_by_preflight` | `FakeTestProvider` bị từ chối dứt khoát trong research mode | **PASSED** |
| `test_valid_mocked_transport_around_real_provider_interface` | Mocked transport hoạt động hoàn hảo trên real provider interface | **PASSED** |
| `test_research_cli_exits_nonzero_on_missing_credentials` | CLI thoát với status code 1 khi thiếu credentials | **PASSED** |

### Kiểm thử hồi quy toàn diện:
- **326/326 tests PASSED** trên toàn bộ hệ thống backend (Zero Regression).

---

## 4. KẾT LUẬN

Nhiệm vụ **APT-055** đã thiết lập thành công rào chắn tiền kiểm tra (Preflight Validation) bất khả xâm phạm. Nghiên cứu thực nghiệm hiện nay đảm bảo:
- Không thể khởi chạy hoặc tính toán metrics nếu thiếu LLM provider thực tế hợp lệ.
- Loại bỏ hoàn toàn khả năng ngầm dùng mock/cache/fallback để tạo kết quả nghiên cứu.
- Bảo đảm độ tin cậy khoa học tối đa cho các đợt chạy benchmark trong tương lai.
