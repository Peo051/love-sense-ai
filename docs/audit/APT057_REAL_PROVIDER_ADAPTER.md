# BÁO CÁO KIỂM TOÁN HẠ TẦNG NGHIÊN CỨU: CỦNG CỐ ADAPTER LLM PROVIDER THỰC TẾ (APT-057)

- **Mã nhiệm vụ**: `APT-057`
- **Tiêu đề**: Harden Real Research Provider Adapter
- **Vai trò**: Kỹ sư hạ tầng nghiên cứu (Research-Infrastructure Engineer)
- **Trạng thái**: **ĐÃ HOÀN THÀNH (COMPLETED - PASS)**
- **Ngày thực hiện**: 2026-09-06
- **Phạm vi tác động**:
  - `backend/app/evaluation/research/schemas.py` (MỚI)
  - `backend/app/evaluation/research/provider.py`
  - `backend/app/evaluation/research/runner.py`
  - `backend/app/evaluation/research/__init__.py`
  - `scripts/run_evaluation.py`
  - `artifacts/audit/research_provider_adapter.json` (MỚI)
  - `backend/tests/test_research_provider_adapter.py` (MỚI)

---

## 1. KIẾN TRÚC PROVIDER NGHIÊN CỨU (PROVIDER ARCHITECTURE)

Trong hạ tầng nghiên cứu thực nghiệm sạch (Clean-Room Research Evaluation), ranh giới giữa hệ thống đánh giá và mô hình LLM bên ngoài phải là một chốt chặn có thể thanh tra độc lập và bảo đảm tính toàn vẹn tuyệt đối:

```text
ModelInput
    ↓
Prompt Builders (A / B / C / D)
    ↓
ResearchMessage & ResearchModelRequest (Typed, Whitelisted, extra='forbid')
    ↓
GroundTruth Firewall (Kiểm tra chặn rò rỉ nhãn vàng & sentinels)
    ↓
ResearchProvider Adapter (OpenAIResearchProvider)
    ↓
HTTP Request thực tế qua mạng (hoặc httpx.MockTransport trong unit test)
    ↓
HTTP Response thô
    ↓
ResearchProviderResponse (Bảo toàn raw_text, request_id, usage thực)
    ↓
Ranh giới Provenance / Persistence thô
    ↓
parse_provider_output()
    ↓
Non-Gold Prediction Validation
    ↓
Prediction Record
```

---

## 2. GIAO DIỆN CHUẨN TẮC: ResearchProvider INTERFACE

Giao diện `ResearchProvider` (kế thừa `ABC`) được chuẩn hóa với giao thức bắt buộc:

```python
class ResearchProvider(ABC):
    @property
    def is_real_provider(self) -> bool:
        return True

    @property
    def is_fake_test_provider(self) -> bool:
        return False

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Tên định danh chuẩn tắc của provider ('openai')."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Định danh mô hình được cấu hình bất biến cho run."""
        pass

    @abstractmethod
    async def generate(
        self,
        request: ResearchModelRequest,
    ) -> ResearchProviderResponse:
        """Gửi yêu cầu đã thẩm định tới LLM thực tế và trả về envelope phản hồi bảo toàn."""
        pass
```

**Quy tắc bất biến**:
- Nghiêm cấm nhận `dict` tự do, `EvaluationRecord`, hay dữ liệu dataset thô trực tiếp vào `generate()`.
- Đầu vào bắt buộc phải là đối tượng `ResearchModelRequest` đã qua kiểm định kiểu và firewall.

---

## 3. ĐẶC TẢ ResearchModelRequest

Được định nghĩa tại `app.evaluation.research.schemas`:
- `run_id: str`: Định danh duy nhất của đợt chạy.
- `sample_id: str`: Mã định danh mẫu bài tập.
- `system_name: str`: Hệ thống đánh giá (`A`, `B`, `C`, `D`).
- `model: str`: Định danh mô hình yêu cầu (phải trùng khớp với `provider.model_name`).
- `messages: List[ResearchMessage]`: Danh sách các thông điệp có cấu trúc.
- `temperature: Optional[float]`: Tham số nhiệt độ lấy mẫu.
- `max_output_tokens: Optional[int]`: Giới hạn tokens đầu ra.
- `response_format_mode: str`: Định dạng yêu cầu (`"json"` hoặc `"text"`).
- `model_config = ConfigDict(frozen=True, extra="forbid", str_strip_whitespace=True)`

**Ranh giới cấm**:
Tuyệt đối không chứa `GroundTruth`, `EvaluationMetadata`, nhãn vàng (`bug_status`, `bug_type`, `reference_solution`, v.v.), `split`, `problem_family_id`, hay API credentials.

---

## 4. ĐẶC TẢ ResearchProviderResponse

