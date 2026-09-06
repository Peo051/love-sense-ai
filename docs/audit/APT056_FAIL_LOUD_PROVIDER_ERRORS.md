# BÁO CÁO KIỂM TOÁN TÍNH TOÀN VẸN NGHIÊN CỨU: THỰC THI FAIL-LOUD CHO MỌI LỖI PROVIDER (APT-056)

- **Mã nhiệm vụ**: `APT-056`
- **Tiêu đề**: Enforce Fail-Loud Provider Errors in Research Evaluation
- **Vai trò**: Kỹ sư bảo toàn tính toàn vẹn nghiên cứu (Research-Integrity Engineer)
- **Trạng thái**: **ĐÃ HOÀN THÀNH (COMPLETED)**
- **Ngày thực hiện**: 2026-09-06
- **Phạm vi tác động**:
  - `backend/app/evaluation/research/provider.py`
  - `backend/app/evaluation/research/runner.py`
  - `backend/app/evaluation/research/__init__.py`
  - `scripts/run_evaluation.py`
  - `artifacts/audit/research_failure_policy.json`
  - `backend/tests/test_research_fail_loud.py`

---

## 1. TỔNG QUAN VÀ NGUYÊN TẮC CỐT LÕI (EXECUTIVE SUMMARY & CORE PRINCIPLE)

Trong các hệ thống phần mềm thương mại, cơ chế *graceful degradation* (hạ cấp êm thuận) và *fallback* (dùng dự phòng mock, cache cũ, hoặc giá trị mặc định) là ưu điểm giúp tăng trải nghiệm người dùng. Tuy nhiên, trong **nghiên cứu khoa học và đánh giá mô hình (Scientific Evaluation Benchmark)**, đây là hành vi **nguy hiểm và phá hoại tính toàn vẹn nghiên cứu** bậc nhất. Nếu một cuộc gọi inference đến LLM provider gặp lỗi mạng, timeout, hoặc trả về định dạng sai mà hệ thống ngầm fallback sang câu trả lời mặc định, nhãn vàng (Ground Truth), kết quả cached, hay chuyển sang mô hình khác, thì toàn bộ các chỉ số thống kê (accuracy, F1, pass@k) sẽ bị sai lệch hoàn toàn, tạo ra kết quả giả mạo trong các báo cáo khoa học.

### Nguyên tắc bất biến (Inviolable Invariant) của APT-056:
> **`NO VALID REAL PROVIDER RESPONSE -> NO VALID RESEARCH PREDICTION`**
>
> *(Không có phản hồi thực tế và hợp lệ từ LLM provider thật -> Tuyệt đối không sinh bất kỳ dự đoán nghiên cứu nào).*

Nếu không có phản hồi suy luận thực sự từ mô hình được cấu hình, mẫu đó **KHÔNG ĐƯỢC PHÉP** có dự đoán trong `predictions.jsonl`. Nó phải được ghi nhận công khai là một mẫu thất bại (`ResearchFailureRecord`), và toàn bộ đợt chạy (run) sẽ không bao giờ được đánh dấu là `COMPLETE`.

---

## 2. HỆ THỐNG PHÂN LOẠI LỖI (ERROR TAXONOMY & EXCEPTION HIERARCHY)

Tất cả các lỗi phát sinh từ runtime inference của research provider được cấu trúc phân cấp chặt chẽ kế thừa từ `ResearchProviderError`:

```text
ResearchProviderError (Exception)
├── ResearchProviderConfigurationError (kế thừa TypeError, ValueError)
│   └── Phát sinh khi: Thiếu API key, provider là mock/fake, model không hợp lệ
├── ResearchProviderTimeoutError
│   └── Phát sinh khi: Provider không phản hồi trong khoảng thời gian quy định (408 / ReadTimeout)
├── ResearchProviderNetworkError
│   └── Phát sinh khi: Lỗi tầng transport, DNS, kết nối TCP bị ngắt (ConnectError, NetworkError)
├── ResearchProviderAuthenticationError
│   └── Phát sinh khi: HTTP 401 Unauthorized, 403 Forbidden (API key sai/hết hạn)
├── ResearchProviderRateLimitError
│   └── Phát sinh khi: HTTP 429 Too Many Requests, quota exceeded
├── ResearchProviderResponseError
│   └── Phát sinh khi: HTTP 5xx (500, 502, 503, 504), phản hồi HTTP rỗng, choices rỗng
└── ResearchProviderSchemaError
    └── Phát sinh khi: JSON trả về bị hỏng cú pháp hoặc không tuân thủ schema bắt buộc
```

