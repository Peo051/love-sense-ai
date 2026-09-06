# Đặt Vấn Đề Nghiên Cứu (Research Problem Statement)

> [!CAUTION]
> **CẢNH BÁO TÍNH TOÀN VẸN NGHIÊN CỨU (RESEARCH INTEGRITY WARNING):**  
> Các số liệu thực nghiệm, chỉ số hiệu năng và kết luận đánh giá trong tài liệu này thuộc bản phát hành lịch sử `codesense-research-v1.0` và **ĐÃ BỊ HỦY BỎ HIỆU LỰC HOÀN TOÀN (INVALIDATED)** theo kết luận kiểm toán độc lập [APT-047](../docs/audit/APT047_EVALUATION_INTEGRITY_VERDICT.md) (commit `4b07ec2`).  
> - Bảng phân loại hiệu lực chi tiết xem tại: [V1_RESULT_STATUS.md](V1_RESULT_STATUS.md).  
> - Bộ dữ liệu `VietCSharpTutor-600` chỉ được coi là: **INTERNAL REGRESSION BENCHMARK ONLY** (Không phải benchmark được ngoại kiểm).  
> - Các hiện vật thực nghiệm lịch sử được lưu trữ nguyên trạng nhằm phục vụ mục đích kiểm toán đối soát minh bạch.

---


Tài liệu xác lập bối cảnh khoa học và động lực nghiên cứu của dự án **CodeSense AI - Adaptive Programming Tutor**.

---

## 1. Thách Thức Khi Người Mới Bắt Đầu Học Lập Trình Hướng Đối Tượng (OOP)

Lập trình hướng đối tượng (Object-Oriented Programming - OOP) là một trong những ngưỡng nhận thức (Threshold Concepts) khó khăn nhất đối với sinh viên năm nhất ngành Công nghệ Thông tin. Không giống như lập trình thủ tục tuần tự, OOP đòi hỏi người học phải hình thành mô hình trừu tượng hóa đa chiều:
- **Biến tham chiếu và Khởi tạo vùng nhớ Heap:** Sinh viên thường nhầm lẫn giữa việc khai báo biến lớp và việc cấp phát thực thể (`new`), dẫn đến các lỗi `NullReferenceException` hoặc `CS0165 (Use of unassigned local variable)`.
- **Bao gói dữ liệu và Quy tắc bất biến (Encapsulation & Invariants):** Xu hướng lạm dụng trường `public` hoặc viết getter/setter gọi đệ quy chính nó gây `StackOverflowException`.
- **Phạm vi biến và Từ khóa `this`:** Hiện tượng tham số che khuất trường dữ liệu (`variable shadowing`), khiến đối tượng giữ giá trị mặc định mà không báo lỗi lúc biên dịch.
- **Tính đa hình và Liên kết động (Polymorphism & Dynamic Dispatch):** Nhầm lẫn giữa che giấu phương thức (method hiding) và ghi đè phương thức (method overriding), quên cặp từ khóa `virtual` / `override`.

---

## 2. Nghịch Lý Của Các Mô Hình AI Tạo Sinh Thông Thường (The GenAI Dilemma)

Sự bùng nổ của các mô hình ngôn ngữ lớn (như ChatGPT, GitHub Copilot, Claude) mang lại tiềm năng hỗ trợ học tập to lớn, nhưng đồng thời tạo ra một nghịch lý sư phạm nghiêm trọng:

```
[Sinh viên gặp lỗi] 
       │
       ▼
[Hỏi ChatGPT/Copilot] ───> [AI trả về ngay đoạn code đã sửa 100%]
                                        │
                                        ▼ (Solution Leakage)
                      [Sinh viên Copy - Paste mà không hiểu bản chất]
                                        │
                                        ▼
                      [Không hình thành tư duy OOP - Phụ thuộc AI]
```

1. **Rò rỉ giải pháp sớm (Premature Solution Dumping):** LLM mặc định luôn cố gắng làm hài lòng người dùng bằng cách viết lại toàn bộ đoạn mã hoàn chỉnh. Điều này triệt tiêu hoàn toàn quá trình "vật lộn nhận thức tích cực" (Productive Failure / Cognitive Struggle) cần thiết để hình thành kỹ năng giải quyết vấn đề.
2. **Thiếu tính định vị và neo bằng chứng (Hallucinated Localization):** LLM thường đưa ra lời giải thích lan man, không neo đúng dòng lỗi thực tế trong bài làm của học sinh.
3. **Ảo giác trên mã đúng (No-Bug False Positives):** Khi học viên nộp đoạn code đã chuẩn, các chatbot AI thường tự "bịa" ra lỗi phong cách hoặc yêu cầu viết lại theo cách khác, gây hoang mang cho người mới học.
4. **Không có mô hình người học (No Learner Modeling):** Mô hình trả lời chung chung cho mọi sinh viên mà không biết bạn đó đã thuần thục kiến thức nào, đang gặp khó khăn ở KC nào hay đã thử sửa bao nhiêu lần.

---

## 3. Giải Pháp CodeSense AI Tutor

CodeSense AI được phát triển nhằm giải quyết triệt để nghịch lý trên thông qua 4 cơ chế khoa học:

1. **Pipeline Chẩn đoán Cấu trúc:** Kết hợp luật phân tích Roslyn và schema sư phạm chặt chẽ để xác định chính xác loại lỗi, vị trí và bằng chứng nguyên văn.
2. **Khung Gợi ý Tăng dần 3 Bậc (Progressive Scaffolding):**
   - Không bao giờ đưa code giải pháp ở Hint 1 & Hint 2.
   - Gợi mở tư duy Socratic để người học tự nhận ra lỗi của chính mình.
3. **Mô hình Hóa Năng Lực Học Viên (Student Mastery Modeling):**
   - Theo dõi điểm thuần thục (Mastery Score) của 10+ Thành phần Kiến thức (KCs).
   - Điều chỉnh gợi ý nằm trong Vùng phát triển gần nhất (ZPD - Vygotsky).
4. **Bảo Mật & Quyền Riêng Tư (Privacy-by-Design):**
   - Tách biệt lưu trữ kết quả và mã nguồn đầu vào, tôn trọng quyền riêng tư của sinh viên.

---

## 4. Phân Định Nghiên Cứu Theo 4 Tầng

- **`implemented`:** Toàn bộ khung chẩn đoán cấu trúc, cơ chế phân tầng gợi ý 3 bậc, mô hình hóa KCs, và bộ dữ liệu đánh giá 600 ca đã hoàn thành.
- **`planned`:** Mở rộng nghiên cứu sang ngôn ngữ Java OOP và Python OOP (v1.2).
- **`experimental`:** Đánh giá ảnh hưởng của tốc độ gõ phím đến tải nhận thức (v1.5).
- **`future work`:** Mô hình hóa mạng Bayes đa cấp (Dynamic Bayesian Knowledge Tracing) tích hợp trực tiếp vào hệ thống quản lý học tập (LMS) của các trường đại học (v2.0).
