# BÁO CÁO KIỂM TOÁN PHÂN LOẠI TRƯỜNG DỮ LIỆU VIETCSHARPTUTOR (APT-042)

> **Mã kiểm toán**: APT-042  
> **Chức danh kiểm toán**: Independent Research Auditor (Kiểm toán viên nghiên cứu độc lập)  
> **Dự án**: CodeSense AI - Adaptive Programming Tutor  
> **Bộ dữ liệu mục tiêu**: VietCSharpTutor-600 (`data/vietcsharptutor/vietcsharptutor_600.jsonl`)  
> **Phiên bản đóng băng**: `codesense-research-v1.0`  
> **Nhánh kiểm toán**: `audit/evaluation-integrity-v1`  
> **Ngày thực hiện**: 2026-09-06  

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)

Kiểm toán viên độc lập đã hoàn tất việc rà soát và truy vết mã nguồn (Source Code Tracing) cho toàn bộ **25 trường dữ liệu** của bộ chuẩn đánh giá `VietCSharpTutor-600`. Mục tiêu kiểm toán là xác định chính xác vai trò thiết kế theo tài liệu (*Intended Role*) đối chiếu với vai trò sử dụng thực tế (*Actual Role*) trong mã nguồn của hệ thống đánh giá thực nghiệm (`backend/app/evaluation/`).

### Tổng hợp phân loại theo vai trò thiết kế (Intended Roles):
- **`MODEL_INPUT`** (3 trường): `problem_statement_vi`, `student_code`, `compiler_error`.
- **`GROUND_TRUTH_ONLY`** (14 trường): `expected_behavior`, `bug_status`, `error_category`, `bug_type`, `bug_location`, `knowledge_components`, `possible_misconception`, `reference_diagnosis`, `evidence`, `hint_1`, `hint_2`, `hint_3`, `reference_solution`, `explanation_vi`.
- **`EVALUATION_METADATA`** (6 trường): `id`, `topic`, `difficulty`, `problem_family_id`, `source_type`, `split`.
- **`UNUSED`** (2 trường): `language`, `review_status`.
- **`STUDENT_CONTEXT_SOURCE`** (0 trường trực tiếp trong schema dataset, được mô phỏng từ KCs/misconceptions).

### Tổng hợp phân loại mức độ rủi ro (Risk Profile):
- **CRITICAL** (8 trường): `bug_status`, `error_category`, `bug_type`, `bug_location`, `knowledge_components`, `possible_misconception`, `evidence`, `reference_solution`.
- **HIGH** (6 trường): `topic`, `reference_diagnosis`, `hint_1`, `hint_2`, `hint_3`, `explanation_vi`.
- **REVIEW** (0 trường): 0 trường.
- **SAFE** (11 trường): `id`, `language`, `difficulty`, `problem_family_id`, `problem_statement_vi`, `student_code`, `compiler_error`, `expected_behavior`, `source_type`, `split`, `review_status`.

> [!CAUTION]
> **PHÁT HIỆN KIỂM TOÁN QUAN TRỌNG NHẤT**:  
> Toàn bộ **7/7 nhãn vàng cốt lõi** phục vụ tính điểm (`bug_status`, `error_category`, `bug_type`, `bug_location`, `evidence`, `knowledge_components`, `possible_misconception`) bị **sao chép trực tiếp 100% từ đối tượng `sample` vào kết quả dự đoán `pred`** của hệ thống Proposed D bên trong `EvaluationRunner._predict_single` (`backend/app/evaluation/runner.py` dòng 331-337).  
> Đây chính là nguyên nhân cơ bản khiến kết quả công bố của Proposed D đạt **100% Diagnosis Accuracy**, **100% Localization Accuracy**, **100% Error Category Accuracy**, và **100% Evidence Faithfulness**. Kết quả thực nghiệm này là **kết quả giả lập từ việc sao chép nhãn vàng (Ground Truth Copying)**, không phản ánh năng lực suy luận thực tế của mô hình ngôn ngữ lớn.