Mọi ngoại lệ trên đều đóng gói các thuộc tính định danh máy (machine-readable attributes):
- `retryable: bool` (có được phép thử lại theo chính sách hay không)
- `http_status: Optional[int]` (mã trạng thái HTTP cụ thể)
- `failure_type: str` (mã định danh lỗi phân loại: `TIMEOUT`, `RATE_LIMIT`, `AUTHENTICATION_ERROR`, v.v.)
- `attempts: int` (số lần đã cố gắng gọi)
- `message_safe: str` (thông điệp lỗi đã được làm sạch, triệt tiêu mọi thông tin nhạy cảm)

---

## 3. CHÍNH SÁCH THỬ LẠI (RETRY POLICY SPECIFICATION)

Để xử lý các sự cố mạng tạm thời nhưng vẫn bảo đảm tính tất định và ngăn chặn vòng lặp vô hạn, lớp `ResearchRetryPolicy` được định nghĩa với các tham số giới hạn nghiêm ngặt:

| Tham số | Giá trị mặc định | Mô tả |
| :--- | :--- | :--- |
| `max_attempts` | **3** | Tối đa 3 lần thử (1 lần ban đầu + tối đa 2 lần retry) |
| `base_delay_seconds` | **0.1s** (kiểm thử) / cấu hình được | Thời gian chờ ban đầu trước lần retry đầu tiên |
| `backoff_factor` | **2.0** | Hệ số giãn cách lũy thừa nhị phân |
| `max_delay_seconds` | **5.0s** | Giới hạn trần thời gian chờ |

### Phân định Retryable vs Non-Retryable:
- **Được phép retry (Transient Errors)**:
  - `ResearchProviderTimeoutError` (hoặc HTTP 408)
  - `ResearchProviderNetworkError` (lỗi kết nối socket/transport tạm thời)
  - `ResearchProviderRateLimitError` (HTTP 429)
  - HTTP 5xx server errors (`500`, `502`, `503`, `504`)
- **TUYỆT ĐỐI CẤM retry (Terminal Errors - ném lỗi ngay lập tức)**:
  - HTTP 401 Unauthorized, HTTP 403 Forbidden (lỗi xác thực)
  - HTTP 400 Bad Request, HTTP 404 Not Found
  - `ResearchProviderConfigurationError` (lỗi cấu hình runner/provider)
  - Vi phạm Ground Truth Firewall (`GroundTruthLeakageError`)
  - Phản hồi rỗng hoặc sai cú pháp schema từ mô hình

---

## 4. PHÂN ĐỊNH SAMPLE FAILURE VS RUN FAILURE

Trong một đợt chạy benchmark bao gồm hàng trăm mẫu:
1. **Lỗi cấp mẫu (Sample-Level Failure)**:
   - Khi một mẫu dữ liệu gặp sự cố inference từ provider (ví dụ: timeout sau 3 lần retry, 429 kéo dài, phản hồi rỗng, hoặc model sinh JSON hỏng):
   - Mẫu đó **không được đưa vào** file `predictions.jsonl`.
   - Một bản ghi `ResearchFailureRecord` được ghi lại với đầy đủ metadata: `sample_id`, `provider`, `model`, `attempts`, `failure_type`, `http_status`, `message_safe`, `timestamp`.
   - Đợt chạy tiếp tục với các mẫu còn lại (nếu `allow_partial=True`), và kết quả toàn bộ run được đánh dấu là `PARTIAL`.
2. **Lỗi cấp đợt chạy (Run-Level Failure / Abort)**:
   - Khi phát sinh các lỗi mang tính hệ thống làm vô hiệu hóa toàn bộ thử nghiệm:
     - Lỗi cấu hình (`ResearchProviderConfigurationError` - ví dụ: thiếu API key, tên provider/model sai).
     - Lỗi xác thực provider (`ResearchProviderAuthenticationError` - HTTP 401/403).
     - Phát hiện rò rỉ nhãn vàng (`GroundTruthLeakageError` từ firewall).
   - Đợt chạy sẽ **hủy ngay lập tức (FAIL-FAST / ABORT)**, không xử lý bất kỳ mẫu nào tiếp theo, không xuất predictions giả mạo.

