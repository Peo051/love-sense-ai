# BÁO CÁO KIỂM TOÁN CƠ CHẾ MOCK, CACHE VÀ FALLBACK (APT-046)

> **Mã kiểm toán**: APT-046  
> **Chức danh kiểm toán**: Independent Research Auditor (Kiểm toán viên nghiên cứu độc lập)  
> **Dự án**: CodeSense AI - Adaptive Programming Tutor  
> **Phiên bản đóng băng**: `codesense-research-v1.0`  
> **Nhánh kiểm toán**: `audit/evaluation-integrity-v1`  
> **Ngày thực hiện**: 2026-09-06  

---

## 1. TÓM TẮT ĐIỀU HÀNH (EXECUTIVE SUMMARY)

Mục tiêu tối thượng của nhiệm vụ **APT-046** là trả lời dứt khoát câu hỏi cốt lõi:

> *Liệu các chỉ số đánh giá nghiên cứu (research metrics) của CodeSense AI có thể được sinh ra mà hoàn toàn không cần thực thi suy luận từ mô hình ngôn ngữ lớn (real LLM inference) hay không?*

### Câu trả lời kiểm toán viên: **HOÀN TOÀN CÓ THỂ, VÀ THỰC TẾ ĐÃ DIỄN RA NHƯ VẬY.**

### Các phát hiện chấn động qua rà soát mã nguồn:
1. **Không hề có đường dẫn gọi LLM thật trong Evaluation Runner**: Trong `backend/app/evaluation/runner.py`, mã nguồn hoàn toàn **không chứa bất kỳ thư viện hay client kết nối mạng nào** (`google.generativeai`, `openai`, `httpx`, `requests`). Tham số `--provider` và `--model` chỉ là các biến định danh được ghi lại trong manifest mà không bao giờ kích hoạt lệnh gọi API thực tế.
2. **Quy trình đánh giá chạy trọn vẹn khi KHÔNG CÓ API KEY**: Toàn bộ quy trình đánh giá thực nghiệm có thể chạy ngoại tuyến (offline) 100%, không cần kết nối internet, không cần bất kỳ API key nào, và vẫn sinh ra đầy đủ bộ chỉ số 100% hoàn hảo.
3. **Không có cơ chế Fail Loudly**: Khi thiếu cấu hình nhà cung cấp hoặc mô hình thực tế, runner không hề báo lỗi dừng chương trình mà âm thầm chuyển hướng 100% sang mã mock nội bộ và sao chép nhãn vàng từ ground truth.
4. **Độ trễ và Tokens giả lập**: Các thông số tài nguyên được công bố trong bài báo (`latency_mean_ms`, `total_tokens`, `estimated_cost_usd`) đều được sinh ra từ các hàm số ngẫu nhiên `random.uniform(150.0, 420.0)` và `random.randint(...)`, hoàn toàn không phản ánh tài nguyên điện toán thực tế.

---

## 2. MA TRẬN KIỂM TOÁN 8 KỊCH BẢN CẤU HÌNH AN TOÀN (SAFE CONFIGURATION MATRIX)

