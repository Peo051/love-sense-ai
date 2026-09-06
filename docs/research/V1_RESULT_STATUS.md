# QUY CHUẨN TRẠNG THÁI HIỆU LỰC KẾT QUẢ NGHIÊN CỨU V1 (V1 RESEARCH RESULT STATUS)

> **Cơ quan ban hành**: Ban Duy trì Tính toàn vẹn Nghiên cứu (Research Integrity Maintainer)  
> **Dự án**: CodeSense AI - Adaptive Programming Tutor  
> **Phiên bản gốc**: `codesense-research-v1.0`  
> **Kiểm toán hủy bỏ hiệu lực**: Kiểm toán độc lập `APT-040` đến `APT-047`  
> **Commit phán quyết hủy bỏ**: `4b07ec2` (Phán quyết `FAIL`)  
> **Ngày ban hành**: 2026-09-06  

---

## 1. TUYÊN BỐ CỐT LÕI VỀ BỘ DỮ LIỆU VIETCSHARPTUTOR-600

> ###  ĐỊNH DANH BẮT BUỘC:
> **VietCSharpTutor-600 được phân loại duy nhất là: BỘ KIỂM THỬ HỒI QUY NỘI BỘ (INTERNAL REGRESSION BENCHMARK ONLY).**  
> Tuyệt đối **KHÔNG ĐƯỢC** gọi đây là một "Bộ benchmark được thẩm định ngoại kiểm" (externally validated benchmark), "Bộ chuẩn quốc tế", hay sử dụng để tuyên bố sự vượt trội tổng quát của mô hình AI trước công chúng hoặc hội đồng khoa học.

- **Mục đích sử dụng hợp lệ:** Kiểm thử hồi quy nội bộ kỹ thuật (functional regression), kiểm tra tính tương thích cú pháp của parser, AST và schema JSON.
- **Mục đích bị nghiêm cấm:** Sử dụng kết quả V1 để công bố hiệu năng suy luận LLM hoặc trích dẫn các chỉ số 100% như thành tựu khoa học thực tế.

---

## 2. PHÂN LOẠI TOÀN DIỆN ARTIFACT VÀ KẾT QUẢ NGHIÊN CỨU V1

Mọi tài liệu, chỉ số, tệp dữ liệu và phát hiện trong phiên bản `codesense-research-v1.0` được phân loại chính thức thành 4 nhóm độc lập:

```
                  ┌────────────────────────────────────────────────────────┐
                  │ HỒ SƠ THỰC NGHIỆM V1 (codesense-research-v1.0)        │
                  └──────────────────────────┬─────────────────────────────┘
                                             │
      ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
      ▼                      ▼                               ▼                      ▼
┌──────────────┐      ┌───────────────┐              ┌───────────────┐      ┌───────────────┐
│ INVALIDATED  │      │DESCRIPTIVE    │              │ UNAFFECTED    │      │ HISTORICAL    │
│ (Hủy bỏ hoàn │      │ONLY           │              │ ENGINEERING   │      │ ONLY          │
│  toàn)       │      │(Chỉ mô tả thô)│              │ (Kỹ thuật tốt)│      │ (Lưu đối soát)│
└──────────────┘      └───────────────┘              └───────────────┘      └───────────────┘
```

---

### NHÓM 1: INVALIDATED (KẾT QUẢ BỊ HỦY BỎ HIỆU LỰC HOÀN TOÀN)
*Toàn bộ các chỉ số dưới đây phát sinh từ mã mock nội bộ sao chép nhãn vàng, không có suy luận LLM thực tế và bị hủy bỏ vĩnh viễn:*

| Chỉ số / Tuyên bố V1 | Giá trị công bố cũ | Tệp nguồn | Lý do hủy bỏ chính thức |
|---|:---:|---|---|
| **Diagnosis Accuracy (Proposed D)** | `100.0%` | `results/ANALYSIS_SUMMARY.md` | Sinh ra từ mã mock sao chép ground truth; 0% LLM inference |
| **Bug Localization Accuracy** | `100.0%` | `results/ANALYSIS_SUMMARY.md` | Gán trực tiếp `sample['bug_location']`; 0% LLM inference |
| **Error Category Accuracy** | `100.0%` | `results/ANALYSIS_SUMMARY.md` | Gán trực tiếp `sample['error_category']`; 0% LLM inference |
| **Knowledge Component F1-Score** | `1.000` | `results/ANALYSIS_SUMMARY.md` | Gán trực tiếp `sample['knowledge_components']`; 0% LLM inference |
| **Misconception Identification F1** | `1.000` | `results/ANALYSIS_SUMMARY.md` | Gán trực tiếp `sample['possible_misconception']`; 0% LLM inference |
| **Zero Solution Leakage (0.0%)** | `0.0%` | `results/ANALYSIS_SUMMARY.md` | Sao chép trực tiếp gợi ý mẫu chuyên gia từ ground truth |
| **Hint Policy Compliance (100%)** | `100.0%` | `results/ANALYSIS_SUMMARY.md` | Sao chép trực tiếp gợi ý mẫu chuyên gia từ ground truth |
| **Kiểm định McNemar ($p < 0.001$)** | $\chi^2 = 12.07, p = 0.00051$ | `results/statistical_tests.json` | Tính toán trên dữ liệu giả lập; không có giá trị thống kê |
| **Độ trễ suy luận trung bình** | `285.4 ms` | `manifests/` | Sinh ngẫu nhiên từ `random.uniform(150.0, 420.0)` |
| **Lượng token & Chi phí suy luận** | Số liệu USD V1 | `manifests/` | Sinh ngẫu nhiên từ `random.randint(300, 850)` |
| **Kết luận các câu hỏi RQ1 - RQ4** | Đạt kết quả tối ưu | `docs/research/RESEARCH_QUESTIONS.md` | Toàn bộ dữ liệu thực nghiệm làm nền tảng là dữ liệu giả lập |

