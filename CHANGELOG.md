# Lịch Sử Thay Đổi (Changelog)

Toàn bộ các thay đổi và cột mốc phát hành của dự án **CodeSense AI - Adaptive Programming Tutor**.

Định dạng tuân thủ [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) và quy ước [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [codesense-research-v1.0] - 2026-09-06

### Đã Thêm (Added)
- **Bộ Dữ Liệu VietCSharpTutor-600 (APT-026, APT-027):**
  - Xây dựng 600 ca benchmark chuẩn mực C# OOP cho người mới học trên 60 họ bài toán độc lập (`problem_family_id`) và 10 chủ đề OOP.
  - Phân chia split không rò rỉ ranh giới (Zero Family Leakage): 360 dev / 120 validation / 120 test.
  - Định nghĩa JSON Schema Draft-07 với đúng 25 trường bắt buộc (`schema.json`).
  - Xây dựng CLI Validator tự động (`scripts/validate_vietcsharptutor.py`) kiểm định cú pháp, tính xác thực bằng chứng (evidence grounding) và xuất báo cáo `benchmark_report.md`.
- **Hệ Thống Đánh Giá & Đo Lường Sư Phạm (APT-028, APT-029):**
  - Hiện thực hóa Evaluation Runner hỗ trợ 4 hệ thống: Baseline A (Direct LLM), Baseline B (Generic Tutor), Proposed C (Structured Scaffolding), Proposed D (Full Adaptive Tutor).
  - Xây dựng Tutoring Metrics Suite tính toán độc lập 11 chỉ số sư phạm cốt lõi (Diagnosis Accuracy, Localization, Error Category, KC F1, Misconception, No-Bug FPR, Insufficient-Context, Evidence Faithfulness, Solution Leakage, JSON Valid, Hint Policy) cùng độ trễ và chi phí.
  - Bổ sung các ca kiểm thử unit test tính tay độc lập (`test_tutoring_metrics.py`).
- **Nghiên Cứu Triệt Tiêu Thành Phần (Ablation Study - APT-030):**
  - Xây dựng 5 cấu hình triệt tiêu độc lập: `FULL`, `NO_STUDENT_MODEL`, `NO_PROGRESSIVE_HINT`, `NO_STRUCTURED_DIAGNOSIS`, `DIRECT_BASELINE`.
  - Tự động sinh các bản ghi manifest bất biến ghi nhận git commit, mã băm split, và siêu tham số.
- **Thực Thi Giao Thức Đóng Băng (Frozen Experimental Protocol - APT-031):**
  - Kiểm định tự động 6 điều kiện đóng băng nghiêm ngặt trước khi chạy test split.
  - Lưu trữ toàn bộ kết quả dự đoán và xuất báo cáo không lỗi `runs/failure_report.json`.
- **Phân Tích Thống Kê Chuyên Sâu (APT-032):**
  - Tích hợp kiểm định ghép cặp McNemar có hiệu chỉnh liên tục Edwards và tính khoảng tin cậy Bootstrap 95% (1,000 resamples).
  - Phân tích định tính sâu trên 6 dạng lỗi sư phạm, xuất các bảng JSON, CSV và báo cáo `results/ANALYSIS_SUMMARY.md`.
- **Kiểm Định Sẵn Sàng Vận Hành (Production Readiness - APT-034):**
  - Xây dựng công cụ kiểm định tự động `scripts/validate_production_readiness.py` xác minh 18 luồng chức năng và 7 tiêu chuẩn an ninh hệ thống với 100% kết quả PASS (`docs/release/PRODUCTION_VALIDATION.md`).
- **Bộ Tài Liệu Nghiên Cứu & Phát Hành Tái Lập (APT-033, APT-035):**
  - Hoàn thiện tài liệu hướng dẫn tái lập `REPRODUCIBILITY.md`.
  - Xuất bản thẻ dữ liệu chuẩn mực `DATASET_CARD.md` và thẻ hệ thống `SYSTEM_CARD.md`.
  - Viết mới và đồng bộ toàn bộ tài liệu dự án: `README.md`, `ARCHITECTURE.md`, `API_DOCUMENTATION.md`, `PRIVACY_DESIGN.md`, `TESTING.md`, `ROADMAP.md`, `PROBLEM_STATEMENT.md`, `RESEARCH_QUESTIONS.md`, `DATASET_PROTOCOL.md`, `EVALUATION_PROTOCOL.md`.

### Đã Thay Đổi & Làm Sạch (Changed & Cleaned)
- Loại bỏ hoàn toàn các tuyên bố lỗi thời về phân tích cảm xúc hội thoại khỏi tài liệu hoạt động của hệ thống.
- Phân định minh bạch toàn bộ các tính năng theo 4 tầng chuẩn mực: `implemented`, `planned`, `experimental`, `future work`.

---

## [v0.1.0] - Giai Đoạn Khởi Thảo (Baseline Archive)
- Trạng thái baseline nguyên bản của hệ thống được bảo lưu và đóng băng an toàn tại git tag `love-sense-ai-final` và tài liệu lưu trữ `docs/pivot/BASELINE.md`.