---

## 2. KHUNG PHÂN LOẠI DỮ LIỆU (CLASSIFICATION FRAMEWORK)

Hệ thống phân loại kiểm toán thiết lập 5 nhóm vai trò nghiêm ngặt:

1. **`MODEL_INPUT`**: Các trường dữ liệu hợp lệ duy nhất được phép đưa vào ngữ cảnh (Prompt / User Input) của mô hình ngôn ngữ lớn tại thời điểm trước khi suy luận (*Pre-Inference*).
2. **`GROUND_TRUTH_ONLY`**: Các trường nhãn vàng chuẩn do chuyên gia biên soạn, CHỈ được phép nạp sau khi mô hình đã hoàn tất sinh kết quả (*Post-Inference*) để phục vụ bộ công cụ tính chỉ số (`TutoringMetricsSuite`) hoặc xác thực.
3. **`EVALUATION_METADATA`**: Các trường dữ liệu phục vụ quản lý thực nghiệm, chia nhóm thống kê (*per-topic metrics*), lọc phân vùng dữ liệu (*split*), hoặc liên kết cặp dự đoán - nhãn vàng (`id`). Không được can thiệp vào suy luận.
4. **`STUDENT_CONTEXT_SOURCE`**: Các trường dùng để tổng hợp hồ sơ người học (ví dụ: lịch sử thử nghiệm, KCs đang gặp khó khăn). Tuyệt đối không được lấy trực tiếp nhãn vàng của ca hiện tại để gán vào bối cảnh người học.
5. **`UNUSED`**: Các trường chỉ tồn tại mang tính quy ước chuẩn hóa trong schema JSON, hoàn toàn không tham gia vào bất kỳ pha nào của pipeline đánh giá.

---

## 3. BẢNG PHÂN LOẠI CHI TIẾT 25 TRƯỜNG DỮ LIỆU (DATASET FIELD MATRIX)

Bảng ma trận truy vết đầy đủ 25 trường của bộ dữ liệu `VietCSharpTutor-600` (được lưu trữ tại `artifacts/audit/dataset_field_matrix.csv`):

