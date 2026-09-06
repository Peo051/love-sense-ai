# APT-039: BÁO CÁO KIỂM TOÁN TÁI LẬP PHÒNG SẠCH (CLEAN-ROOM REPRODUCTION AUDIT)

**Kiểm toán viên:** Independent Research Auditor  
**Dự án:** CodeSense AI - Adaptive Programming Tutor  
**Phiên bản đóng băng kiểm toán:** `codesense-research-v1.0`  
**Ngày thực hiện kiểm toán:** 2026-09-06  
**Mục tiêu:** Xác minh xem quy trình đánh giá và kết quả công bố của CodeSense AI có thể tái lập được từ một môi trường sạch mà không phụ thuộc vào trạng thái ẩn (hidden local state) hay không.  
*(Ghi chú bắt buộc: Không thực hiện gọi lại LLM trên tập frozen test split nhằm bảo toàn tính nguyên vẹn của tập kiểm định).*

---

## 1. Môi Trường Thực Thi Phòng Sạch (Clean Environment Specification)

Kiểm toán viên ghi nhận thông tin cấu hình môi trường chuẩn tại thời điểm kiểm toán:

| Thuộc tính môi trường | Giá trị thực tế |
| :--- | :--- |
| **Hệ điều hành (OS)** | Microsoft Windows NT 10.0.26200.0 (Windows 11) |
| **Python Version** | `Python 3.13.9` |
| **Node.js Version** | `v24.14.0` |
| **NPM Version** | `11.9.0` |
| **.NET SDK Version** | `10.0.400` |
| **Git Commit SHA** | `3035e069d26892a010276993bdc452c9a458f45c` (Release v1.0) |
| **Backend Requirements Hash** | `99721287c25c9f558851465a8f9f8009bc633c46d2efa669c52c7f82353f2716` |
| **Dataset SHA-256** | `5ca8890eb12542a78a2c2c4ac86856f1ec2ff52e2e790687e5677baa00d637ed` |

---

## 2. Kết Quả Xây Dựng & Kiểm Định Ứng Dụng (Application Verification)

| Bộ kiểm định (Verification Suite) | Lệnh thực thi | Kết quả | Chi tiết |
| :--- | :--- | :---: | :--- |
| **Backend Unit Tests** | `pytest -o pythonpath=backend backend/tests` | **PASS** | 286/286 passed (100%), bao gồm cả 7 taint isolation tests |
| **Frontend Unit Tests** | `npm --prefix frontend test -- --run` | **PASS** | 37/37 passed across 8 test suites |
| **Dataset Validator** | `python scripts/validate_vietcsharptutor.py` | **PASS** | 600/600 mẫu hợp lệ theo schema kỹ thuật |
| **Taint Isolation Tests** | `pytest backend/tests/test_taint_isolation.py` | **PASS** | 7/7 tests pass |

---

## 3. Tái Tính Toán Offline Các Chỉ Số Đóng Băng (Offline Metric Reproduction)

Kiểm toán viên đã nạp lại 4 file dự đoán đã lưu trữ của đợt chạy thực nghiệm frozen test:
- `runs/run_A_test_20260906_103703/predictions.jsonl`
- `runs/run_B_test_20260906_103703/predictions.jsonl`
- `runs/run_C_test_20260906_103703/predictions.jsonl`
- `runs/run_D_test_20260906_103703/predictions.jsonl`

Sau đó chạy lại bộ tính toán `TutoringMetricsSuite` hoàn toàn offline mà KHÔNG gọi thêm bất kỳ lệnh nào tới mô hình LLM.

### Kết quả đối chiếu với `results/evaluation_results.json` & `ANALYSIS_SUMMARY.md`:

| Hệ thống | Số lượng mẫu | Sai lệch phát hiện (Discrepancies) | Trùng khớp tuyệt đối |
| :--- | :---: | :---: | :---: |
| **Baseline A** | 120 | 0 sai lệch | **100% MATCH** |
| **Baseline B** | 120 | 0 sai lệch | **100% MATCH** |
| **Proposed C** | 120 | 0 sai lệch | **100% MATCH** |
| **Proposed D** | 120 | 0 sai lệch | **100% MATCH** |

