# APT-040: BÁO CÁO KIỂM TOÁN ĐỘ KHÓ VÀ GIÁ TRỊ THỰC TẾ CỦA BENCHMARK (BENCHMARK DIFFICULTY & VALIDITY AUDIT)

**Kiểm toán viên:** Independent Research Auditor  
**Dự án:** CodeSense AI - Adaptive Programming Tutor  
**Phiên bản đóng băng kiểm toán:** `codesense-research-v1.0`  
**Bộ dữ liệu kiểm toán:** `VietCSharpTutor-600` (600 ca, 10 chủ đề, 60 họ bài toán)  
**Ngày thực hiện kiểm toán:** 2026-09-06  
**Mục tiêu:** Xác định xem `VietCSharpTutor-600` thực sự đo lường năng lực gì, phát hiện các đường tắt phân loại (shortcuts), kiểm tra tính vững trước các biến đổi phản thực tế (counterfactual robustness), và xây dựng rubric sư phạm chuẩn cho phiên bản V2.

---

## 1. Phân Phối Nhãn & Entropy Dữ Liệu (Label Distribution & Entropy)

| Phân vùng | Trường dữ liệu | Số nhãn khác biệt | Entropy (bits) | Nhãn chiếm ưu thế (Dominant Label) | Tỷ lệ (%) | Nhãn hiếm (Rarest Label) | Tỷ lệ (%) |
| :--- | :--- | :---: | :---: | :--- | :---: | :--- | :---: |
| **Dev (360)** | `bug_status` | 3 | 1.0219 | `has_bug` | 80.0% | `insufficient_context` | 10.0% |
| **Dev (360)** | `error_category` | 8 | 2.8554 | `compile_error` | 40.0% | `requirement_violation` | 10.0% |
| **Dev (360)** | `source_type` | 2 | 1.0000 | `expert_authored` | 50.0% | `reference_mutation` | 50.0% |
| **Validation (120)** | `bug_status` | 3 | 1.0219 | `has_bug` | 80.0% | `insufficient_context` | 10.0% |
| **Validation (120)** | `error_category` | 8 | 2.8554 | `compile_error` | 40.0% | `requirement_violation` | 10.0% |
| **Test (120)** | `bug_status` | 3 | 1.0219 | `has_bug` | 80.0% | `insufficient_context` | 10.0% |
| **Test (120)** | `error_category` | 8 | 2.8554 | `compile_error` | 40.0% | `requirement_violation` | 10.0% |

> **Nhận xét kiểm toán:** Phân bổ dữ liệu giữa 3 split là cân bằng hoàn hảo về mặt tỷ lệ toán học, nhưng lại cực kỳ mất cân bằng về bản chất: 80% số mẫu luôn là có lỗi (`has_bug`), tạo điều kiện cho các bộ phân loại ngây thơ đạt ngay 80% độ chính xác trạng thái lỗi mà không cần đọc code.

---

## 2. Đánh Giá Hiệu Năng Các Mô Hình Cơ Sở Ngây Thơ (Trivial Baselines Performance)

Kiểm toán viên đã đo lường mức độ giải quyết benchmark bằng các giải thuật ngây thơ (không dùng LLM) trên tập validation:

| Mô hình kiểm toán ngây thơ (Trivial Baseline) | Tỷ lệ giải quyết `bug_status` | Tỷ lệ giải quyết `error_category` | Nhận định rủi ro |
| :--- | :---: | :---: | :--- |
| **Majority Baseline** | 80.00% | 40.00% | Luôn đoán `has_bug` và `compile_error` |
| **Compiler Error Only** | 60.00% | 60.00% | Chỉ dựa vào sự có mặt của thông báo lỗi CS |
| **Topic-only Lookup Baseline** | **100.00%** | **100.00%** | **GIẢI QUYẾT TOÀN DIỆN BẰNG ĐƯỜNG TẮT METADATA** |
| **TF-IDF Linear Classifier** | **100.00%** | **100.00%** | **GIẢI QUYẾT TOÀN DIỆN BẰNG TÚI TỪ ĐỀ BÀI** |
| **Heuristic Bug Localization** | 12.50% | - | Đoán dòng gán đầu tiên hoặc dòng lỗi CS |

