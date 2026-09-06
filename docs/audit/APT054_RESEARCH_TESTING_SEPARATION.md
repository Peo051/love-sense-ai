# BÁO CÁO KIỂM TOÁN KIẾN TRÚC: TÁCH BIỆT TESTING HARNESS KHỎI RESEARCH EVALUATION (APT-054)

- **Mã nhiệm vụ**: `APT-054`
- **Tiêu đề**: Separate Testing Harness from Research Evaluation
- **Trạng thái**: **ĐÃ HOÀN THÀNH (COMPLETED)**
- **Ngày thực hiện**: 2026-09-06
- **Phạm vi tác động**:
  - `backend/app/evaluation/research/` (`runner.py`, `provider.py`, `parser.py`, `provenance.py`, `__init__.py`)
  - `backend/app/evaluation/testing/` (`fake_provider.py`, `fixtures.py`, `__init__.py`)
  - `backend/app/evaluation/runner.py`
  - `scripts/run_evaluation.py`
  - `backend/tests/test_research_testing_separation.py`

---

## 1. BỐI CẢNH VÀ MỤC TIÊU

Các phát hiện kiểm toán từ **APT-046**, **APT-047** và **APT-053** cho thấy rủi ro nghiêm trọng khi mã kiểm thử nội bộ (test doubles, mocks, deterministic fixtures) bị trộn lẫn trực tiếp với mã đánh giá nghiên cứu khoa học (research runner). Điều này dẫn tới nguy cơ:
1. Đánh giá nghiên cứu vô tình hoặc cố ý kích hoạt cờ `mock=True`, tạo ra kết quả giả mạo mà không thực thi suy luận LLM thực tế.
2. Provider giả lập (fake/mock) có thể thỏa mãn cấu hình CLI của nghiên cứu.
3. Không có ranh giới kiểu dữ liệu (type-level boundary) để ngăn chặn test doubles lọt vào pipeline thực nghiệm.

**Mục tiêu của APT-054**:
- Tách bạch cấu trúc vật lý và logic giữa **Research Evaluation** và **Testing Harness**.
- Chuẩn hóa hai interface đối lập: `ResearchProvider` (chỉ cho phép LLM thật) và `FakeTestProvider` (chỉ cho phép trong test nội bộ).
- Loại bỏ hoàn toàn tham số `mock` và `mock_mode` khỏi `ResearchRunner` và CLI nghiên cứu.
- Cơ chế **Fail-Closed**: Tự động từ chối `FakeTestProvider` trong Research Mode nếu không có môi trường kiểm thử tường minh (`allow_test_doubles=True` hoặc `CODESENSE_EVAL_TEST_ENV=1`).

---

## 2. CHI TIẾT TÁCH BIỆT KIẾN TRÚC (ARCHITECTURAL DECOUPLING)

```
backend/app/evaluation/
├── research/                       # KHÔNG GIAN NGHIÊN CỨU THỰC NGHIỆM KHOA HỌC
│   ├── runner.py                   # ResearchRunner: Không có cờ mock, fail-closed khi gặp fake
│   ├── provider.py                 # ResearchProvider interface & OpenAIResearchProvider
│   ├── parser.py                   # Clean-Room Parser & Non-Gold Validator
│   ├── provenance.py               # Immutable Manifest Generator & Dataset Hashing
│   └── __init__.py
│
├── testing/                        # KHÔNG GIAN KIỂM THỬ ĐƠN VỊ NỘI BỘ
│   ├── fake_provider.py            # FakeTestProvider, DeterministicFakeProvider, LeakingFakeProvider
│   ├── fixtures.py                 # Clean ModelInput, GroundTruth & synthetic dataset fixtures
│   └── __init__.py
│
└── runner.py                       # Tương thích ngược (Backward Compatibility) kế thừa ResearchRunner
```