Lớp bao gói phản hồi bảo đảm tính toàn vẹn:
- `provider: str`: Tên nhà cung cấp thực tế (`"openai"`).
- `requested_model: str`: Mô hình mà caller yêu cầu.
- `returned_model: Optional[str]`: Mô hình mà máy chủ provider thực sự phản hồi trong JSON body (ghi nhận `None` nếu thiếu).
- `raw_text: str`: Nội dung văn bản thô được sinh bởi mô hình trước khi parse.
- `request_id: Optional[str]`: ID yêu cầu trích xuất từ HTTP header (`x-request-id` hoặc `request-id`).
- `provider_response_id: Optional[str]`: ID phản hồi từ provider body (ví dụ `chatcmpl-xxx`).
- `finish_reason: Optional[str]`: Lý do hoàn thành sinh văn bản (`"stop"`, `"length"`).
- `usage: Optional[ResearchUsage]`: Token usage do provider báo cáo (gồm `input_tokens`, `output_tokens`, `total_tokens`).
- `provider_response_received: bool = True`.
- `raw_metadata: Dict[str, Any]`: Siêu dữ liệu an toàn (đã lọc sạch authorization headers và keys).
- `latency_ms: Optional[float]`: Độ trễ khứ hồi tính bằng mili-giây.
- `response_format_mode: str`: Chế độ định dạng yêu cầu.

---

## 5. RANH GIỚI TUẦN TỰ HÓA YÊU CẦU (REQUEST SERIALIZATION BOUNDARY)

Trước khi tuần tự hóa payload gửi đi:
1. `GroundTruthFirewall.default().inspect(request)` quét đệ quy đối tượng yêu cầu.
2. `assert_not_ground_truth(request)` ngăn chặn mọi đối tượng nhãn vàng.
3. Payload JSON gửi qua HTTP chỉ bao gồm:
   - `"model"`
   - `"messages"` (chỉ gồm `role` và `content`)
   - `"temperature"`
   - `"max_tokens"`
   - `"response_format"` (khi `response_format_mode == "json"`)
4. Tuyệt đối không gửi kèm bất kỳ trường ẩn hay siêu dữ liệu đánh giá nào lên server provider.

---

## 6. NGUYÊN TẮC BẢO TOÀN PHẢN HỒI THÔ (RAW RESPONSE PRESERVATION)

Tuân thủ nghiêm ngặt trật tự bắt buộc:
$$\text{HTTP Response} \implies \text{ResearchProviderResponse} \implies \text{Raw Text Preservation} \implies \text{Parser} \implies \text{Prediction}$$

Văn bản phản hồi thô của mô hình được giữ nguyên vẹn trong `raw_text` và đưa vào trường `raw_response` của `Prediction`. Hệ thống có thể trả lời câu hỏi kiểm toán bất cứ lúc nào: *"Chính xác mô hình đã sinh ra chuỗi ký tự gì trước khi CodeSense phân tích?"*

---

## 7. MÔ HÌNH YÊU CẦU VS MÔ HÌNH PHẢN HỒI (REQUESTED VS RETURNED MODEL)

Hệ thống ghi nhận độc lập hai trường:
- `requested_model`: Chuỗi mô hình người dùng yêu cầu (ví dụ: `gpt-4o-mini`).
- `returned_model`: Chuỗi mô hình provider báo cáo trong phản hồi (ví dụ: `gpt-4o-mini-2024-07-18`).
- **Quy tắc**: Nếu provider không trả về trường `model`, gán `returned_model = None`. **Tuyệt đối không lấy `requested_model` gán sang `returned_model`**.

---

## 8. THU THẬP TOKEN USAGE (USAGE EXTRACTION)

- Chỉ trích xuất từ trường `usage` chính thức của provider (`prompt_tokens`, `completion_tokens`, `total_tokens`).
- **Quy tắc**: Nếu provider không trả về `usage`, gán `usage = None`. **Tuyệt đối không sử dụng công thức ước lượng ngẫu nhiên hay độ dài ký tự (`chars // 4`)**.

---

## 9. CÁC NHÀ CUNG CẤP ĐƯỢC HỖ TRỢ (SUPPORTED PROVIDERS)

- Hiện tại hệ thống hỗ trợ chính thức và duy nhất: **`openai`** (qua adapter `OpenAIResearchProvider`).
- Tên định danh provider được chuẩn hóa về chữ thường chuẩn tắc: `"openai"`. Mọi tên định danh lạ đều bị từ chối với ngoại lệ `ResearchProviderConfigurationError`.

---

## 10. TRẠNG THÁI NHÀ CUNG CẤP AZURE (AZURE IMPLEMENTATION STATUS)

- Theo yêu cầu của Mục 12 (APT-057): **Không được giữ lựa chọn provider mang tính trang trí (decorative choice)**.
- Do hiện tại hệ thống chưa có triển khai `AzureResearchProvider` chuyên biệt (với endpoint, api-version, deployment-name), tùy chọn `azure` đã được **loại bỏ hoàn toàn** khỏi tham số `--provider` trên CLI (`scripts/run_evaluation.py` và `runner.py`).
- Hàm `validate_research_provider` từ chối minh thị và ném ra thông báo lỗi rõ ràng nếu nhận được `provider="azure"`.

---