> **Kết luận kiểm toán:** Bộ công cụ tính toán chỉ số `backend/app/evaluation/metrics.py` hoàn toàn tất định (deterministic), không có sai số trôi nổi hoặc thay đổi kết quả khi tính toán lại.

---

## 4. Tái Lập Thực Nghiệm Trực Tiếp Trên Validation Split (Live Rerun on Validation)

Để đo lường độ ổn định của hệ thống đánh giá, kiểm toán viên đã thực thi 3 lần lặp độc lập trên 30 mẫu `validation` cố định với các random seeds khác nhau (`seed = 42, 100, 999`) trên hệ thống Proposed C:

| Lần lặp | Random Seed | Diagnosis Accuracy | JSON Valid Rate | Evidence Faithfulness | Tỷ lệ lỗi (Failure Rate) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Lần 1** | 42 | 93.33% | 100% | 100% | 0.0% |
| **Lần 2** | 100 | 90.00% | 100% | 100% | 0.0% |
| **Lần 3** | 999 | 93.33% | 100% | 100% | 0.0% |

### Đo lường phương sai thực nghiệm:
- **Độ chính xác trung bình (Mean Accuracy):** $92.22\%$
- **Phương sai độ chính xác (Accuracy Variance):** $0.000246$ (rất thấp, phản ánh độ ổn định của mock engine).
- **Tỷ lệ thất bại (Failure Rate):** $0.0\%$.
- **Độ hợp lệ JSON đầu ra (Output Validity):** $100\%$.

---

## 5. Kiểm Toán Tính Xác Thực Của Provider (Provider Authenticity Audit)

Kiểm toán viên đã rà soát toàn bộ cấu trúc manifests và log calls:
1. **Thông tin Provider & Model:**
   - Trường `provider` trong manifests ghi rõ: `"mock"`.
   - Trường `model` ghi rõ: `"mock-tutor-v1"`.
2. **Đánh giá về tính nguyên bản:**
   - Đợt chạy thực nghiệm được đóng băng tại bản release `codesense-research-v1.0` sử dụng harness mô phỏng tĩnh nội bộ (Internal Mock Simulation Harness).
   - Hệ thống KHÔNG kết nối tới gateway OpenAI/Gemini/Anthropic thực sự trong quá trình chạy `runner.py`.
   - Do đó, mọi phát biểu khoa học cần làm rõ: Kết quả thực nghiệm phản ánh hành vi của mock simulation harness, không phản ánh năng lực API của một mô hình thương mại cụ thể.

---

## 6. Kiểm Toán Trạng Thái Ẩn (Cached-State Audit)

Kiểm toán viên xác nhận:
- Khi xóa bỏ toàn bộ thư mục `__pycache__`, file sqlite database rỗng, và không nạp bất kỳ thông tin hồ sơ sinh viên hay lịch sử nộp bài cũ nào vào bộ nhớ, pipeline đánh giá vẫn thực thi hoàn toàn trơn tru và cho ra kết quả tương đương.
- Không tồn tại trạng thái ẩn (hidden local state) bắt buộc để chạy code.

---

## 7. Phán Quyết Kiểm Toán Tái Lập (Final Verdict)

# PHÁN QUYẾT: REPRODUCIBLE WITH LIMITATIONS (TÁI LẬP CÓ GIỚI HẠN)

### Giải thích giới hạn:
1. **Tái lập hoàn toàn (Fully Reproducible):** Toàn bộ mã nguồn backend, frontend, schema validation và bộ công cụ tính toán offline metrics tái lập chính xác 100% số liệu đã công bố mà không cần gọi lại LLM.
2. **Giới hạn thực nghiệm (Experimental Limitation):** Bản thân các file dự đoán được sinh ra từ mock harness nội bộ (`mock-tutor-v1`), chưa phải là kết quả thu thập từ các API mô hình LLM trực tiếp trong môi trường sản xuất.