| STT | Kịch bản kiểm tra | Hành vi của Runner | Trạng thái Manifest | Rủi ro nhãn vàng | Phân loại kiểm toán |
|:---:|---|---|---|---|:---:|
| 1 | **mock=true (Chế độ mock được bật tường minh hoặc mặc định)** | `USES MOCK` | Ghi nhận 'mock_mode': true trong manifest.json | Có toàn quyền truy cập và sao chép 100% nhãn vàng ground truth | **CRITICAL** |
| 2 | **provider missing (Tham số --provider bị bỏ trống hoặc truyền None)** | `USES MOCK` | Ghi nhận giá trị provider tương ứng mà không xác thực | Vẫn truy cập và sao chép ground truth bình thường | **CRITICAL** |
| 3 | **provider exception (Provider ném ngoại lệ mạng, HTTP 500, lỗi xác thực)** | `USES MOCK (Không bao giờ xảy ra lỗi)` | Không ghi nhận lỗi nào vì không có lệnh gọi mạng | Truy cập trực tiếp trong bộ nhớ | **CRITICAL** |
| 4 | **timeout (Mạng trễ hoặc API hết hạn thời gian phản hồi)** | `USES MOCK (Không bao giờ timeout)` | Ghi nhận độ trễ giả lập latency_ms từ 150ms đến 420ms | Truy cập trực tiếp bộ nhớ | **CRITICAL** |
| 5 | **invalid response (Mô hình trả về JSON hỏng, text rỗng hoặc sai schema)** | `USES MOCK (Luôn sinh JSON chuẩn 100%)` | Ghi nhận 'json_valid': true | Dữ liệu được lấy từ ground truth nên luôn hợp lệ cú pháp | **CRITICAL** |
| 6 | **fallback activation (Kích hoạt mô hình dự phòng khi mô hình chính gặp sự cố)** | `FAILS LOUDLY / NOT IMPLEMENTED` | Không có trường fallback trong evaluation manifest | Không có | **LOW** |
| 7 | **cached prediction reuse (Tái sử dụng các tệp dự đoán đã chạy trước đó)** | `USES CACHE (Tái sử dụng offline)` | Không ghi vết trong tệp metrics nếu chạy evaluate_metrics.py offline | Không trực tiếp (đọc từ predictions.jsonl cũ) | **MEDIUM** |
| 8 | **No API key available (Không cấu hình bất kỳ API key nào: OPENAI_API_KEY, GEMINI_API_KEY)** | `DOES NOT FAIL LOUDLY - USES MOCK` | Ghi nhận run thành công trọn vẹn, exit code 0 | Toàn quyền sao chép nhãn vàng | **CRITICAL** |

---

## 3. CHI TIẾT CÁC CƠ CHẾ MOCK, CACHE VÀ FALLBACK TRONG TOÀN BỘ REPOSITORY

### Cơ chế: EvaluationRunner Internal Mock Engine
- **Tệp & Hàm**: `backend/app/evaluation/runner.py` (`EvaluationRunner._predict_single`, dòng `204-347`)
- **Điều kiện kích hoạt**: Luôn luôn được kích hoạt trong mọi cuộc gọi run()
- **Khả năng tiếp cận trong Research Run**: **CÓ - 100% các run nghiên cứu chính thức đều bắt nguồn từ đây**
- **Khả năng tiếp cận trong Unit Test**: KHÔNG - Đây là runner nghiên cứu chính thức
- **Quyền truy cập nhãn vàng**: **TRUY CẬP VÀ SAO CHÉP TRỰC TIẾP**
- **Cách thức tạo dự đoán**: Gán trực tiếp từ biến sample
- **Hiển thị trong Manifest**: `Ghi nhận 'mock_mode': self.mock`
- **Phân loại rủi ro**: **`CRITICAL`**

### Cơ chế: AblationRunner Internal Mock Engine
- **Tệp & Hàm**: `backend/app/evaluation/ablation.py` (`AblationRunner._predict_sample`, dòng `185-330`)
- **Điều kiện kích hoạt**: Luôn luôn được kích hoạt khi chạy run_ablation.py
- **Khả năng tiếp cận trong Research Run**: **CÓ - 100% các run ablation đều bắt nguồn từ đây**
- **Khả năng tiếp cận trong Unit Test**: KHÔNG
- **Quyền truy cập nhãn vàng**: **TRUY CẬP VÀ SAO CHÉP TRỰC TIẾP, nhúng reference_solution**
- **Cách thức tạo dự đoán**: Gán trực tiếp từ biến sample theo 5 cấu hình
- **Hiển thị trong Manifest**: `Ghi manifest riêng`
- **Phân loại rủi ro**: **`CRITICAL`**