| STT | Tên trường | Intended Role | Actual Role | Model-Visible | Pre-Inf | Post-Inf | Validator | Metrics | Mức rủi ro | Vị trí mã nguồn thực tế |
|---|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| 1 | `id` | EVALUATION_METADATA | EVALUATION_METADATA | No | Yes | Yes | Yes | Yes | **SAFE** | `runner.py:206,225,258,291,324; metrics.py:170; validate_vietcsharptutor.py:82` |
| 2 | `language` | EVALUATION_METADATA | UNUSED | No | No | No | Yes | No | **SAFE** | `validate_vietcsharptutor.py:86` |
| 3 | `topic` | EVALUATION_METADATA | EVALUATION_METADATA | No | Yes | Yes | Yes | Yes | **HIGH** | `runner.py:207; metrics.py:174; validate_vietcsharptutor.py:90` |
| 4 | `difficulty` | EVALUATION_METADATA | EVALUATION_METADATA | No | No | No | Yes | No | **SAFE** | `validate_vietcsharptutor.py:93` |
| 5 | `problem_family_id` | EVALUATION_METADATA | EVALUATION_METADATA | No | No | No | Yes | No | **SAFE** | `validate_vietcsharptutor.py:96,197` |
| 6 | `problem_statement_vi` | MODEL_INPUT | MODEL_INPUT | Yes | Yes | No | Yes | No | **SAFE** | `prompts.py:25,42,72,105; validate_vietcsharptutor.py:156,189` |
| 7 | `student_code` | MODEL_INPUT | MODEL_INPUT | Yes | Yes | Yes | Yes | Yes | **SAFE** | `prompts.py:25,42,72,105; metrics.py:259; validate_vietcsharptutor.py:151,156,190` |
| 8 | `compiler_error` | MODEL_INPUT | MODEL_INPUT | Yes | Yes | No | No | No | **SAFE** | `prompts.py:25,42,72,107` |
| 9 | `expected_behavior` | GROUND_TRUTH_ONLY | UNUSED | No | No | No | Yes | No | **SAFE** | `validate_vietcsharptutor.py:156` |
| 10 | `bug_status` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **CRITICAL** | `runner.py:208,221,254,288,321; metrics.py:239; validate_vietcsharptutor.py:99,120` |
| 11 | `error_category` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **CRITICAL** | `runner.py:233,266,299,332; metrics.py:228; validate_vietcsharptutor.py:102,121` |
| 12 | `bug_type` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **CRITICAL** | `runner.py:234,267,300,333; metrics.py:246; validate_vietcsharptutor.py:122,128,145` |
| 13 | `bug_location` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **CRITICAL** | `runner.py:235,268,301,334; metrics.py:252; validate_vietcsharptutor.py:129` |
| 14 | `knowledge_components` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **CRITICAL** | `runner.py:237,270,303,336; metrics.py:232; validate_vietcsharptutor.py:114` |
| 15 | `possible_misconception` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **CRITICAL** | `runner.py:238,271,304,337; metrics.py:272; validate_vietcsharptutor.py:133,139` |
| 16 | `reference_diagnosis` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | No | Yes | No | **HIGH** | `runner.py:275,308,341; validate_vietcsharptutor.py:157` |
| 17 | `evidence` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **CRITICAL** | `runner.py:236,269,302,335; metrics.py:256; validate_vietcsharptutor.py:131,147` |
| 18 | `hint_1` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **HIGH** | `runner.py:305,338; metrics.py:111,131; validate_vietcsharptutor.py:157` |
| 19 | `hint_2` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **HIGH** | `runner.py:306,339; metrics.py:111,132; validate_vietcsharptutor.py:157` |
| 20 | `hint_3` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | Yes | Yes | Yes | **HIGH** | `runner.py:274,307,340; metrics.py:133; validate_vietcsharptutor.py:157` |
| 21 | `reference_solution` | GROUND_TRUTH_ONLY | GROUND_TRUTH_LEAKED_TO_PRED | No | Yes | Yes | Yes | Yes | **CRITICAL** | `runner.py:239; ablation.py:249,265,305,321; metrics.py:108,264; validate_vietcsharptutor.py:158` |
| 22 | `explanation_vi` | GROUND_TRUTH_ONLY | GROUND_TRUTH_COPIED_TO_PRED | No | Yes | No | Yes | No | **HIGH** | `runner.py:276,309,342; validate_vietcsharptutor.py:158` |
| 23 | `source_type` | EVALUATION_METADATA | EVALUATION_METADATA | No | No | No | Yes | No | **SAFE** | `validate_vietcsharptutor.py:108` |
| 24 | `split` | EVALUATION_METADATA | EVALUATION_METADATA | No | Yes | No | Yes | No | **SAFE** | `runner.py:120; validate_vietcsharptutor.py:105,199` |
| 25 | `review_status` | EVALUATION_METADATA | UNUSED | No | No | No | Yes | No | **SAFE** | `validate_vietcsharptutor.py:111` |

---

## 4. TRẢ LỜI 6 CÂU HỎI KIỂM TOÁN THEN CHỐT (AUDIT QUESTIONS DEEP DIVE)

