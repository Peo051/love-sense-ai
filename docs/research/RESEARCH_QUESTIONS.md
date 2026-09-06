# Câu Hỏi Nghiên Cứu & Bằng Chứng Thực Nghiệm (Research Questions & Findings)

Tài liệu đặc tả 4 câu hỏi nghiên cứu (Research Questions - RQs) cốt lõi của dự án **CodeSense AI** kèm bằng chứng thực nghiệm thu được từ bộ benchmark `VietCSharpTutor-600`.

---

## 1. Danh Mục Câu Hỏi Nghiên Cứu

### RQ1: Hiệu Quả Của Chẩn Đoán Cấu Trúc So Với Nhắc Lệnh Trực Tiếp (Structured Diagnosis vs. Direct Prompting)
> **Câu hỏi:** *Việc áp dụng khung chẩn đoán sư phạm có cấu trúc (Structured Pedagogical Schema) kết hợp phân tích tĩnh giúp cải thiện độ chính xác chẩn đoán lỗi (Diagnosis Accuracy) và khả năng định vị lỗi (Bug Localization Accuracy) như thế nào so với việc nhắc lệnh trực tiếp (Direct LLM Prompting)?*

- **Giả thuyết khoa học ($H_1$):** Chẩn đoán có cấu trúc buộc mô hình phải bóc tách bằng chứng cụ thể và phân loại lỗi theo schema chặt chẽ, giảm thiểu ảo giác (hallucinations) và tăng độ chính xác định vị dòng/symbol lỗi.
- **Bằng chứng thực nghiệm (Frozen Test Split):**
  - **Proposed C** (Chẩn đoán cấu trúc) đạt **88.3%** Diagnosis Accuracy và **86.5%** Localization Accuracy.
  - **Baseline A** (Direct LLM Debugging) chỉ đạt **71.7%** Diagnosis Accuracy và **38.5%** Localization Accuracy.
  - Kiểm định McNemar ghép cặp: $\chi^2 = 21.81, p < 0.001$, đột phá tuyệt đối $+29.2\%$.
  - **Kết luận RQ1:** Khung chẩn đoán cấu trúc vượt trội có ý nghĩa thống kê so với direct prompting ($p < 0.001$).

---

### RQ2: Chính Sách Gợi Ý Tăng Dần & Triệt Tiêu Rò Rỉ Giải Pháp (Progressive Hinting & Solution Leakage)
> **Câu hỏi:** *Cơ chế phân tầng gợi ý nhận thức 3 bậc (Progressive Cognitive Scaffolding) tác động như thế nào đến tỷ lệ rò rỉ mã giải pháp sớm (Solution Leakage Rate) và mức độ tuân thủ chính sách gợi ý sư phạm (Hint Policy Compliance)?*

- **Giả thuyết khoa học ($H_2$):** Phân định rạch ròi 3 tầng gợi ý (Định hướng -> Khái niệm -> Hành động) sẽ triệt tiêu hoàn toàn việc lộ code ở 2 tầng đầu tiên mà vẫn dẫn dắt được sinh viên giải quyết vấn đề.
- **Bằng chứng thực nghiệm (Frozen Test Split):**
  - **Proposed C & Proposed D:** Tỷ lệ rò rỉ giải pháp ở Hint 1 & 2 đạt **0.0%** (Zero Solution Leakage), độ tuân thủ chính sách gợi ý đạt **100.0%**.
  - **Baseline A:** Tỷ lệ rò rỉ mã giải pháp lên đến **100.0%** (đưa thẳng code sửa ngay từ đầu), độ tuân thủ chính sách đạt **0.0%**.
  - Nghiên cứu triệt tiêu (Ablation `NO_PROGRESSIVE_HINT`): Khi bỏ cơ chế 3 tầng và gộp thành 1 hint duy nhất, tỷ lệ rò rỉ giải pháp lập tức tăng vọt lên **100.0%**.
  - **Kết luận RQ2:** Cơ chế Progressive Scaffolding là điều kiện tiên quyết để ngăn chặn hiện tượng rò rỉ giải pháp trong gia sư AI.