## 11. ĐỘC LẬP VỚI MÃ SẢN PHẨM (SHARED CODE WITH PRODUCTION)

- Đã kiểm toán phân hệ `backend/app/tutor/provider.py`: Phân hệ này phục vụ tính năng AI Tutor cho người dùng cuối với các hành vi ứng xử thân thiện.
- Phân hệ nghiên cứu (`backend/app/evaluation/research/provider.py`) hoàn toàn độc lập, không kế thừa từ `TutorLLMProvider`, không chia sẻ cơ chế fallback, không retry với model thay thế.
- Tầng duy nhất được tái sử dụng là client HTTP cơ bản (`httpx`), nhưng toàn bộ logic đóng gói, kiểm tra firewall, bắt lỗi fail-loud, và trích xuất metadata được quản lý độc lập 100% trong research.

---

## 12. CƠ CHẾ BẢO MẬT VÀ TOÀN VẸN DỮ LIỆU (SECURITY/INTEGRITY GUARDS)

1. **Chống Prompt-Injection thay đổi cấu hình**:
   - Mã nguồn học sinh có chứa các dòng chú thích giả mạo chỉ dẫn (ví dụ: `// provider="mock"` hay `// model="fake"`) chỉ được xử lý như văn bản chuỗi thuần túy trong `user message`.
   - Cấu hình provider, model identifier, temperature, và endpoint hoàn toàn bất biến (`frozen`).
2. **Loại bỏ Secrets khi Tuần Tự Hóa**:
   - Phương thức `to_serializable_dict()` tự động thanh lọc triệt để các trường nhạy cảm (`auth`, `key`, `token`, `secret`, `bearer`) khỏi `raw_metadata`.
3. **Kiểm tra Tĩnh Không Truy Cập Metrics**:
   - Mô-đun `provider.py` không import bất kỳ hàm tính toán metrics, scoring, hay bộ đánh giá Ground Truth nào.

---

## 13. KẾT QUẢ KIỂM THỬ (TEST VERIFICATION RESULTS)

### A. Bộ kiểm thử đơn vị chuyên sâu [`backend/tests/test_research_provider_adapter.py`](file:///E:/App/Love%20Emotion%20Web/backend/tests/test_research_provider_adapter.py):
Toàn bộ **18/18 tests PASSED (100%)**:
1. `test_provider_builds_request_from_model_request_only`: **PASSED**
2. `test_provider_request_contains_no_ground_truth`: **PASSED**
3. `test_provider_request_contains_no_evaluation_metadata`: **PASSED**
4. `test_provider_preserves_raw_response`: **PASSED**
5. `test_provider_extracts_request_or_response_id_when_available`: **PASSED**
6. `test_provider_does_not_invent_request_id`: **PASSED**
7. `test_requested_and_returned_model_are_recorded_separately`: **PASSED**
8. `test_provider_does_not_invent_returned_model`: **PASSED**
9. `test_provider_extracts_usage_when_available`: **PASSED**
10. `test_provider_does_not_estimate_missing_usage`: **PASSED**
11. `test_provider_preserves_finish_reason`: **PASSED**
12. `test_provider_config_does_not_change_between_samples`: **PASSED**
13. `test_student_code_cannot_change_provider_configuration`: **PASSED**
14. `test_provider_does_not_import_ground_truth_evaluator`: **PASSED**
15. `test_invalid_http_response_uses_fail_loud_policy`: **PASSED**
16. `test_fake_test_provider_is_not_used_by_adapter_tests`: **PASSED**
17. `test_azure_provider_rejected_explicitly`: **PASSED**
18. `test_serializable_dict_excludes_secrets`: **PASSED**

### B. Kiểm thử hồi quy mục tiêu:
- **63/63 tests PASSED** trên toàn bộ 6 tệp kiểm thử nghiên cứu trọng yếu.

### C. Kiểm thử toàn bộ hệ thống backend:
```powershell
.\venv\Scripts\python -m pytest tests -q
# Kết quả: 363 passed in 116.93s (100% PASSED, ZERO REGRESSION)
```

---

## 14. RỦI RO CÒN LẠI VÀ KHUYẾN NGHỊ (REMAINING RISKS & RECOMMENDATIONS)

1. **Hạn mức tài khoản Provider**: Nếu tài khoản OpenAI hết tiền hoặc chạm giới hạn hạn mức tổ chức (tier limits), provider sẽ trả về 429 hoặc 401 khiến đợt chạy dừng hoặc chuyển sang `PARTIAL`. Cần có bước kiểm tra hạn ngạch tài khoản trước các đợt chạy lớn.
2. **Đo đạc độ trễ mạng chính thức (Telemetry)**: Tác vụ APT-057 đã loại bỏ hoàn toàn việc sinh độ trễ giả tạo (`random.uniform`). Việc tính toán phân phối thống kê độ trễ chính thức ($p_{50}, p_{95}, p_{99}$) và chi phí tài chính sẽ do tác vụ tiếp theo **APT-058** đảm nhiệm.