### Câu hỏi 1: Trường `expected_behavior` có bị lộ vào mô hình hoặc prompt đánh giá không?
- **Kết luận**: **KHÔNG (SAFE)**.
- **Bằng chứng mã nguồn**:
  - Trong `backend/app/evaluation/prompts.py`, cả 4 hàm dựng prompt (`build_prompt_a`, `build_prompt_b`, `build_prompt_c`, `build_prompt_d`) chỉ nhận `problem_statement`, `student_code`, `compiler_error` và `student_context`. Trường `expected_behavior` không hề được truyền vào.
  - Trong `backend/app/evaluation/runner.py`, `expected_behavior` không được trích xuất trong `_predict_single`.
  - Trong `backend/app/evaluation/metrics.py`, không có bất kỳ hàm metric nào tham chiếu tới `expected_behavior`.
- **Đánh giá**: Trường này hoàn toàn được cô lập an toàn khỏi luồng thực thi.

### Câu hỏi 2: Trường `reference_solution` có được cô lập nghiêm ngặt đến sau suy luận không?
- **Kết luận**: **KHÔNG ĐƯỢC CÔ LẬP (CRITICAL VIOLATION)**.
- **Bằng chứng mã nguồn**:
  - Trong prompt builder (`prompts.py`), `reference_solution` không xuất hiện.
  - Tuy nhiên, trong `backend/app/evaluation/runner.py` dòng 239 (Baseline A mock generator):
    ```python
    "hint_1": f"Mã sửa lại như sau:\n```csharp\n{sample.get('reference_solution', '')}\n```"
    ```
    Mã nguồn giải pháp chuẩn bị runner đọc trước suy luận và bơm trực tiếp vào trường dự đoán `hint_1` của Baseline A để tạo ra mẫu thử nghiệm rò rỉ.
  - Tương tự trong `backend/app/evaluation/ablation.py`:
    - Dòng 265 (`NO_PROGRESSIVE_HINT`): `hint_1` được gán bằng `reference_solution`.
    - Dòng 321 (`DIRECT_BASELINE`): `hint_1` được gán bằng `reference_solution`.
- **Đánh giá**: Việc mock runner trực tiếp truy cập vào `sample['reference_solution']` trước suy luận vi phạm nghiêm trọng nguyên tắc cô lập ground truth. Khi đánh giá bằng mock runner, điều này dẫn đến việc Solution Leakage Rate của Baseline A luôn bằng 100%.

### Câu hỏi 3: Trường `reference_diagnosis` có xuất hiện khi dựng prompt không?
- **Kết luận**: **KHÔNG xuất hiện trong Prompt, nhưng BỊ RÒ RỈ vào Predictions (HIGH RISK)**.
- **Bằng chứng mã nguồn**:
  - Trong `prompts.py`, `reference_diagnosis` chỉ xuất hiện trong phần mô tả JSON schema output mong muốn (dòng 91, 132), không truyền nội dung giá trị mẫu vào prompt text.
  - Tuy nhiên, trong mock runner (`runner.py`):
    - Baseline B (dòng 275): `"reference_diagnosis": sample.get("reference_diagnosis", "Cần xem lại bài làm.")`
    - Proposed C (dòng 308): `"reference_diagnosis": sample.get("reference_diagnosis", "Chẩn đoán cấu trúc.")`
    - Proposed D (dòng 341): `"reference_diagnosis": sample.get("reference_diagnosis", "Chẩn đoán cá nhân hóa chính xác.")`
  - Trường nhãn vàng của chuyên gia bị chép nguyên văn sang kết quả dự đoán.

### Câu hỏi 4: Các trường `bug_type`, `error_category`, `bug_location` có bị rò rỉ vào context không?
- **Kết luận**: **RÒ RỈ TOÀN BỘ VÀO OUTPUT DỰ ĐOÁN CỦA PROPOSED D (CRITICAL LEAKAGE)**.
- **Bằng chứng mã nguồn**:
  - Trong `backend/app/evaluation/runner.py` dòng 331-334:
    ```python
    pred_status = gt_status if is_diag_correct else gt_status
    ...
    "bug_status": pred_status,
    "error_category": sample["error_category"],
    "bug_type": sample["bug_type"],
    "bug_location": sample.get("bug_location"),
    ```
  - Trong hệ thống Proposed D, `error_category`, `bug_type`, và `bug_location` không hề được suy luận từ mã nguồn học sinh mà được gán thẳng từ đối tượng `sample` ground truth!
  - Khi `metrics.py` so sánh:
    - `pred.get("error_category") == gt.get("error_category")` -> luôn `True` (100% Accuracy).
    - `check_localization(pred.get("bug_location"), gt.get("bug_location"))` -> luôn `True` (100% Accuracy).
