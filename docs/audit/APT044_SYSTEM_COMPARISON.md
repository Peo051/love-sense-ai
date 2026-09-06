# BÁO CÁO SO SÁNH CÓ KIỂM SOÁT 4 HỆ THỐNG ĐÁNH GIÁ (APT-044)

> **Mã kiểm toán**: APT-044  
> **Chức danh kiểm toán**: Independent Research Auditor (Kiểm toán viên nghiên cứu độc lập)  
> **Dự án**: CodeSense AI - Adaptive Programming Tutor  
> **Phiên bản đóng băng**: `codesense-research-v1.0`  
> **Nhánh kiểm toán**: `audit/evaluation-integrity-v1`  
> **Ngày thực hiện**: 2026-09-06  

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)

Nhiệm vụ kiểm toán độc lập **APT-044** thực hiện so sánh có kiểm soát (Controlled Comparison) giữa 4 hệ thống đánh giá thực nghiệm: **Baseline A**, **Baseline B**, **Proposed C**, và **Proposed D** dựa trên mã nguồn triển khai thực tế (`backend/app/evaluation/`), tách biệt hoàn toàn khỏi các tuyên bố trong tài liệu README hoặc bài báo nghiên cứu.

### Các phát hiện kiểm toán mang tính quyết định:
1. **Thiết kế dự kiến lý thuyết**: Nghiên cứu tuyên bố rằng `Proposed D = Proposed C + Student Context`, nhằm trả lời câu hỏi nghiên cứu RQ3 về giá trị gia tăng của mô hình người học.
2. **Thực tế mã nguồn**: `StudentContextBuilder` **hoàn toàn không được triệu gọi** trong luồng thực nghiệm của Proposed D. Không có bất kỳ dữ liệu bối cảnh người học nào (lịch sử thử, KCs yếu kém, quan niệm sai lầm cũ) được nạp vào.
3. **Yếu tố nhiễu chết người giữa C và D (Critical Confounder)**:
   - Trong Hệ thống C: Bộ mock engine cài đặt tỷ lệ ngẫu nhiên `is_diag_correct = random < 0.92` (tạo ra khoảng 8% lỗi mô phỏng).
   - Trong Hệ thống D: Dòng 321 viết `pred_status = gt_status if is_diag_correct else gt_status` (luôn luôn đúng 100%), và toàn bộ 100% các trường nhãn vàng khác được gán trực tiếp từ `sample` sang `pred` mà không hề qua kiểm tra ngẫu nhiên!
   - **Kết luận khoa học**: Khoảng cách hiệu năng 100% vs 92% giữa D và C **hoàn toàn là do lập trình viên cố ý gán nhãn vàng 100% cho D trong code mock**, không phản ánh bất kỳ tác động nhân quả (causal effect) nào của Student Context.
4. **Yếu tố nhiễu nhiệt độ (Temperature Confounder)**: Baseline A và B chạy ở `temperature = 0.7`, trong khi Proposed C và D chạy ở `temperature = 0.2`. Đây là yếu tố gây nhiễu vi phạm nguyên tắc biến kiểm soát (controlled variable).

---

## 2. BẢNG SO SÁNH 16 THUỘC TÍNH (SYSTEM COMPARISON MATRIX)

