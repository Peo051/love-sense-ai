# Hướng Dẫn Tái Lập Nghiên Cứu Độc Lập (Reproducibility Guide)

Tài liệu hướng dẫn bất kỳ nhà nghiên cứu hoặc kỹ sư độc lập nào có thể **tái lập 100%** toàn bộ kết quả thực nghiệm và số liệu công bố của dự án **CodeSense AI** và bộ dữ liệu **VietCSharpTutor-600**.

- **Phiên bản phát hành:** `codesense-research-v1.0`
- **Mã băm tập Test Split đóng băng (SHA-256):** `719fd445444ff9f42e6989729236c8a64773cdd96344fd61307c532457516de4`
- **Ngôn ngữ thực nghiệm:** Python 3.11+ / C# .NET 8 / Node.js 20 LTS

---

## 1. Yêu Cầu Môi Trường & Cài Đặt (Prerequisites)

### 1.1. Sao chép mã nguồn (Clone Repository)
```bash
git clone https://github.com/Peo051/love-sense-ai.git
cd love-sense-ai
git checkout codesense-research-v1.0
```

### 1.2. Thiết lập Môi trường Python
```bash
cd backend
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
cd ..
```

---

## 2. Quy Trình Tái Lập 4 Bước (Step-by-Step Reproduction)

### Bước 1: Kiểm Định Toàn Vẹn Bộ Dữ Liệu VietCSharpTutor-600
Kiểm tra cấu trúc 25 trường, ràng buộc ngữ nghĩa và xác nhận rò rỉ ranh giới split bằng 0 (Zero Family Leakage):
```bash
python scripts/validate_vietcsharptutor.py \
  --data data/vietcsharptutor/vietcsharptutor_600.jsonl \
  --schema data/vietcsharptutor/schema.json \
  --report data/vietcsharptutor/benchmark_report.md
```
- **Kết quả kỳ vọng:** `THÀNH CÔNG: Toàn bộ 600 mẫu đều hợp lệ theo chuẩn VietCSharpTutor!`
- `Rò rỉ split: False` (Zero leakage across 60 problem families).

### Bước 2: Chạy Toàn Bộ Kiểm Thử Tự Động (Automated Tests)
Xác nhận tính ổn định của mã nguồn và thuật toán tính toán chỉ số:
```bash
cd backend
pytest -v
cd ..
```
- **Kết quả kỳ vọng:** 275 bài kiểm thử `PASSED` (bao gồm các bài test tính tay độc lập cho 11 metrics và kiểm định rò rỉ dữ liệu).

### Bước 3: Thực Thi Frozen Experimental Protocol
Khởi chạy thực nghiệm trên tập Validation và tập Test Split đóng băng cho cả 4 hệ thống (Baseline A, Baseline B, Proposed C, Proposed D) và 5 cấu hình Ablation:
```bash
python scripts/execute_frozen_protocol.py
```
- **Kết quả kỳ vọng:**
  - Xác nhận 6 điều kiện đóng băng đạt chuẩn (Git commit, Dataset version, Test hash, Prompts, Models, Config).
  - Hoàn thành tất cả các runs và lưu trữ predictions tại thư mục `runs/`.
  - Báo cáo lỗi `runs/failure_report.json` ghi nhận: `total_failures: 0`.
  - Manifest master lưu tại: `manifests/FROZEN_PROTOCOL_MANIFEST.json`.

### Bước 4: Tái Lập Phân Tích Thống Kê & Bảng Kết Quả
Đọc toàn bộ file predictions đã lưu và tái tạo bảng số liệu khoa học:
```bash
python scripts/analyze_results.py
```
- **Kết quả kỳ vọng:**
  - Xuất bảng so sánh tổng thể: `results/overall_comparison.csv`.
  - Xuất kết quả kiểm định McNemar: `results/statistical_tests.json` (Proposed C vs Baseline A: $p < 0.001$, Proposed D vs Proposed C: $p < 0.001$).
  - Xuất phân tích triệt tiêu: `results/ablation_results.json`.
  - Xuất báo cáo tổng hợp Markdown: `results/ANALYSIS_SUMMARY.md`.

---

## 3. Kiểm Định Tính Bất Biến & An Toàn Dữ Liệu (Integrity Verification)

Mọi tệp tin sinh ra từ quá trình thực nghiệm đều đi kèm file `manifest.json` ghi nhận:
- Mã băm SHA-256 của tập dữ liệu và split tương ứng.
- Commit hash của git repository tại thời điểm chạy.
- Seed số ngẫu nhiên (`seed=42`).
- Tuyệt đối KHÔNG chứa API keys, token bảo mật hay dữ liệu sinh viên nhạy cảm.

---

## 4. Liên Hệ Hỗ Trợ Kỹ Thuật
Nếu gặp bất kỳ sự cố nào trong quá trình tái lập, vui lòng mở Issue trên GitHub repository hoặc tham khảo tài liệu [DATASET_CARD.md](DATASET_CARD.md) và [SYSTEM_CARD.md](SYSTEM_CARD.md).