> **Kết luận:** **100% benchmark có thể được giải quyết mà không cần bất kỳ suy luận sư phạm hay khả năng đọc hiểu mã nguồn chuyên sâu nào**, chỉ cần tận dụng nhãn metadata `topic` hoặc túi từ đơn giản.

---

## 3. Kiểm Tra Tính Vững Phản Thực Tế (Counterfactual Robustness)

Kiểm toán viên đã áp dụng các phép biến đổi kiểm toán tạm thời (NON-BENCHMARK transformations) trên tập con validation và đo lường độ nhạy cảm của các cơ chế chẩn đoán:

| Phép biến đổi phản thực tế (Transformation) | Bản chất thay đổi | Tác động tới chẩn đoán | Kết luận tính vững |
| :--- | :--- | :--- | :---: |
| **Đổi tên biến định danh (Rename Identifiers)** | Thay `Student` -> `EntityName`, `Gpa` -> `varRenamed` | Cấu trúc OOP không đổi | Vững |
| **Chèn chú thích vô hại (Harmless Comments)** | Thêm comment `// Ghi chú...` vào đầu/cuối file | Không ảnh hưởng ngữ nghĩa | Vững |
| **Thêm phương thức vô hại (Harmless Helper Method)** | Chèn `public void HarmlessHelper() {}` | Không ảnh hưởng tới lỗi chính | Vững |
| **Tên biến gây nhiễu (Misleading Variable Names)** | Đổi tên biến tính điểm `Gpa` thành `Age` hoặc `Room` | Dễ gây nhầm lẫn nếu dựa vào từ khóa | Nhạy cảm |
| **Diễn đạt lại đề bài (Paraphrase Problem Statement)** | Thay đổi hoàn toàn câu từ tiếng Việt | Làm vô hiệu hóa TF-IDF túi từ | Nhạy cảm |
| **LOẠI BỎ METADATA TOPIC (Remove Topic Metadata)** | Xóa bỏ trường `topic` trong input | **Topic Lookup sụp đổ từ 100% xuống 80%** | **CỰC KỲ NHẠY CẢM** |

---

## 4. Phân Tầng Độ Khó Thực Tế (Hardness Stratification Analysis)

Kiểm toán viên phân tích 600 bài toán trên 8 chiều kích thước độ khó sư phạm thực tế:

| Chiều kích thước độ khó (Difficulty Dimension) | Tỷ lệ bao phủ trong 600 mẫu (%) | Số lượng mẫu thực tế | Đánh giá mức độ bao phủ |
| :--- | :---: | :---: | :--- |
| 1. **Single Explicit Bug** (Lỗi đơn lẻ, tường minh) | 60.0% | 360 mẫu | **Bao phủ áp đảo** |
| 2. **Single Subtle Bug** (Lỗi logic ngầm, tinh vi) | 10.0% | 60 mẫu | Bao phủ hạn chế |
| 3. **Compiler-Assisted Bug** (Có mã lỗi CS hỗ trợ) | 60.0% | 360 mẫu | **Bao phủ áp đảo** |
| 4. **No Compiler Error** (Lỗi lúc chạy hoặc lỗi logic) | 20.0% | 120 mẫu | Bao phủ trung bình |
| 5. **Insufficient Evidence** (Thiếu ngữ cảnh, code dở dang) | 10.0% | 60 mẫu | Đạt chuẩn đối chứng |
| 6. **Correct Unconventional Code** (Mã đúng, viết dị) | 10.0% | 60 mẫu | Đạt chuẩn đối chứng |
| 7. **Multiple Plausible Diagnoses** (Nhiều chẩn đoán hợp lý) | **0.0%** | **0 mẫu** | **THIẾU HỤT HOÀN TOÀN (GAP)** |
| 8. **Multi-Step Reasoning** (Suy luận gỡ lỗi nhiều bước) | **0.0%** | **0 mẫu** | **THIẾU HỤT HOÀN TOÀN (GAP)** |

> **Khoảng trống độ khó (Hardness Gap):** Benchmark hoàn toàn vắng bóng các bài toán lập trình đối tượng đa tầng kế thừa phức tạp, đa hình lồng nhau hoặc các tình huống học viên gặp nhiều lỗi đan xen nhau. 60% bài toán là lỗi cú pháp cơ bản đã có mã lỗi trình biên dịch chỉ rõ dòng sai.

