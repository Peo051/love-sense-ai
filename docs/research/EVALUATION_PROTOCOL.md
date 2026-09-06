# Giao Thức Đánh Giá Thực Nghiệm Đóng Băng (Frozen Evaluation Protocol)

Tài liệu đặc tả quy trình và phương pháp luận đánh giá khoa học đông băng của dự án **CodeSense AI - Adaptive Programming Tutor**.

---

## 1. Nguyên Tắc Đóng Băng Thực Nghiệm (Freezing Principles)

Để đảm bảo tính khách quan học thuật và khả năng tái lập 100% (Full Reproducibility), quy trình đánh giá tuân thủ 6 nguyên tắc bất biến trước khi tiếp cận tập dữ liệu kiểm thử (Test Split):

1. **Đóng băng Git Commit:** Mã nguồn hệ thống và pipeline phân tích được ghi nhận cố định theo mã băm commit cụ thể.
2. **Đóng băng Phiên bản Dataset:** Sử dụng bộ dữ liệu `VietCSharpTutor-600` phiên bản v1.0.0.
3. **Đóng băng Mã băm Tập Test:** Mã băm SHA-256 của tập Test Split (120 mẫu) là:
   `719fd445444ff9f42e6989729236c8a64773cdd96344fd61307c532457516de4`.
4. **Đóng băng Phiên bản Nhắc lệnh (Prompts):** Toàn bộ prompt của các hệ thống và ablation được gán nhãn `v1.0` và không được phép chỉnh sửa sau khi chạy thực nghiệm.
5. **Đóng băng Danh sách Mô hình:** Danh sách mô hình thử nghiệm cố định trong cấu hình runner.
6. **Thực nghiệm Validation trước, Test Split chạy đúng 1 lần:** Mọi điều chỉnh và tinh chỉnh siêu tham số chỉ được thực hiện trên `dev` hoặc `validation` split. Khi chạy trên `test` split, hệ thống chỉ chạy một lần duy nhất và lưu toàn bộ raw predictions trước khi tiến hành phân tích thống kê.

---

## 2. Các Hệ Thống Đối So Sánh (Comparative Systems)

| Hệ Thống | Mã Hiệu | Mô Tả Kỹ Thuật | Vai Trò Thực Nghiệm |
| :--- | :--- | :--- | :--- |
| **Baseline A** | Direct LLM Debugging | Nhắc lệnh trực tiếp tìm lỗi và viết lại toàn bộ mã đã sửa. | Đại diện cho các chatbot GenAI thông thường (ChatGPT/Copilot). |
| **Baseline B** | Generic Tutor Prompt | Đóng vai gia sư lập trình chung chung, giải thích lỗi văn xuôi không cấu trúc. | Đo lường hiệu quả của việc đóng vai gia sư khi thiếu schema chẩn đoán. |
| **Proposed C** | Structured Scaffolding | Khung chẩn đoán cấu trúc Roslyn + JSON schema, 3 tầng gợi ý tăng dần. | Đánh giá tác động độc lập của chẩn đoán cấu trúc và progressive hints. |
| **Proposed D** | Full Adaptive Tutor | Tích hợp đầy đủ: Chẩn đoán cấu trúc + Gợi ý tăng dần + Ngữ cảnh mô hình học viên (Mastery KCs). | Hệ thống hoàn chỉnh của CodeSense AI. |

---

## 3. Nghiên Cứu Triệt Tiêu Thành Phần (Ablation Study)

Để kiểm chứng vai trò của từng mô-đun độc lập, 5 cấu hình triệt tiêu được thiết kế theo nguyên tắc "chỉ thay đổi một biến số duy nhất":
1. `FULL`: Đầy đủ cả 3 thành phần (Chẩn đoán cấu trúc + Gợi ý 3 bậc + Mô hình người học).
2. `NO_STUDENT_MODEL`: Loại bỏ ngữ cảnh người học, chỉ giữ chẩn đoán cấu trúc và gợi ý 3 bậc.
3. `NO_PROGRESSIVE_HINT`: Loại bỏ 3 bậc gợi ý, đưa trực tiếp mã giải pháp ở gợi ý đầu tiên.
4. `NO_STRUCTURED_DIAGNOSIS`: Loại bỏ schema JSON chẩn đoán, sử dụng nhắc lệnh văn bản tự do.
5. `DIRECT_BASELINE`: Loại bỏ toàn bộ các thành phần sư phạm (Baseline thuần túy).

---

## 4. Bộ Chỉ Số Đánh Giá Sư Phạm (11 Core Tutoring Metrics)