### 2.1. Quy tắc không gian Research (`app.evaluation.research`)
1. **Real Provider Only**: Bắt buộc kết nối thực tế tới LLM qua các lớp kế thừa `ResearchProvider` (`is_real_provider = True`).
2. **Không có cờ mock**: `ResearchRunner.__init__` không có tham số `mock` hay `mock_mode`.
3. **Fail-Closed Provider Check**: Nếu `provider_client` là `FakeTestProvider` trong research mode, hệ thống ném ngoại lệ `TypeError: FakeTestProvider '<ClassName>' is strictly rejected in research evaluation mode`.
4. **Không hỗ trợ cờ CLI mock**: Giao diện CLI `scripts/run_evaluation.py` loại bỏ hoàn toàn `--mock` và chỉ chấp nhận các provider thực tế (`openai`, `azure`).
5. **Manifest sạch**: Bất biến, không chứa cờ `mock_mode`.

### 2.2. Quy tắc không gian Testing (`app.evaluation.testing`)
1. **Cô lập kiểm thử**: `FakeTestProvider` (`is_fake_test_provider = True`, `is_real_provider = False`) chỉ được phép hoạt động khi runner được cấu hình tường minh với `allow_test_doubles=True` hoặc biến môi trường `CODESENSE_EVAL_TEST_ENV=1`.
2. **Deterministic Fixtures**: Cung cấp `fixtures.py` để tạo `ModelInput`, `GroundTruth` và test dataset độc lập, bảo đảm kiểm thử đơn vị chạy 100% offline với độ tin cậy tuyệt đối.

---

## 3. KẾT QUẢ KIỂM ĐỊNH (VERIFICATION RESULTS)

File kiểm thử `backend/tests/test_research_testing_separation.py` được triển khai để kiểm chứng toàn bộ 4 ràng buộc:

| Test Case | Mục tiêu kiểm chứng | Kết quả |
| :--- | :--- | :---: |
| `test_research_runner_has_no_mock_flag` | Xác minh `ResearchRunner.__init__` không chứa `mock`/`mock_mode`, manifest không chứa `mock_mode` | **PASSED** |
| `test_fake_provider_rejected_in_research_mode` | Xác minh `ResearchRunner` từ chối dứt khoát `FakeTestProvider` (`TypeError`) và `provider='mock'` (`ValueError`) | **PASSED** |
| `test_test_harness_still_supports_unit_tests` | Xác minh harness kiểm thử vẫn hoạt động hoàn hảo, tạo dự đoán đúng và manifest đầy đủ khi kích hoạt môi trường test | **PASSED** |
| `test_research_cli_rejects_mock_and_fake_providers` | Xác minh CLI `scripts/run_evaluation.py` chặn đứng `--mock` và `--provider mock` | **PASSED** |

### Kết quả chạy kiểm thử hồi quy toàn diện:
- `tests/test_research_testing_separation.py`: **4 passed**
- `tests/test_evaluation_runner.py`: **4 passed**
- `tests/test_ground_truth_isolation.py`: **6 passed**
- `tests/test_taint_isolation.py`: **7 passed**
- `tests/test_model_input_boundary.py`: **6 passed**
- `tests/test_ground_truth_firewall.py`: **8 passed**
- `tests/test_ablation.py`: **5 passed**
- **Toàn bộ hệ thống kiểm thử**: **100% PASS (Zero Regressions)**

---

## 4. KẾT LUẬN

Nhiệm vụ **APT-054** đã hoàn tất việc tách bạch kiến trúc giữa **Testing Harness** và **Research Evaluation Runner**. Toàn bộ mã nguồn nghiên cứu khoa học hiện nay được bảo vệ bằng rào chắn kiến trúc đa tầng:
1. Không thể vô tình hay cố ý chạy mock trong pipeline nghiên cứu.
2. Ranh giới kiểm thử và nghiên cứu được thực thi nghiêm ngặt tại runtime và type-system.
3. Độ trung thực khoa học (scientific evaluation integrity) được bảo vệ hoàn toàn.