| STT | Thuộc tính (`Property`) | Baseline A | Baseline B | Proposed C | Proposed D | Phân loại kiểm toán |
|:---:|---|---|---|---|---|:---:|
| 1 | **`provider`** | mock | mock | mock | mock | **INTENDED** |
| 2 | **`model`** | mock-tutor-v1 | mock-tutor-v1 | mock-tutor-v1 | mock-tutor-v1 | **INTENDED** |
| 3 | **`system_prompt`** | Lập trình viên C# chuyên nghiệp (tìm lỗi và viết lại mã đã sửa) | Gia sư AI dạy lập trình C# thân thiện (giải thích lỗi và gợi ý) | CodeSense AI Tutor chuyên sâu (chẩn đoán cấu trúc + gợi ý 3 tầng JSON) | CodeSense AI Tutor thích ứng (chẩn đoán + gợi ý 3 tầng + cá nhân hóa theo ZPD) | **INTENDED** |
| 4 | **`user_prompt`** | build_prompt_a (Yêu cầu tìm lỗi và cung cấp mã sửa hoàn chỉnh) | build_prompt_b (Yêu cầu hướng dẫn giải quyết vấn đề tự do bằng tiếng Việt) | build_prompt_c (Yêu cầu xuất JSON schema 12 trường) | build_prompt_d (Nhận thêm bối cảnh học viên + yêu cầu xuất JSON schema 12 trường) | **INTENDED (Nhưng BỊ BỎ QUA trong runner)** |
| 5 | **`few_shot_examples`** | None (Zero-shot) | None (Zero-shot) | None (Zero-shot) | None (Zero-shot) | **INTENDED** |
| 6 | **`model_visible_fields`** | problem_statement, student_code, compiler_error | problem_statement, student_code, compiler_error | problem_statement, student_code, compiler_error | problem_statement, student_code, compiler_error, student_context (lý thuyết) | **CRITICAL (Thực tế mock nhìn thấy cả 25 trường)** |
| 7 | **`student_context`** | None | None | None | attempt_count, struggling_kcs, recent_misconceptions (lý thuyết) | **CRITICAL (Vắng mặt hoàn toàn trong thực thi)** |
| 8 | **`temperature`** | 0.7 | 0.7 | 0.2 | 0.2 | **CONFOUNDING** |
| 9 | **`max_tokens`** | 1024 | 1024 | 1024 | 1024 | **INTENDED** |
| 10 | **`retry_count`** | 0 | 0 | 0 | 0 | **INTENDED** |
| 11 | **`output_schema`** | Unstructured text (Chứa mã sửa lại) | Unstructured text (Giải thích thân thiện) | Structured JSON (12 trường bắt buộc) | Structured JSON (12 trường bắt buộc) | **INTENDED** |
| 12 | **`validator`** | None (Hardcoded log: ['direct_prompt_parsed']) | None (Hardcoded log: ['generic_tutor_parsed']) | None (Hardcoded log: ['structured_schema_verified', 'evidence_grounded']) | None (Hardcoded log: ['student_model_context_injected', 'structured_schema_verified', 'evidence_grounded']) | **CONFOUNDING** |
| 13 | **`fallback`** | None | None | None | None | **INTENDED** |
| 14 | **`mock_implementation`** | Cố ý tạo false positive 35%, max acc 65%, gán reference_solution vào hint_1 | Cố ý tạo false positive 20%, max acc 75%, gán evidence vào hint_2, copy hints/diag | Giả lập p < 0.92, copy ground truth khi đúng, gán lỗi khi sai | 100% DIRECT COPY từ sample sang pred, không có nhánh sai, không có ngẫu nhiên | **CRITICAL (Gian lận thực nghiệm trực tiếp)** |
| 15 | **`cache_behavior`** | Deterministic seed = 42 | Deterministic seed = 42 | Deterministic seed = 42 | Deterministic seed = 42 | **INTENDED** |
| 16 | **`post_processing`** | Tạo prediction dict trực tiếp | Tạo prediction dict trực tiếp | Tạo prediction dict trực tiếp | Tạo prediction dict trực tiếp | **INTENDED** |

---

## 3. PHÂN TÍCH SO SÁNH TỪNG CẶP (PAIRWISE COMPARISONS)

### Baseline A (Direct Debugging) vs Baseline B (Generic Tutor)
**1. Khác biệt dự kiến (Intended Differences):**
- Persona: Kỹ sư sửa code (A) vs Gia sư sư phạm thân thiện (B).
- Mục tiêu đầu ra: Cung cấp mã đã sửa (A) vs Hướng dẫn giải quyết vấn đề (B).

**2. Yếu tố gây nhiễu (Confounding Factors):**
- Cả hai cùng chạy ở temperature = 0.7.
- Tỷ lệ False Positive cố ý được cài đặt khác nhau (35% ở A vs 20% ở B).

**3. Sai phạm / Lỗi nghiêm trọng (Critical Flaws):**
- Baseline A bị lập trình viên hardcode nhúng trực tiếp 'reference_solution' vào hint_1 để ép buộc Solution Leakage Rate luôn bằng 100%.


### Baseline B (Generic Tutor) vs Proposed C (Structured Diagnosis)
**1. Khác biệt dự kiến (Intended Differences):**
- Định dạng đầu ra: Văn bản tự do không cấu trúc (B) vs Đối tượng JSON cấu trúc 12 trường (C).
- Chiến lược gợi ý: Gợi ý chung chung (B) vs Chính sách 3 bậc thang gợi ý sư phạm (C).

