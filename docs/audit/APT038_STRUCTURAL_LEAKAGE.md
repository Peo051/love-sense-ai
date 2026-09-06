# APT-038: BÁO CÁO KIỂM TOÁN RÒ RỈ CẤU TRÚC VÀ KHUÔN MẪU BÀI TẬP XUYÊN TẬP (CROSS-SPLIT STRUCTURAL & TEMPLATE LEAKAGE AUDIT)

**Kiểm toán viên:** Independent Research Auditor  
**Dự án:** CodeSense AI - Adaptive Programming Tutor  
**Phiên bản đóng băng kiểm toán:** `codesense-research-v1.0`  
**Bộ dữ liệu kiểm toán:** `VietCSharpTutor-600` (600 mẫu, 60 họ bài toán, 10 chủ đề)  
**Ngày thực hiện kiểm toán:** 2026-09-06  
**Mục tiêu:** Xác định xem việc phân chia theo `problem_family_id` có thực sự ngăn chặn hiện tượng rò rỉ thông tin cấu trúc (Structural & Template Leakage) giữa `dev`, `validation` và `test` hay không, và đo lường khả năng giải quyết benchmark bằng các đường tắt đơn giản (Shortcut Baselines).

---

## 1. Tóm Tắt Phát Hiện Kiểm Toán Then Chốt (Executive Summary)

1. **Trùng lặp mã nguồn nguyên văn (Exact Student Code Duplicates):** **0 trường hợp** (Đạt tiêu chuẩn hình thức: không có mã học viên nào bị copy y nguyên qua biên giới các split).
2. **Trùng lặp nguyên văn văn bản sư phạm (Exact Pedagogical Text Duplicates):** **XUẤT HIỆN TRÊN DIỆN RỘNG**:
   - `hint_1`: **10,080 cặp** trùng khớp nguyên văn giữa các split.
   - `hint_2`: **9,072 cặp** trùng khớp nguyên văn giữa các split.
   - `hint_3`: **2,016 cặp** trùng khớp nguyên văn giữa các split.
   - `reference_diagnosis`: **1,008 cặp** trùng khớp nguyên văn giữa các split.
3. **Độ tương đồng cấu trúc mã nguồn C# sau chuẩn hóa (Normalized Structural Similarity):**
   - **81.7% (7,059 / 8,640 cặp cùng chủ đề)** đạt độ tương đồng cấu trúc **$\ge 0.95$ (CRITICAL REVIEW)**.
   - **88.5% (7,650 / 8,640 cặp)** đạt độ tương đồng cấu trúc **$\ge 0.90$ (HIGH REVIEW)**.
   - Cấu trúc mã của bài thi trong tập test thực chất chỉ là việc đổi tên biến (identifier renaming) từ các bài tập trong tập dev.
4. **Hiệu năng của các Shortcut Baselines không cần LLM:**
   - **Topic-only Lookup Baseline:** Đạt **100% Accuracy** chẩn đoán (`bug_status`) và phân loại lỗi (`error_category`) trên cả Validation và Test.
   - **TF-IDF + Naive Bayes Baseline:** Đạt **100% Accuracy** trên cả Validation và Test.
   - **Majority Baseline:** Đạt **80% Accuracy** trạng thái lỗi do 8/10 chủ đề luôn có lỗi (`has_bug`).

---

## 2. Kiểm Toán Trùng Lặp Nguyên Văn (Exact Duplicate Audit)

Kiểm toán viên đã đối soát chéo toàn bộ các cặp mẫu giữa 3 phân vùng: `dev \leftrightarrow validation`, `dev \leftrightarrow test`, `validation \leftrightarrow test`:

| Tên trường đối chiếu | Số cặp trùng khớp nguyên văn (Exact Matches) | Nhận xét kiểm toán |
| :--- | :---: | :--- |
| `student_code` | **0** | Đạt yêu cầu: Không có code trùng lặp ký tự tuyệt đối |
| `problem_statement_vi` | **0** | Đạt yêu cầu: Tên thực thể đã được thay đổi |
| `compiler_error` | **3,024** | Thông báo lỗi trình biên dịch trùng lặp mã lỗi CS |
| `reference_solution` | **0** | Mã giải pháp đã thay đổi tên định danh |
| `reference_diagnosis` | **1,008** | Văn bản chẩn đoán được tái sử dụng nguyên văn theo chủ đề |
| `hint_1` | **10,080** | **TRÙNG LẶP NGUYÊN VĂN 100%** giữa các bài cùng chủ đề |
| `hint_2` | **9,072** | **TRÙNG LẶP NGUYÊN VĂN** theo chủ đề |
| `hint_3` | **2,016** | **TRÙNG LẶP NGUYÊN VĂN** theo chủ đề |

---

## 3. Độ Tương Đồng Cấu Trúc Mã Nguồn (Normalized Code Similarity)

Quy trình chuẩn hóa mã C# đã loại bỏ toàn bộ comment, chuẩn hóa khoảng trắng, biến đổi chuỗi/số thành tokens chuẩn (`STR_LIT`, `NUM_LIT`) và ánh xạ toàn bộ tên định danh riêng thành `ID_0, ID_1, ID_2,...`. Sau đó tính toán kết hợp Token Jaccard Similarity và Sequence Similarity:

$$\text{StructuralSimilarity} = \frac{\text{TokenJaccard} + \text{SequenceSimilarity}}{2}$$

### Phân phối độ tương đồng xuyên split (cùng topic):
- Tổng số cặp so sánh: **8,640 cặp**
- Cặp có độ tương đồng $\ge 0.95$ (**CRITICAL REVIEW**): **7,059 cặp (81.7%)**
- Cặp có độ tương đồng $\ge 0.90$ (**HIGH REVIEW**): **591 cặp (6.8%)**
- Cặp có độ tương đồng $\ge 0.80$ (**REPORT**): **0 cặp**
- Tỷ lệ các cặp có nguy cơ rò rỉ cấu trúc nghiêm trọng ($\ge 0.90$): **88.5%**

### Bảng Top 10 Cặp Đáng Ngờ Nhất (Top 10 Suspicious Pairs):

| STT | Mẫu Val/Test ID | Split | Họ Val/Test | Mẫu Dev ID | Họ Dev | Chủ đề | Token Jaccard | Sequence Sim | Structural Sim |
| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| 1 | `vct-361` | validation | `fam-parking-lot` | `vct-021` | `fam-product-inventory` | `class_object` | 1.0 | 1.0 | **1.0** |
| 2 | `vct-361` | validation | `fam-parking-lot` | `vct-041` | `fam-library-book` | `class_object` | 1.0 | 1.0 | **1.0** |
| 3 | `vct-361` | validation | `fam-parking-lot` | `vct-101` | `fam-course-enrollment` | `class_object` | 1.0 | 1.0 | **1.0** |
| 4 | `vct-361` | validation | `fam-parking-lot` | `vct-111` | `fam-shopping-cart` | `class_object` | 1.0 | 1.0 | **1.0** |
| 5 | `vct-361` | validation | `fam-parking-lot` | `vct-131` | `fam-smartphone-battery` | `class_object` | 1.0 | 1.0 | **1.0** |
| 6 | `vct-361` | validation | `fam-parking-lot` | `vct-141` | `fam-pet-care` | `class_object` | 1.0 | 1.0 | **1.0** |
| 7 | `vct-361` | validation | `fam-parking-lot` | `vct-171` | `fam-movie-ticket` | `class_object` | 1.0 | 1.0 | **1.0** |
| 8 | `vct-361` | validation | `fam-parking-lot` | `vct-191` | `fam-timer-stopwatch` | `class_object` | 1.0 | 1.0 | **1.0** |
| 9 | `vct-361` | validation | `fam-parking-lot` | `vct-201` | `fam-game-character` | `class_object` | 1.0 | 1.0 | **1.0** |
| 10 | `vct-361` | validation | `fam-parking-lot` | `vct-221` | `fam-laptop-spec` | `class_object` | 1.0 | 1.0 | **1.0** |