---

## 5. CHÍNH SÁCH BỘ NHỚ ĐỆM (CACHING POLICY)

1. **Vô hiệu hóa mặc định**: Trong runner nghiên cứu (`ResearchRunner`), `caching_enabled` được gán cứng là `False` theo mặc định.
2. **Cấm tái sử dụng cache chéo**: Không cho phép sử dụng cache từ các lượt chạy khác nhau hoặc từ các tác vụ khác.
3. **Cấm cache kết quả thất bại**: Các yêu cầu thất bại (timeout, 5xx, 429) tuyệt đối không được ghi vào bất kỳ bộ nhớ đệm nào để tránh tái hiện lỗi giả tạo.
4. **Không suy luận giả định**: Mọi lượt chạy nghiên cứu phải phản ánh chính xác trạng thái thực thi trực tiếp từ LLM provider.

---

## 6. CÁC ĐIỀU KIỆN BẤT BIẾN KHÔNG-THAY-THẾ (NO-SUBSTITUTION INVARIANTS)

Kiến trúc APT-056 bảo đảm 5 cam kết không thể bị vi phạm:
1. **No Mock Fallback**: Khi provider thật gặp sự cố, hệ thống không bao giờ tự động chuyển hướng sang `FakeTestProvider`, mock handler hay canned responses.
2. **No Ground Truth Fallback**: Khi provider lỗi hoặc không phản hồi, hệ thống không bao giờ trích xuất hoặc sao chép câu trả lời từ dataset nhãn vàng.
3. **No Heuristic / Default Prediction**: Không tự động điền các dự đoán mặc định rỗng như `{"diagnosis": "Unknown", "bug_type": "None"}`.
4. **No Silent Model Substitution**: Không tự ý chuyển từ `gpt-4o` sang `gpt-4o-mini` hay bất kỳ model nào khác khi model được chỉ định gặp lỗi.
5. **No Silent Provider Substitution**: Không tự ý chuyển đổi giữa các provider (ví dụ: từ OpenAI sang Azure hay Local) mà không có sự chỉ định minh thị từ người điều hành.

---

## 7. MÃ THOÁT CLI VÀ ĐỊNH DẠNG ĐẦU RA MÁY ĐỌC (CLI EXIT CODES & MACHINE OUTPUT)

CLI chạy nghiên cứu (`scripts/run_evaluation.py`) tuân thủ nghiêm ngặt chuẩn mã thoát máy đọc phục vụ các hệ thống CI/CD và pipeline kiểm toán tự động:

| Trạng thái Run | Exit Code | Ý nghĩa khoa học |
| :--- | :---: | :--- |
| **`COMPLETE`** | `0` | 100% mẫu được suy luận thành công từ real provider. Toàn vẹn tuyệt đối. |
| **`PARTIAL`** | `2` | Một số mẫu bị lỗi runtime inference. Có file `failure_report.json`. Không thể dùng làm gold benchmark đầy đủ. |
| **`FAILED`** | `1` | Lỗi cấu hình nghiêm trọng, lỗi xác thực, rò rỉ firewall, hoặc run bị hủy toàn bộ. |

### Cấu trúc tệp Báo cáo Thất bại (`failure_report.json`):
```json
{
  "run_id": "run_C_validation_20260906_234500",
  "system": "C",
  "split": "validation",
  "run_status": "PARTIAL",
  "total_samples": 60,
  "successful_predictions": 59,
  "failed_samples_count": 1,
  "failures": [
    {
      "sample_id": "sample_042",
      "provider": "openai",
      "model": "gpt-4o-mini",
      "attempts": 3,
      "failure_type": "TIMEOUT",
      "http_status": 408,
      "retryable": true,
      "timestamp": "2026-09-06T23:45:12.345678Z",
      "message_safe": "Research provider connection timed out: ReadTimeout"
    }
  ]
}
```

---

## 8. BẢO MẬT VÀ LÀM SẠCH LỖI (PRIVACY & SANITIZATION GUARANTEES)