**2. Yếu tố gây nhiễu (Confounding Factors):**
- Temperature Confounder: Baseline B chạy ở temp = 0.7, Proposed C chạy ở temp = 0.2. Nhiệt độ thấp hơn ở C làm tăng độ ổn định cấu trúc và tuân thủ schema, làm sai lệch so sánh công bằng.
- Prompt length chênh lệch lớn (B ngắn, C rất chi tiết với 8 quy tắc ràng buộc).

**3. Sai phạm / Lỗi nghiêm trọng (Critical Flaws):**
- Xác suất chính xác trong mock engine được ấn định cứng: B đạt tối đa 75%, trong khi C đạt 92%.


### Proposed C (Structured Progressive) vs Proposed D (Contextual Adaptive)
**1. Khác biệt dự kiến (Intended Differences):**
- Theo thiết kế lý thuyết: Proposed D = Proposed C + Student Context (Bối cảnh người học).

**2. Yếu tố gây nhiễu (Confounding Factors):**
- Token giả lập: D được gán prompt_tokens và completion_tokens cao hơn C (520-720 vs 450-600).
- Validator log: D tự động thêm log 'student_model_context_injected' dù không có context builder nào chạy.

**3. Sai phạm / Lỗi nghiêm trọng (Critical Flaws):**
- VẮNG MẶT STUDENT CONTEXT: Trong runner.py, biến student_context hoàn toàn không tồn tại, StudentContextBuilder không được gọi.
- GROUND TRUTH COPYING DISCREPANCY: Trong C, có kiểm tra ngẫu nhiên 'is_diag_correct = random < 0.92' (có 8% mẫu sai). Nhưng trong D, 'pred_status = gt_status if is_diag_correct else gt_status' (luôn đúng 100%), và 100% các trường vàng khác được gán trực tiếp không qua kiểm tra ngẫu nhiên.
- KẾT LUẬN C vs D: Khoảng chênh lệch hiệu năng giữa C (92%) và D (100%) KHÔNG PHẢI do bối cảnh người học mang lại, mà là do code mock của D sao chép 100% nhãn vàng không cài đặt tỷ lệ lỗi!


---

## 4. PHÂN TÍCH CHUYÊN SÂU: PROPOSED C VS PROPOSED D (`C_vs_D_diff`)

Đây là phép so sánh cốt lõi quyết định tính trung thực khoa học của toàn bộ công trình CodeSense AI.

### 4.1. Đối chiếu Giả định Nghiên cứu vs Thực tế Triển khai
```
GIẢ ĐỊNH THIẾT KẾ:  D = C + Student Context
THỰC TẾ MÃ NGUỒN:   D = 100% Ground Truth Copying (Không có Student Context)
```

### 4.2. So sánh từng dòng mã nguồn trong `backend/app/evaluation/runner.py`

```python
# --- HỆ THỐNG C (runner.py: dòng 283-312) ---
elif self.system == "C":
    is_diag_correct = (random.random() < 0.92)  # <-- CÓ TỶ LỆ LỖI 8%
    pred_status = gt_status if is_diag_correct else ("has_bug" if gt_status != "has_bug" else "no_bug")
    return {
        "bug_status": pred_status,
        "error_category": sample["error_category"] if is_diag_correct else "compile_error",
        "bug_type": sample["bug_type"] if is_diag_correct else "oop_structure_error",
        "bug_location": sample.get("bug_location") if is_diag_correct else None,
        "evidence": sample.get("evidence") if is_diag_correct else None,
        "knowledge_components": sample.get("knowledge_components", []) if is_diag_correct else ["OOP.Classes"],
        ...
    }

# --- HỆ THỐNG D (runner.py: dòng 316-345) ---
elif self.system == "D":
    is_diag_correct = (random.random() < 0.97)
    pred_status = gt_status if is_diag_correct else gt_status  # <-- BUG/TRICK: LUÔN BẰNG gt_status!
    return {
        "bug_status": pred_status,                    # <-- 100% ĐÚNG
        "error_category": sample["error_category"],    # <-- GÁN THẲNG, KHÔNG CÓ NHÁNH ELSE!
        "bug_type": sample["bug_type"],                # <-- GÁN THẲNG, KHÔNG CÓ NHÁNH ELSE!
        "bug_location": sample.get("bug_location"),    # <-- GÁN THẲNG, KHÔNG CÓ NHÁNH ELSE!
        "evidence": sample.get("evidence"),            # <-- GÁN THẲNG, KHÔNG CÓ NHÁNH ELSE!
        "knowledge_components": sample.get("knowledge_components", []), # <-- GÁN THẲNG!
        "possible_misconception": sample.get("possible_misconception"), # <-- GÁN THẲNG!
        ...
    }
```

