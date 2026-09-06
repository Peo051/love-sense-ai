# APT-037: BÁO CÁO KIỂM TOÁN CÔ LẬP NHÃN VÀNG & Ô NHIỄM DỮ LIỆU (GROUND-TRUTH ISOLATION & TAINT AUDIT)

**Kiểm toán viên:** Independent Research Auditor  
**Dự án:** CodeSense AI - Adaptive Programming Tutor  
**Phiên bản đóng băng kiểm toán:** `codesense-research-v1.0`  
**Ngày thực hiện kiểm toán:** 2026-09-06  
**Mục tiêu:** Chứng minh toán học và thực nghiệm xem các trường nhãn chuẩn (Ground-Truth Reference Annotations) có thể tiếp cận đầu vào của mô hình hay không, và phát hiện các con đường ô nhiễm mục tiêu (Target Contamination).

---

## 1. Ma Trận 15 Trường Nhãn Cấm (Forbidden Field Matrix)

Dưới đây là ma trận 15 trường nhãn vàng chuẩn được phân loại là **TUYỆT ĐỐI CẤM (FORBIDDEN MODEL INPUT)** và kết quả kiểm toán khả năng rò rỉ tại 3 tầng kiến trúc:
1. **Tầng Prompt Builders (`prompts.py` / `context_builder.py`)**
2. **Tầng Student Context Injection (Proposed D)**
3. **Tầng Execution Pipeline (`runner.py` / `ablation.py`)**

| STT | Trường cấm (Forbidden Field) | Kiểu dữ liệu | Tầng Prompt tĩnh | Tầng Student Context | Tầng Mock Runner V1 | Trạng thái rủi ro |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: |
| 1 | `expected_behavior` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | An toàn |
| 2 | `bug_status` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **CRITICAL** |
| 3 | `error_category` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **CRITICAL** |
| 4 | `bug_type` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **CRITICAL** |
| 5 | `bug_location` | `dict` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **CRITICAL** |
| 6 | `knowledge_components` | `list[str]` | ĐÃ CÔ LẬP | **NGUY CƠ CAO** | **RÒ RỈ (LEAKED)** | **CRITICAL** |
| 7 | `possible_misconception` | `str` | ĐÃ CÔ LẬP | **NGUY CƠ CAO** | **RÒ RỈ (LEAKED)** | **CRITICAL** |
| 8 | `reference_diagnosis` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **HIGH** |
| 9 | `evidence` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **CRITICAL** |
| 10 | `hint_1` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **HIGH** |
| 11 | `hint_2` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **HIGH** |
| 12 | `hint_3` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **HIGH** |
| 13 | `reference_solution` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ VÀO BASELINE A** | **CRITICAL** |
| 14 | `explanation_vi` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | **RÒ RỈ (LEAKED)** | **HIGH** |
| 15 | `review_status` | `str` | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | ĐÃ CÔ LẬP | An toàn |

---

## 2. Kết Quả Kiểm Tra Taint Tracking Bằng Chuỗi Sentinel

Kiểm toán viên đã gắn các chuỗi sentinel độc nhất (`TAINT_SENTINEL_*`) vào từng trường cấm của mẫu bài toán và thực thi công cụ kiểm toán ô nhiễm tự động (`artifacts/audit/taint_tracker.py`):

1. **Kiểm tra Prompt A, B, C (Tĩnh):**
   - Kết quả: **0% rò rỉ**. Không có bất kỳ chuỗi sentinel nào xuất hiện trong các prompts tĩnh của Baseline A, B hay Proposed C.
2. **Kiểm tra Prompt D (Tĩnh):**
   - Khi truyền `student_context` độc lập (tổng hợp từ lịch sử người học): **0% rò rỉ**.
   - Khi truyền `student_context` bị ô nhiễm (lấy nhãn `knowledge_components` hoặc `possible_misconception` của mẫu hiện tại): **PHÁT HIỆN RÒ RỈ 100%**.
3. **Kiểm tra Mock Runner (`runner.py`):**
   - **System A:** Phát hiện rò rỉ `reference_solution` vào `hint_1`.
   - **System B:** Phát hiện rò rỉ `reference_diagnosis`, `evidence`, `hint_3`, `explanation_vi`.
   - **System C:** Phát hiện rò rỉ 12/15 trường nhãn vàng.
   - **System D:** Phát hiện rò rỉ 12/15 trường nhãn vàng trực tiếp vào kết quả dự đoán.

---

## 3. Kết Quả Kiểm Thử Tự Động (Automated Unit Tests)

Bộ kiểm thử cô lập ô nhiễm đã được tích hợp vào hệ thống kiểm thử tự động tại `backend/tests/test_taint_isolation.py`:

```
backend/tests/test_taint_isolation.py::test_reference_solution_never_reaches_prompt PASSED [ 14%]
backend/tests/test_taint_isolation.py::test_reference_diagnosis_never_reaches_prompt PASSED [ 28%]
backend/tests/test_taint_isolation.py::test_bug_type_never_reaches_prompt PASSED [ 42%]
backend/tests/test_taint_isolation.py::test_bug_location_never_reaches_prompt PASSED [ 57%]
backend/tests/test_taint_isolation.py::test_reference_hints_never_reach_prompt PASSED [ 71%]
backend/tests/test_taint_isolation.py::test_ground_truth_dictionary_cannot_be_serialized_into_context PASSED [ 85%]
backend/tests/test_taint_isolation.py::test_proposed_d_student_context_contains_no_gold_annotations PASSED [100%]
============================== 7 passed in 0.88s ==============================
```

Toàn bộ 7 kiểm thử đơn vị đều **PASS**, xác nhận rằng giao diện tạo prompt (`prompts.py` và `context_builder.py`) được thiết kế đúng nguyên tắc phân tách trách nhiệm nếu người dùng gọi đúng cách.

---

## 4. Kiểm Toán Ô Nhiễm Mô Hình Người Học (Student-Model Contamination Audit)

Đặc biệt kiểm toán đối với **Proposed D**:
- **Nguyên tắc khoa học hợp lệ:** Bối cảnh học sinh (`student_context`) phải được sinh ra từ lịch sử tương tác trước đó, hồ sơ kỹ năng hoặc mô phỏng độc lập (independent simulated student state).
- **Phát hiện kiểm toán đối với Runner V1:**
  - Trong quá trình chạy thực nghiệm đóng băng của release `codesense-research-v1.0`, runner KHÔNG hề sử dụng một mô hình người học độc lập.
  - Thay vào đó, trong `EvaluationRunner._predict_single` (dòng 320-345), hệ thống gán trực tiếp:
    ```python
    "error_category": sample["error_category"],
    "bug_type": sample["bug_type"],
    "bug_location": sample.get("bug_location"),
    "evidence": sample.get("evidence"),
    "knowledge_components": sample.get("knowledge_components", []),
    "possible_misconception": sample.get("possible_misconception"),
    ```
  - Đây là hình thức **Target Leakage (Rò rỉ mục tiêu)** trực tiếp nhất: Nhãn cần dự đoán được sử dụng làm chính kết quả dự đoán.

---

## 5. Danh Sách Các Lỗ Hổng Rò Rỉ Đã Xác Nhận (Leakage Findings)

1. **LEAK-037-1: Direct Ground-Truth Copying in Mock Evaluation Runner**
   - *Mô tả:* Tệp `backend/app/evaluation/runner.py` và `backend/app/evaluation/ablation.py` sao chép trực tiếp các trường `error_category`, `bug_type`, `bug_location`, `evidence`, `knowledge_components`, `possible_misconception` từ `sample` vào output JSON của Proposed D và Ablation FULL.
   - *Hậu quả:* Mọi chỉ số đánh giá kỹ thuật (Diagnosis Accuracy = 100%, Localization Accuracy = 100%, Error Category Accuracy = 100%, KC F1 = 1.000) trên tập test của Proposed D đều là kết quả của việc gán nhãn tĩnh, không phải suy luận AI.
2. **LEAK-037-2: Reference Solution Leakage in Baseline A Simulation**
   - *Mô tả:* Baseline A được tạo ra với `hint_1` chứa thẳng `sample["reference_solution"]`.
   - *Hậu quả:* Chỉ số Solution Leakage Rate = 100% của Baseline A bị khuếch đại nhân tạo, làm thiên lệch tính công bằng so sánh sư phạm giữa Baseline A và Proposed C.

---

## 6. Phán Quyết Cuối Cùng & Điều Kiện Dừng (Stop Condition)

Căn cứ vào kết quả kiểm toán ô nhiễm thực nghiệm:

# PHÁN QUYẾT: LEAKED

### Thực Thi Điều Kiện Dừng (Stop Condition Protocol):
1. **Vô hiệu hóa kết quả V1 (Invalidate V1 Results):** Các kết quả thực nghiệm được báo cáo cho Proposed D tại bản phát hành `codesense-research-v1.0` (bao gồm bảng so sánh trong `results/ANALYSIS_SUMMARY.md`) chính thức bị tuyên bố **VÔ HIỆU HÓA KHOA HỌC** do lỗi rò rỉ nhãn vàng trực tiếp trong mock runner.
2. **Không sửa đổi lén lút (No Silent Fix):** Tuyệt đối giữ nguyên tập dữ liệu `VietCSharpTutor-600` và các files kết quả đã lưu trữ của V1 nhằm bảo toàn bằng chứng kiểm toán.
3. **Quy định đối với V2:** Khi thực hiện đánh giá Live LLM trên phiên bản V2, tập test đóng băng đã bị lộ cho mock runner trong quá khứ không được xem là tập kiểm định mù (uncontaminated blind test) nếu không có quy trình bảo vệ phân lập tuyệt đối ở cấp độ mạng/môi trường.