- **Đánh giá**: Đây là nguyên nhân trực tiếp tạo ra kết quả hoàn hảo 100% của Proposed D trên tập test split.

### Câu hỏi 5: Trường `topic` có làm lộ ngữ nghĩa bài toán hoặc tạo shortcut không?
- **Kết luận**: **CÓ NGUY CƠ TẠO SHORTCUT CỰC KỲ CAO (HIGH RISK)**.
- **Bằng chứng ngữ nghĩa và mã nguồn**:
  - Trong `vietcsharptutor_600.jsonl`, tập nhãn của `topic` gồm 10 giá trị:
    1. `correct_code`: 100% mẫu có `bug_status = "no_bug"`, `error_category = "no_bug"`, `bug_type = "no_bug"`.
    2. `insufficient_context`: 100% mẫu có `bug_status = "insufficient_context"`, `error_category = "insufficient_context"`.
    3. 8 chủ đề OOP còn lại: 100% mẫu có `bug_status = "has_bug"`.
  - Trong `runner.py` dòng 207: Biến `topic = sample["topic"]` được đọc ra ngay đầu hàm `_predict_single`.
  - Mặc dù `prompts.py` không chèn `topic` vào prompt text, nếu bất kỳ thành phần nào (như heuristics phân loại, student context builder, hay mock engine) truy cập `sample["topic"]`, nó có thể phân loại chính xác tuyệt đối `bug_status` mà không cần đọc một dòng mã `student_code` nào.
- **Đánh giá**: `topic` là một kênh rò rỉ ngữ nghĩa tiềm tàng (Semantic Shortcut Channel). Cần phải loại bỏ trường này khỏi bộ nhớ trước suy luận.

### Câu hỏi 6: Các tầng gợi ý `hint_1`, `hint_2`, `hint_3` có được giữ kín khỏi model context không?
- **Kết luận**: **KHÔNG ĐƯỢC GIỮ KÍN TRONG MOCK RUNNER (HIGH RISK)**.
- **Bằng chứng mã nguồn**:
  - Trong prompt builder (`prompts.py`), các trường gợi ý không được truyền vào prompt.
  - Tuy nhiên, trong mock runner (`runner.py` dòng 338-340 cho Proposed D và 305-307 cho Proposed C):
    ```python
    "hint_1": sample.get("hint_1", "Quan sát lại cách thức cấp phát bộ nhớ."),
    "hint_2": sample.get("hint_2", "Trong mô hình OOP, thực thể cần được định danh rõ ràng."),
    "hint_3": sample.get("hint_3", "Hãy thực hiện thao tác gán tương ứng."),
    ```
  - Mock runner lấy trực tiếp các gợi ý vàng do chuyên gia biên soạn để làm output dự đoán.
  - Do các gợi ý vàng trong `vietcsharptutor_600.jsonl` được thiết kế chuẩn xác tuân thủ chính sách 3 bậc (Hint 1 không lộ mã giải pháp, Hint 2 giải thích khái niệm, Hint 3 hướng dẫn hành động), việc gán trực tiếp này khiến chỉ số `hint_policy_compliance` của Proposed D đạt 100% và `solution_leakage_rate` đạt 0%.
- **Đánh giá**: Điểm tuân thủ chính sách gợi ý của Proposed D là kết quả sao chép từ nhãn vàng, không phản ánh năng lực sinh ngôn ngữ có kiểm soát của mô hình AI.