### 4.3. Bảng phân tích chi tiết các điểm sai lệch giữa C và D

| Tiêu chí so sánh | Hệ thống C | Hệ thống D | Tác động khoa học | Phân loại |
|---|---|---|---|:---:|
| **Sự hiện diện của Student Context** | Không | **KHÔNG** (bị bỏ qua trong code) | Vi phạm định nghĩa hệ thống D | **CRITICAL** |
| **Tỷ lệ chẩn đoán đúng giả lập** | 92% (có 8% giả lập sai) | **100%** (`pred_status = gt_status`) | Tạo ưu thế nhân tạo cho D | **CRITICAL** |
| **Gán nhãn vàng `error_category`** | Có điều kiện (`if is_diag_correct`) | **Gán trực tiếp vô điều kiện** | Tạo 100% Cat Acc nhân tạo | **CRITICAL** |
| **Gán nhãn vàng `bug_location`** | Có điều kiện (`if is_diag_correct`) | **Gán trực tiếp vô điều kiện** | Tạo 100% Loc Acc nhân tạo | **CRITICAL** |
| **Gán nhãn vàng `evidence`** | Có điều kiện (`if is_diag_correct`) | **Gán trực tiếp vô điều kiện** | Tạo 100% Faithfulness nhân tạo | **CRITICAL** |
| **Gán nhãn vàng `knowledge_components`** | Có điều kiện (`if is_diag_correct`) | **Gán trực tiếp vô điều kiện** | Tạo F1 = 1.0 nhân tạo | **CRITICAL** |
| **Gán nhãn vàng `possible_misconception`** | Có điều kiện (`if is_diag_correct`) | **Gán trực tiếp vô điều kiện** | Tạo 100% Misc Acc nhân tạo | **CRITICAL** |
| **Validator Actions log** | `schema_verified`, `evidence_grounded` | Thêm chuỗi `student_model_context_injected` | Ghi log giả mạo sự hiện diện của context | **CONFOUNDING** |

---

## 5. ĐÁNH GIÁ TÍNH HỢP LỆ KHOA HỌC (SCIENTIFIC VALIDITY ASSESSMENT)

Một thí nghiệm khoa học chỉ có giá trị khi sự khác biệt về kết quả đầu ra giữa nhóm đối chứng (Control) và nhóm can thiệp (Treatment) được cô lập nhân quả (causally attributable) từ biến độc lập duy nhất được khảo sát.

Trong trường hợp CodeSense AI:
- **Biến độc lập tuyên bố**: Sự bổ sung của mô hình người học (Student Context).
- **Biến can thiệp thực tế**: Một đoạn mã Python gán thẳng 100% nhãn vàng từ bộ dữ liệu sang kết quả đầu ra trong mock engine, kết hợp với việc xóa bỏ hoàn toàn nhánh tạo lỗi ngẫu nhiên vốn có ở hệ thống C.
- **Hệ quả**: Bất kỳ kết luận nào cho rằng 'Student Context giúp tăng Diagnosis Accuracy từ 92% lên 100%' hoặc 'tăng Localization Accuracy từ 92% lên 100%' đều là **kết luận sai sự thật khoa học** do bị chi phối bởi yếu tố gian lận thực nghiệm (Experimental Cheating / Confounding Bias).

---

## 6. KẾT LUẬN KIỂM TOÁN

Nhiệm vụ kiểm toán **APT-044** đã vạch rõ toàn bộ các yếu tố gây nhiễu và gian lận cấu trúc trong 4 hệ thống đánh giá:
1. Baseline A bị ép buộc có rò rỉ giải pháp (Solution Leakage) bằng cách hardcode `reference_solution` vào output.
2. Baseline A/B và Proposed C/D bị phân tách bởi biến gây nhiễu nhiệt độ (temperature = 0.7 vs 0.2).
3. Proposed D hoàn toàn không chứa Student Context trong luồng thực thi; điểm số 100% của Proposed D là kết quả trực tiếp của việc sao chép nhãn vàng không điều kiện trong mock runner.
4. Tệp JSON chi tiết đã được lưu trữ tại `artifacts/audit/system_comparison.json` làm cơ sở pháp lý kỹ thuật cho các báo cáo kiểm toán tiếp theo.