### Cơ chế: DeterministicMockTutorProvider (Unit Test Mock)
- **Tệp & Hàm**: `backend/app/tutor/provider.py` (`DeterministicMockTutorProvider.generate_response`, dòng `72-161`)
- **Điều kiện kích hoạt**: Được khởi tạo trong unit tests với canned response
- **Khả năng tiếp cận trong Research Run**: **KHÔNG - Runner không sử dụng lớp này**
- **Khả năng tiếp cận trong Unit Test**: CÓ - Được cách ly đúng chuẩn trong tests/ conftest.py
- **Quyền truy cập nhãn vàng**: **KHÔNG có quyền truy cập dataset**
- **Cách thức tạo dự đoán**: Trả về chuỗi JSON mẫu cố định
- **Hiển thị trong Manifest**: `Không áp dụng`
- **Phân loại rủi ro**: **`LOW`**

### Cơ chế: Vision OCR Mock Mode
- **Tệp & Hàm**: `backend/app/services/vision_ocr_service.py` (`VisionOCRService.extract_code`, dòng `Đọc LLM_MOCK_MODE`)
- **Điều kiện kích hoạt**: LLM_MOCK_MODE=true trong .env
- **Khả năng tiếp cận trong Research Run**: **KHÔNG - Không tham gia vào benchmark C#**
- **Khả năng tiếp cận trong Unit Test**: CÓ - Dùng cho kiểm thử frontend/OCR
- **Quyền truy cập nhãn vàng**: **Không có**
- **Cách thức tạo dự đoán**: Trả về code C# mẫu cố định
- **Hiển thị trong Manifest**: `Không áp dụng`
- **Phân loại rủi ro**: **`LOW`**

---

## 4. PHÂN TÍCH HIỆN TƯỢNG 'PHANTOM LLM RUNNER' (RUNNER NGỤY TRANG)

Trong thiết kế phần mềm nghiên cứu khoa học, một runner đánh giá tiêu chuẩn phải có kiến trúc tách bạch:
```
Runner CLI  --->  Provider Adapter (Gemini / OpenAI)  --->  Live LLM API  --->  Response Parser
                      | (khi có cờ --mock)
                      v
                  Mock Provider (Không truy cập nhãn vàng)
```

Tuy nhiên, trong `backend/app/evaluation/runner.py`, kiến trúc thực tế là:

```
Runner CLI  --------------------------------------------------->  Hàm _predict_single nội bộ
(--model gemini-2.5-flash)                                                   |
(--provider gemini)                                                           v
(--mock false)                                                    Gán trực tiếp sample['error_category']
                                                                 Gán trực tiếp sample['bug_location']
                                                                 Gán trực tiếp sample['evidence']
                                                                 Gán trực tiếp sample['hints 1-3']
```

> [!CAUTION]
> **KẾT LUẬN VỀ RUNNER NGỤY TRANG**:  
> Cho dù người dùng chạy lệnh:
> ```bash
> python scripts/run_evaluation.py --system D --split test --model gemini-2.5-flash --provider gemini --mock False
> ```
> Hệ thống **VẪN KHÔNG HỀ GỌI GEMINI**, mà chạy thẳng vào đoạn code sao chép nhãn vàng của `sample`! 
> Tham số `--mock False` hoàn toàn vô hiệu hóa do hàm `_predict_single` không hề kiểm tra biến `self.mock`. Đây là một lỗ hổng nghiêm trọng làm biến mất hoàn toàn ranh giới giữa kiểm thử giả lập và nghiên cứu khoa học thực thụ.

---

## 5. KẾT LUẬN KIỂM TOÁN

Đợt kiểm toán **APT-046** đã xác nhận bằng chứng kỹ thuật không thể chối cãi:
1. **Toàn bộ kết quả benchmark đã công bố** trong `codesense-research-v1.0` được tạo ra mà **hoàn toàn không có sự tham gia của mô hình ngôn ngữ lớn thực tế**.
2. **Không có bất kỳ cuộc gọi API nào bị lỗi hoặc timeout**, vì đơn giản là không có cuộc gọi API nào từng được thực hiện.
3. **Toàn bộ dữ liệu điểm số, độ trễ, và số lượng token tiêu thụ** trong các bản báo cáo đánh giá đều là các giá trị nhân tạo được sinh từ các thuật toán sao chép nhãn vàng và các hàm ngẫu nhiên cục bộ.
4. Tệp ma trận kiểm toán chi tiết đã được lưu trữ tại `artifacts/audit/mock_cache_fallback_matrix.json`.