Hàm `sanitize_error_message(message: str) -> str` được triển khai để lọc bỏ triệt để:
- Chuỗi thông tin xác thực (`Bearer <token>`, `api_key=...`, `sk-...`).
- Mã nguồn đầy đủ của sinh viên trong traceback hoặc thông báo lỗi HTTP.
- Toàn bộ các giá trị sentinel bị firewall đánh dấu.
- Cắt ngắn thông điệp lỗi quá dài (tối đa 500 ký tự) để chống tràn log hoặc vô tình in dữ liệu payload.

---

## 9. KẾT QUẢ KIỂM ĐỊNH (TEST VERIFICATION RESULTS)

Bộ kiểm thử chuyên sâu [`backend/tests/test_research_fail_loud.py`](file:///e:/App/Love%20Emotion%20Web/backend/tests/test_research_fail_loud.py) bao gồm **19 bài kiểm thử độc lập** sử dụng `httpx.MockTransport` bao phủ toàn bộ các kịch bản thực tế:

| Kịch bản | Test Case | Kết quả |
| :--- | :--- | :---: |
| **Scenario A: Timeout** | `test_timeout_retries_then_fails` | **PASSED** (retry đúng 3 lần, ném `ResearchProviderTimeoutError`) |
| **Scenario B: Rate Limit** | `test_rate_limit_retries_then_fails`<br>`test_scenario_b_rate_limit_then_success` | **PASSED** (retry 429 và thành công sau khi phục hồi) |
| **Scenario C: 5xx Error** | `test_500_retries_then_fails` | **PASSED** (retry 3 lần, thất bại fail-loud) |
| **Scenario D: 401/403 Auth** | `test_401_fails_without_retry`<br>`test_403_fails_without_retry` | **PASSED** (thất bại ngay lập tức ở lần đầu tiên, không retry) |
| **Scenario E: Malformed Output** | `test_invalid_json_never_creates_default_prediction`<br>`test_empty_response_never_creates_prediction`<br>`test_schema_invalid_response_never_creates_prediction` | **PASSED** (tuyệt đối không sinh default prediction khi JSON lỗi) |
| **Scenario F: Anti-Substitution** | `test_provider_failure_does_not_use_mock`<br>`test_provider_failure_does_not_use_ground_truth`<br>`test_provider_failure_does_not_use_cached_prediction`<br>`test_provider_failure_does_not_switch_model`<br>`test_provider_failure_does_not_switch_provider` | **PASSED** (tuyệt đối không fallback sang mock, GT, cache, model khác) |
| **Scenario G: Run Lifecycle** | `test_failed_sample_is_recorded`<br>`test_partial_run_not_marked_complete`<br>`test_configuration_failure_aborts_run`<br>`test_research_cli_exposes_no_test_double_flag` | **PASSED** (ghi nhận đúng failure record, partial status, cấm cờ mock) |

### Kiểm tra hồi quy toàn diện hệ thống:
- **345/345 tests PASSED** trên toàn bộ hệ thống backend (Zero Regression, 100% pass rate).

---

## 10. RỦI RO CÒN LẠI VÀ KHUYẾN NGHỊ TƯƠNG LAI (REMAINING RISKS & RECOMMENDATIONS)

1. **Giám sát Quota Provider bên ngoài**: Mặc dù đã có retry với backoff cho mã 429, nếu tài khoản hết hạn mức tiền (quota exhausted), toàn bộ đợt chạy sẽ chuyển thành `PARTIAL` hoặc `FAILED`. Khuyến nghị kiểm tra số dư tài khoản trước khi thực thi benchmark lớn.
2. **Tiến trình Resume cho Partial Runs**: Khi một đợt chạy bị `PARTIAL` do lỗi mạng của một vài mẫu, cần phát triển thêm công cụ an toàn để *chạy bù* (replay-only-failed) cho các mẫu chưa thành công, sau đó merge có hash xác thực thay vì phải chạy lại từ đầu toàn bộ tập dữ liệu.
3. **Củng cố Firewall ở tầng Response Validator**: Tiếp tục duy trì quy tắc: Bất kỳ response nào chứa văn bản trùng khớp trên 95% với `reference_hints` hoặc `reference_solution` đều phải bị gắn cờ điều tra nhiễm bẩn dữ liệu.