---

### NHÓM 2: DESCRIPTIVE_ONLY (CHỈ MANG Ý NGHĨA THỐNG KÊ MÔ TẢ TẬP DỮ LIỆU)
*Các thuộc tính thô của bộ dữ liệu `VietCSharpTutor-600` được biên soạn giữ nguyên tính xác thực mô tả:*

- **Quy mô bộ dữ liệu:** 600 bài toán lập trình C# hướng đối tượng nhập môn do chuyên gia biên soạn.
- **Phân bố chủ đề & Độ khó:** 10 chủ đề OOP và 3 mức độ khó sư phạm (`beginner`, `easy`, `medium`).
- **Đặc tính mã nguồn:** Độ dài dòng mã của sinh viên và thông báo lỗi trình biên dịch Roslyn nguyên gốc.

---

### NHÓM 3: UNAFFECTED_ENGINEERING (KẾT QUẢ KỸ THUẬT PHẦN MỀM KHÔNG BỊ ẢNH HƯỞNG)
*Các tiêu chuẩn kỹ thuật phần mềm, giao diện và bảo mật của ứng dụng CodeSense AI hoạt động độc lập và hoàn toàn đạt chuẩn:*

- **275 bài kiểm thử tự động Backend (Passing):** Xác minh toàn diện API FastAPI, xác thực Firebase, session tracking, database ORM, phân tích AST, trích xuất OCR.
- **37 bài kiểm thử tự động Frontend (Passing):** Giao diện người dùng, phản hồi Socratic, quản lý state và trải nghiệm học tập.
- **18 Luồng chức năng người dùng cốt lõi (18/18 PASS):** Xem chi tiết tại [PRODUCTION_VALIDATION.md](../release/PRODUCTION_VALIDATION.md).
- **7 Tiêu chuẩn an ninh và quyền riêng tư (7/7 PASS):** Không rò rỉ secret, không lộ code trong log, tách biệt kết quả phân tích và mã nguồn, chính sách xóa dữ liệu GDPR.
- **Deterministic Mock Provider trong Unit Tests:** Triển khai mock cô lập chuẩn mực trong `backend/app/tutor/provider.py` phục vụ unit testing không cần mạng.

---

### NHÓM 4: HISTORICAL_ONLY (HIỆN VẬT LỊCH SỬ ĐƯỢC BẢO TOÀN NGUYÊN TRẠNG)
*Tuân thủ nguyên tắc nghiên cứu minh bạch, toàn bộ các tệp dự đoán và kết quả cũ KHÔNG bị xóa, KHÔNG bị ghi đè, mà được bảo tồn nguyên vẹn để làm bằng chứng kiểm toán đối soát:*

- `runs/run_20260906_103014/` (Chứa tệp predictions thô của V1).
- `manifests/run_manifest_20260906_103014.json` (Manifest lịch sử V1).
- `results/evaluation_results.json`, `results/ablation_results.json`, `results/statistical_tests.json`, `results/overall_comparison.csv`.

---

## 3. NGUYÊN TẮC BẢO QUẢN VÀ THAM CHIẾU LỊCH SỬ

1. **Bảo tồn hiện vật (Preservation without Erasure):** Không xóa bất kỳ tệp thực nghiệm cũ nào. Lịch sử nghiên cứu phải minh bạch và có thể truy nguyên 100%.
2. **Ngăn chặn trích dẫn sai lệch:** Mọi tài liệu nghiên cứu hoạt động đều được gắn biển cảnh báo chỉ dẫn về văn bản này.
3. **Điều kiện gỡ bỏ nhãn:** Nhãn `INVALIDATED` chỉ được gỡ bỏ khi một Clean-Room Evaluation Pipeline mới được xây dựng và kiểm định độc lập hoàn tất theo đúng 6 điều kiện chặn của APT-047.