---

## 5. PHÂN TÍCH VẾT RÒ RỈ MÃ NGUỒN (SOURCE CODE TRACE & EVIDENCE)

Dưới đây là chi tiết mã nguồn trong `backend/app/evaluation/runner.py` chứng minh hiện tượng **Ground Truth Copying**:

```python
# Trích đoạn backend/app/evaluation/runner.py: dòng 314-345
elif self.system == "D":
    prompt_tokens = random.randint(520, 720)
    completion_tokens = random.randint(320, 500)
    
    is_diag_correct = (random.random() < 0.97)
    pred_status = gt_status if is_diag_correct else gt_status
    
    return {
        "id": sample_id,
        "model": self.model,
        "provider": self.provider,
        "prompt_version": self.prompt_version,
        "latency_ms": simulated_latency,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "bug_status": pred_status,                    # <-- Bị gán trực tiếp gt_status
        "error_category": sample["error_category"],    # <-- BỊ GÁN TRỰC TIẾP TỪ SAMPLE
        "bug_type": sample["bug_type"],                # <-- BỊ GÁN TRỰC TIẾP TỪ SAMPLE
        "bug_location": sample.get("bug_location"),    # <-- BỊ GÁN TRỰC TIẾP TỪ SAMPLE
        "evidence": sample.get("evidence"),            # <-- BỊ GÁN TRỰC TIẾP TỪ SAMPLE
        "knowledge_components": sample.get("knowledge_components", []), # <-- BỊ GÁN TRỰC TIẾP
        "possible_misconception": sample.get("possible_misconception"), # <-- BỊ GÁN TRỰC TIẾP
        "hint_1": sample.get("hint_1", "..."),        # <-- BỊ GÁN TRỰC TIẾP TỪ SAMPLE
        "hint_2": sample.get("hint_2", "..."),        # <-- BỊ GÁN TRỰC TIẾP TỪ SAMPLE
        "hint_3": sample.get("hint_3", "..."),        # <-- BỊ GÁN TRỰC TIẾP TỪ SAMPLE
        "reference_diagnosis": sample.get("reference_diagnosis", "..."),
        "explanation_vi": sample.get("explanation_vi", "..."),
        "json_valid": True,
        "validator_actions": ["student_model_context_injected", "structured_schema_verified", "evidence_grounded"]
    }
```

Bảng đối chiếu điểm số báo cáo của Proposed D và nguồn gốc dữ liệu:

| Chỉ số đánh giá | Kết quả báo cáo | Cơ chế tính điểm trong `metrics.py` | Nguồn gốc dữ liệu trong `runner.py` | Kết luận kiểm toán |
|---|:---:|---|---|---|
| **Diagnosis Accuracy** | **100.0%** | `pred['bug_status'] == gt['bug_status']` và match `bug_type`/`error_category` | `pred_status = gt_status`; `sample['bug_type']` | **Nhân tạo (Chép nhãn vàng)** |
| **Bug Localization Acc** | **100.0%** | `check_localization(pred['bug_location'], gt['bug_location'])` | `sample.get('bug_location')` | **Nhân tạo (Chép nhãn vàng)** |
| **Error Category Acc** | **100.0%** | `pred['error_category'] == gt['error_category']` | `sample['error_category']` | **Nhân tạo (Chép nhãn vàng)** |
| **Knowledge Component F1** | **1.0000** | Giao tập `pred['knowledge_components']` và `gt['knowledge_components']` | `sample.get('knowledge_components', [])` | **Nhân tạo (Chép nhãn vàng)** |
| **Misconception Acc** | **100.0%** | So khớp từ khóa với `gt['possible_misconception']` | `sample.get('possible_misconception')` | **Nhân tạo (Chép nhãn vàng)** |
| **Evidence Faithfulness** | **100.0%** | `pred['evidence'] in gt['student_code']` | `sample.get('evidence')` | **Nhân tạo (Chép nhãn vàng)** |
| **Solution Leakage Rate** | **0.0%** | Kiểm tra `gt['reference_solution'] in pred['hint_1/2']` | Nhãn vàng `hint_1`, `hint_2` chuẩn | **Nhân tạo (Chép nhãn vàng)** |
| **Hint Policy Compliance** | **100.0%** | Kiểm tra cú pháp gợi ý 3 tầng | Nhãn vàng `hint_1`, `hint_2`, `hint_3` | **Nhân tạo (Chép nhãn vàng)** |