1. **Diagnosis Accuracy:** Tỷ lệ chẩn đoán đúng trạng thái lỗi (`has_bug`, `no_bug`, `insufficient_context`) và đúng loại lỗi (`bug_type`).
2. **Bug Localization Accuracy:** Tỷ lệ xác định chính xác dòng hoặc ký hiệu (`symbol`) gây lỗi trong các ca có lỗi.
3. **Error Category Accuracy:** Tỷ lệ phân loại chính xác nhóm lỗi kỹ thuật (`compile_error`, `logic_error`, `runtime_error`, `conceptual_misuse`).
4. **Knowledge Component F1:** Điểm F1 trung bình (Macro F1) giữa tập KCs dự đoán và KCs chuẩn mực:
   $$\text{F1} = \frac{2 \cdot P \cdot R}{P + R}$$
5. **Misconception Accuracy:** Tỷ lệ suy luận chính xác quan niệm sai lầm cốt lõi của sinh viên.
6. **No-Bug False Positive Rate:** Tỷ lệ báo lỗi oan trên tập đối chứng mã nguồn hoàn toàn đúng (`no_bug`) (Mục tiêu: $0.0\%$).
7. **Insufficient-Context Accuracy:** Tỷ lệ nhận diện chính xác đoạn mã bị cắt đoạn hoặc khuyết định nghĩa lớp (`insufficient_context`).
8. **Evidence Faithfulness:** Tỷ lệ bằng chứng `evidence` được trích xuất nguyên văn là chuỗi con (substring) từ `student_code`.
9. **Solution Leakage Rate:** Tỷ lệ rò rỉ mã giải pháp hoàn chỉnh trong Hint 1 hoặc Hint 2 (Mục tiêu: $0.0\%$).
10. **JSON Valid Rate:** Tỷ lệ phản hồi tuân thủ hoàn hảo định dạng dữ liệu có cấu trúc JSON.
11. **Hint Policy Compliance:** Tỷ lệ gợi ý tuân thủ đúng chính sách 3 bậc (Hint 1: Định hướng, Hint 2: Khái niệm, Hint 3: Hành động).

Kèm theo các chỉ số tài nguyên vận hành:
- **Độ trễ (Latency):** Trung bình, P50, P95 (tính bằng mili-giây ms).
- **Tokens & Chi phí (Cost):** Tổng số prompt tokens, completion tokens và ước tính chi phí USD trên 1M tokens.

---

## 5. Phương Pháp Luận Kiểm Định Thống Kê

1. **Kiểm định McNemar Ghép Cặp (Paired McNemar's Test):**
   Áp dụng cho các biến nhị phân đúng/sai trên cùng một tập mẫu kiểm thử giữa hai hệ thống. Bảng tiếp liên $2 \times 2$:
   - $b$: Số ca Hệ thống 2 đúng, Hệ thống 1 sai
   - $c$: Số ca Hệ thống 1 đúng, Hệ thống 2 sai
   Công thức hiệu chỉnh tính liên tục Edwards:
   $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}, \quad df = 1$$
   Tính $p$-value từ phân phối $\chi^2$. Báo cáo kèm đột phá tuyệt đối $\Delta = \text{Acc}_2 - \text{Acc}_1$ và tỷ số chênh lệch Odds Ratio ($b/c$).
2. **Khoảng Tin Cậy Bootstrap 95% (Bootstrap 95% Confidence Intervals):**
   Lấy mẫu lại có hoàn lại 1,000 lần ($B = 1000$) để tính phân vị $2.5\%$ và $97.5\%$ cho các tỷ lệ tổng hợp nhằm đảm bảo độ tin cậy thống kê cao.

---

## 6. Hướng Dẫn Tái Lập Toàn Bộ Đánh Giá (Reproduction Commands)

```bash
# 1. Thực thi frozen experimental protocol (Validation + Test Split):
python scripts/execute_frozen_protocol.py

# 2. Phân tích thống kê chuyên sâu và tạo báo cáo khoa học:
python scripts/analyze_results.py
```
Toàn bộ kết quả đầu ra sẽ tự động được lưu tại:
- `runs/`: Lưu trữ file predictions thô của từng run.
- `manifests/`: Lưu trữ các file manifest bất biến.
- `results/`: Lưu trữ bảng so sánh JSON, CSV và báo cáo `ANALYSIS_SUMMARY.md`.

---

## 7. Phân Định Giao Thức Đánh Giá (4 Tiers)

- **`implemented`:** Toàn bộ runner, 11 metrics, kiểm định McNemar, bootstrap 95% CI và runner protocol đã được vận hành thành công.
- **`planned`:** Đánh giá mở rộng trên tập dữ liệu đa ngôn ngữ OOP (v1.2).
- **`experimental`:** Đánh giá tính chịu lỗi của hệ thống khi mạng gián đoạn thông qua Chaos Engineering.
- **`future work`:** Kiểm định mù đôi (Double-blind Human Tutor Evaluation) đối chiếu giữa gợi ý của CodeSense AI và trợ giảng con người (v2.0).