---

## 4. Phân Tích Đường Tắt Phân Loại (Shortcut Baseline Analysis)

Để xác định xem benchmark có đòi hỏi năng lực suy luận sư phạm chuyên sâu hay chỉ cần các quy tắc đường tắt (shortcuts), kiểm toán viên đã xây dựng 4 mô hình cơ sở phi LLM (non-LLM baselines) chỉ huấn luyện trên tập `dev` (360 mẫu):

1. **Majority Baseline:** Dự đoán nhãn phổ biến nhất của tập `dev`.
2. **Topic-only Lookup Baseline:** Tra cứu nhãn phổ biến nhất tương ứng với `topic` được gắn kèm trong bài toán.
3. **Regex / Compiler Heuristic:** Nhận diện chuỗi lỗi trình biên dịch (`compiler_error`) kết hợp từ khóa.
4. **TF-IDF + Naive Bayes Classifier:** Mô hình tuyến tính đơn giản phân loại dựa trên túi từ (bag-of-words) của đề bài và mã nguồn.

### Kết quả đo lường thực tế trên Validation và Frozen Test:

| Mô hình kiểm toán (Audited Baseline) | Độ chính xác trạng thái lỗi (`bug_status` Acc) | Độ chính xác loại lỗi (`error_category` Acc) | Đánh giá mức độ rủi ro |
| :--- | :---: | :---: | :--- |
| **Majority Baseline** | 80.00% | 40.00% | Do 80% số topic là buggy |
| **Regex / Compiler Error Baseline** | 80.00% | 80.00% | Nhận diện hoàn hảo compile_error |
| **Topic-only Lookup Baseline** | **100.00%** | **100.00%** | **ĐƯỜNG TẮT TUYỆT ĐỐI (100% SHORTCUT)** |
| **TF-IDF + Naive Bayes Baseline** | **100.00%** | **100.00%** | **ĐƯỜNG TẮT TUYỆT ĐỐI (100% SHORTCUT)** |

### Phân tích nguyên nhân gốc rễ (Root Cause):
Trong `VietCSharpTutor-600`, mỗi `topic` chỉ có duy nhất **MỘT** loại lỗi cụ thể xuyên suốt cả 60 bài toán (ví dụ: topic `class_object` luôn luôn là lỗi `CS0165 / uninstantiated_object_reference`). Do đó, chỉ cần biết `topic`, hệ thống có thể lập tức đoán trúng 100% nhãn chẩn đoán mà không cần phân tích cú pháp hay ngữ nghĩa của mã nguồn học viên!

---

## 5. Phân Loại Rủi Rò Rỉ Cuối Cùng (Audit Verdict)

Áp dụng các ngưỡng kiểm toán đã định nghĩa:
- *Exact Cross-Split Duplicate:* PASS trên `student_code`, FAIL trên gợi ý sư phạm.
- *Normalized Structural Similarity $\ge 0.95$:* **7,059 cặp vi phạm (81.7%)** $\rightarrow$ **CRITICAL REVIEW**.
- *Shortcut Baseline Performance:* **100% Giải quyết được bằng Topic Lookup** $\rightarrow$ **CRITICAL SHORTCUT**.

# PHÂN LOẠI RỦI RO: HIGH LEAKAGE RISK

### Khuyến nghị cho phiên bản Benchmark V2:
1. **Đa dạng hóa lỗi trong cùng một Topic:** Mỗi topic phải chứa ít nhất 5-10 biến thể lỗi khác nhau để triệt tiêu hoàn toàn đường tắt Topic Lookup.
2. **Cắt đứt sự phụ thuộc vào khuôn mẫu (Template Decoupling):** Biên soạn bài tập từ các ngữ cảnh lập trình đa dạng, không sử dụng một hàm sinh code duy nhất với các placeholder cố định.
3. **Loại bỏ nhãn metadata `topic` khỏi luồng suy luận:** Mô hình phải tự phát hiện chủ đề và lỗi hoàn toàn dựa trên mã nguồn và đề bài.