---

## 6. KHUYẾN NGHỊ KIỂM TOÁN (AUDITOR RECOMMENDATIONS)

Để đảm bảo tính trung thực khoa học của công trình nghiên cứu và khôi phục giá trị thực nghiệm của benchmark, kiểm toán viên đề xuất các giải pháp kiến trúc độc lập:

1. **Thiết lập ranh giới dữ liệu cách ly tuyệt đối (Data Isolation Boundary)**:
   - Tách rời hoàn toàn cấu trúc dữ liệu nạp vào:
     - `SampleInput`: Chỉ chứa `id`, `problem_statement_vi`, `student_code`, `compiler_error`.
     - `SampleGroundTruth`: Chứa 21 trường còn lại, được niêm phong trong bộ lưu trữ riêng và CHỈ được nạp vào lúc chạy hàm `TutoringMetricsSuite.evaluate()`.
   - `EvaluationRunner` tuyệt đối không được nhận đối tượng chứa các trường `GROUND_TRUTH_ONLY`.

2. **Xóa bỏ hoàn toàn cơ chế gán nhãn trong Mock Runner**:
   - Mock runner cho môi trường CI/CD phải được viết bằng mô hình giả lập ngẫu nhiên hoặc các quy tắc heuristics đơn giản (naive heuristics) độc lập hoàn toàn với `sample`.
   - Các báo cáo nghiên cứu chính thức TUYỆT ĐỐI KHÔNG được sử dụng kết quả sinh ra từ mock runner. Phải chạy suy luận trực tiếp từ các LLM thực tế (Gemini 1.5 Pro, Claude 3.5 Sonnet, GPT-4o).

3. **Loại bỏ Shortcut ngữ nghĩa của trường `topic`**:
   - Trường `topic` không được xuất hiện trong pipeline trước và trong khi suy luận.
   - Khi chia split và tính metrics theo chủ đề, trường `topic` chỉ được join lại thông qua khóa `id` tại bước cuối cùng của `metrics.py`.

4. **Thực thi Kiểm toán Độc lập Runtime (Taint Tracking Guard)**:
   - Thêm bộ decorator `@isolated_inference` kiểm tra tại thời điểm runtime: nếu phát hiện bất kỳ trường nào thuộc nhóm `GROUND_TRUTH_ONLY` xuất hiện trong tham số hàm suy luận hoặc mock generator, hệ thống sẽ raise `SecurityTaintViolationError` và hủy bỏ run thực nghiệm ngay lập tức.

---

## 7. KẾT LUẬN KIỂM TOÁN

Đợt kiểm toán **APT-042** đã xác định chính xác và minh bạch vị trí, vai trò thiết kế và hành vi sử dụng thực tế của 25 trường dữ liệu `VietCSharpTutor`.

Các kết quả đánh giá 100% được công bố trong đợt phát hành `codesense-research-v1.0` không phải do sự vượt trội về thuật toán prompt hay năng lực mô hình, mà là hệ quả trực tiếp của **sự cố rò rỉ mã nguồn nghiêm trọng (Ground Truth Copying) trong mock evaluation runner**.

Báo cáo này cung cấp đầy đủ bằng chứng mã nguồn và cơ sở dữ liệu làm tiền đề bắt buộc cho các bước kiểm toán cô lập tiếp theo.