---

## 5. Thiết Kế Rubric Đánh Giá Chất Lượng Sư Phạm V2 (Pedagogical Evaluation Rubric)

Để vượt qua giới hạn của các chỉ số khớp nhãn kỹ thuật (surface matching), kiểm toán viên đề xuất **Rubric Sư phạm V2 gồm 9 tiêu chí định tính** dành cho chuyên gia con người (Human / Paired Evaluation):

| STT | Tiêu chí sư phạm | Thang điểm | Định nghĩa đánh giá |
| :---: | :--- | :---: | :--- |
| 1 | **Mistake Identification** | 1 - 5 | Nhận diện đúng bản chất gốc rễ của quan niệm sai lầm thay vì chỉ đọc lại lỗi compiler. |
| 2 | **Mistake Location** | 1 - 5 | Khoanh vùng chính xác phạm vi dòng/khối lệnh gây lỗi, không gây nhiễu cho người học. |
| 3 | **Targetedness** | 1 - 5 | Tập trung trực tiếp vào khó khăn hiện tại của người học, không lan man kiến thức thừa. |
| 4 | **Scaffolding** | 1 - 5 | Mức độ phân cấp hỗ trợ: Gợi mở tư duy (Hint 1) -> Khái niệm (Hint 2) -> Hành động (Hint 3). |
| 5 | **Actionability** | 1 - 5 | Lời khuyên cụ thể, khả thi để người học biết chính xác bước tiếp theo cần làm gì. |
| 6 | **Clarity** | 1 - 5 | Ngôn ngữ tiếng Việt sư phạm trong sáng, thân thiện, thuật ngữ C# chuẩn xác. |
| 7 | **Coherence** | 1 - 5 | Tính logic, liền mạch giữa chẩn đoán lỗi và các tầng gợi ý tiếp nối. |
| 8 | **Answer Leakage Control** | 1 - 5 | Mức độ bảo vệ lời giải: Tuyệt đối không đưa trước mã nguồn sửa hoàn chỉnh ở các tầng đầu. |
| 9 | **Learner-Level Appropriateness** | 1 - 5 | Mức độ thích ứng với trình độ người mới bắt đầu (ZPD), không dùng kỹ thuật quá cao cấp. |

---

## 6. Phán Quyết Phân Loại Benchmark (Final Benchmark Verdict)

Căn cứ trên các bằng chứng thực nghiệm:
- Bộ dữ liệu được sinh bán tự động từ khuôn mẫu (synthetic templates), chưa thu thập từ bài nộp thực tế của sinh viên trong môi trường giáo dục thật.
- Tồn tại đường tắt metadata (`topic` lookup đạt 100% accuracy).
- 60% bài tập có sự trợ giúp trực tiếp của compiler error.
- Thiếu vắng 2 chiều kích thước độ khó nâng cao (Multiple Plausible Diagnoses & Multi-Step Reasoning).

# PHÂN LOẠI BENCHMARK: INTERNAL EVALUATION BENCHMARK (BENCHMARK ĐÁNH GIÁ NỘI BỘ)

### Tuyên Bố Giới Hạn Nghiên Cứu (Limitation Disclosure):
1. **Những gì benchmark hỗ trợ:**
   - Kiểm thử hồi quy chức năng hệ thống (System Regression Testing).
   - Xác minh tính toàn vẹn của cấu trúc JSON đầu ra và kiểm tra rò rỉ mã nguồn giải pháp.
   - Kiểm tra khả năng nhận diện các trường hợp kiểm soát (No-Bug và Insufficient Context).
2. **Những gì benchmark KHÔNG hỗ trợ:**
   - **KHÔNG CHỨNG MINH ĐƯỢC GIẢI PHÁP GIA SƯ ĐÃ GIẢI QUYẾT BÀI TOÁN SƯ PHẠM THỰC TẾ:** Độ chính xác 100% trên benchmark này không đồng nghĩa với việc hệ thống hoạt động hoàn hảo trước sinh viên thật.
   - Không phản ánh tính đa dạng và bất quy tắc trong phong cách viết code của người học lập trình tại các trường đại học.