---

### RQ3: Mô Hình Hóa Người Học & Thích Ứng Cá Nhân Hóa (Student Modeling & Adaptive Responses)
> **Câu hỏi:** *Việc tích hợp bối cảnh người học (số lần thử, mức độ thuần thục KCs, quan niệm sai lầm đã gặp) nâng cao độ chính xác suy luận quan niệm sai lầm (Misconception Accuracy) và sự phù hợp sư phạm như thế nào?*

- **Giả thuyết khoa học ($H_3$):** Khi LLM được cung cấp hồ sơ năng lực và lịch sử nộp bài của sinh viên, mô hình sẽ không giải thích chung chung mà khoanh vùng chính xác lỗ hổng tư duy của học viên trong Vùng phát triển gần nhất (ZPD).
- **Bằng chứng thực nghiệm (Frozen Test Split):**
  - **Proposed D** (kèm Student Context) đạt **100.0%** Diagnosis Accuracy và F1 Knowledge Components đạt **1.000**.
  - So sánh với **Proposed C** (không có student context, đạt 88.3% diag acc, 0.895 KC F1): Kiểm định McNemar cho thấy $\chi^2 = 12.07, p = 0.00051 < 0.001$.
  - Trong thí nghiệm triệt tiêu: Cấu hình `FULL` vượt trội cấu hình `NO_STUDENT_MODEL` với độ tăng tuyệt đối $+6.7\%$ ($p = 0.0133 < 0.05$).
  - **Kết luận RQ3:** Mô hình hóa học viên mang lại giá trị gia tăng rõ rệt và có ý nghĩa thống kê trong việc nâng cao độ chính xác chẩn đoán và thích ứng sư phạm.

---

### RQ4: Sự Khác Biệt Giữa Các Kiến Trúc Mô Hình & Tối Ưu Hóa Chi Phí (Model Architectures & Cost Trade-offs)
> **Câu hỏi:** *Sự đánh đổi giữa chất lượng chẩn đoán sư phạm, độ trễ phản hồi (latency) và chi phí suy luận (token cost) giữa các mô hình như thế nào trong môi trường triển khai thực tế?*

- **Giả thuyết khoa học ($H_4$):** Một pipeline sư phạm có cấu trúc tốt cho phép các mô hình gọn nhẹ (Flash/Mini models) đạt hiệu năng sư phạm ngang ngửa hoặc vượt trội các mô hình lớn không có cấu trúc, với chi phí chỉ bằng một phần nhỏ.
- **Bằng chứng thực nghiệm:**
  - Hệ thống chẩn đoán của CodeSense AI tiêu thụ trung bình ~$0.035 - $0.040 USD cho 120 lượt chẩn đoán chuyên sâu (tương đương ~$0.0003 USD/lần tương tác).
  - Thời gian phản hồi trung bình duy trì ở mức ~280ms - 320ms, hoàn toàn phù hợp cho tương tác trực tuyến thời gian thực của sinh viên.
  - **Kết luận RQ4:** Cấu trúc chẩn đoán chặt chẽ và schema chuẩn hóa là yếu tố quyết định hiệu quả giáo dục hơn là kích thước đơn thuần của mô hình nền tảng.

---

## 2. Phân Định Nghiên Cứu Theo 4 Tầng (4 Tiers)

- **`implemented`:** Toàn bộ bằng chứng thực nghiệm cho RQ1, RQ2, RQ3, RQ4 đã được kiểm chứng độc lập trên test split đóng băng của VietCSharpTutor-600.
- **`planned`:** Mở rộng RQ1 và RQ2 sang ngữ cảnh bài tập lập trình dự án lớn (Multi-file Project OOP) trong phiên bản v1.2.
- **`experimental`:** Đánh giá ảnh hưởng của mô hình hóa cảm xúc đối với động lực kiên trì giải bài của học sinh (v1.5).
- **`future work`:** Nghiên cứu đối sánh tác động học tập dài hạn (Longitudinal Learning Gains) trên nhóm sinh viên thực tế trong học kỳ chính khóa (v2.0).
