# PHÁN QUYẾT CHÍNH THỨC VỀ TÍNH TOÀN VẸN CỦA PIPELINE ĐÁNH GIÁ (APT-047)

> **Chức danh kiểm toán**: Independent Research Auditor (Kiểm toán viên Nghiên cứu Độc lập)  
> **Dự án kiểm toán**: CodeSense AI - Adaptive Programming Tutor  
> **Phiên bản được kiểm toán**: `codesense-research-v1.0`  
> **Bộ dữ liệu chuẩn hóa**: `VietCSharpTutor-600`  
> **Nhánh kiểm toán**: `audit/evaluation-integrity-v1`  
> **Các tài liệu căn cứ**: `APT040_AUDIT_BASELINE.md` đến `APT046_MOCK_CACHE_FALLBACK.md`  
> **Ngày ban hành phán quyết**: 2026-09-06  

---

## 1. PHÁN QUYẾT TỐI CAO (FINAL VERDICT)

# 🛑 PHÁN QUYẾT: FAIL (KHÔNG ĐẠT)

Toàn bộ pipeline đánh giá nghiên cứu của CodeSense AI trên benchmark `VietCSharpTutor-600` **hoàn toàn không đạt các tiêu chuẩn tối thiểu về tính trung thực, tính tái lập và tính hợp lệ khoa học**.

### Lý do cốt lõi:
1. **Hoàn toàn không có suy luận LLM thực tế**: Trong toàn bộ quá trình chạy thử nghiệm được báo cáo, **không có bất kỳ yêu cầu suy luận thực tế nào được gửi tới mô hình ngôn ngữ lớn (real LLM inference = 0)**.
2. **Sao chép trực tiếp 100% nhãn vàng (Ground Truth Copying)**: Module thực thi đánh giá (`backend/app/evaluation/runner.py`) là một mock engine nội bộ, trực tiếp gán các trường nhãn vàng từ tập dữ liệu vào từ điển dự đoán (`predictions`).
3. **Số liệu tài nguyên giả tạo**: Độ trễ suy luận, lượng token tiêu thụ và chi phí ước tính được tạo ra hoàn toàn bằng các hàm số ngẫu nhiên (`random.uniform` và `random.randint`).
4. **Không có giá trị đối chứng khoa học**: Toàn bộ các chỉ số đạt mức tuyệt đối 100% và các kết luận về sự vượt trội của Proposed D so với các Baseline/Proposed C hoàn toàn là sản phẩm nhân tạo của mã nguồn Python cục bộ.

---

## 2. TRẢ LỜI DỨT KHOÁT 13 CÂU HỎI BẮT BUỘC

| STT | Câu hỏi kiểm toán bắt buộc | Kết luận kiểm toán | Bằng chứng kỹ thuật thực tế |
|:---:|---|:---:|---|
| 1 | **Did Baseline A use real LLM inference?** | **KHÔNG (NO)** | Sử dụng heuristic cục bộ tách chuỗi compiler_error và gán topic. Hoàn toàn không gọi LLM. |
| 2 | **Did Baseline B use real LLM inference?** | **KHÔNG (NO)** | Sinh dự đoán giả lập nội bộ trong `EvaluationRunner._predict_single` với nhiễu nhân tạo. |
| 3 | **Did Proposed C use real LLM inference?** | **KHÔNG (NO)** | Chạy qua nhánh mock nội bộ, sao chép 100% nhãn vàng từ sample dict. Không có kết nối mạng. |
| 4 | **Did Proposed D use real LLM inference?** | **KHÔNG (NO)** | Chạy qua cùng nhánh mock nội bộ với Proposed C, sao chép trực tiếp toàn bộ ground truth. |
| 5 | **Did any system directly copy ground truth?** | **CÓ (YES)** | Cả Proposed C và Proposed D đều sao chép trực tiếp 100% các trường nhãn vàng vào kết quả. |
| 6 | **Can ground truth reach prediction construction?** | **CÓ (YES)** | `sample` chứa đủ 26 trường được truyền trực tiếp vào hàm `_predict_single` không qua lọc. |
| 7 | **Can student context contain current-sample gold annotations?** | **CÓ (YES)** | Các trường nhãn vàng của mẫu hiện tại (`possible_misconception`, `knowledge_components`) được tái nhúng vào context. |
| 8 | **Are Proposed C and D scientifically comparable?** | **KHÔNG (NO)** | Bị nhiễu hoàn toàn (confounded). Khác biệt bắt nguồn từ mã mock tự quy định, không phải do ngữ cảnh học viên. |
| 9 | **Can research mode silently fall back to mock?** | **CÓ (YES)** | Thực tế còn nghiêm trọng hơn: Runner LUÔN LUÔN chạy mock 100%, bất kể tham số `--mock False`. |
| 10 | **Can metrics distinguish synthetic and real predictions?** | **KHÔNG (NO)** | `evaluate_metrics.py` hoàn toàn mù về nguồn gốc (provenance-blind), chỉ so khớp 2 dict JSON. |
| 11 | **Which V1 metrics remain interpretable?** | **CHỈ CÓ THỐNG KÊ MÔ TẢ DATASET** | Chỉ có phân bố số dòng mã, phân loại lỗi compiler ban đầu của tập dữ liệu là có giá trị tham khảo. |
| 12 | **Which V1 metrics must be invalidated?** | **TẤT CẢ CHỈ SỐ ĐÁNH GIÁ V1** | Toàn bộ độ chính xác chẩn đoán, F1-score, chất lượng gợi ý, độ trễ và chi phí phải bị HỦY BỎ. |
| 13 | **Is the current evaluation pipeline suitable for future research?** | **HOÀN TOÀN KHÔNG** | Phải bị đóng băng và thay thế hoàn toàn bằng Clean-Room Evaluation Pipeline trước khi thử nghiệm lại. |

---

## 3. TỔNG HỢP CÁC PHÁT HIỆN KIỂM TOÁN (DETAILED FINDINGS)

### Nhóm Phát hiện Nghiêm trọng (CRITICAL FINDINGS)

#### [F-01] Total Absence of Real LLM Client in Research Evaluation Runner
- **Mức độ**: `CRITICAL`
- **Hệ thống bị ảnh hưởng**: Toàn bộ các hệ thống đánh giá (Baseline A, B, Proposed C, D).
- **Bằng chứng kỹ thuật**: Trong `backend/app/evaluation/runner.py` (dòng 204–346), không hề tồn tại bất kỳ import hoặc lệnh gọi nào tới các thư viện `google.generativeai`, `openai`, `httpx`, hay `requests`.
- **Hành vi quan sát**: Lệnh `python scripts/run_evaluation.py --provider gemini --model gemini-2.5-flash` hoàn thành trong vài giây mà không gửi bất kỳ gói tin mạng nào ra ngoài.
- **Hành vi kỳ vọng**: Phải thực hiện suy luận mô hình ngôn ngữ thực tế qua API endpoint chính thức của nhà cung cấp.
- **Tác động khoa học**: Báo cáo công bố kết quả suy luận của LLM là hoàn toàn không có thật; mô hình AI thực tế chưa từng được đánh giá.
- **Tác động kỹ thuật**: Pipeline đánh giá hoàn toàn bị cô lập khỏi hạ tầng cung cấp mô hình thực.
- **Hành động khắc phục**: Xây dựng lại runner với Network Client thật kết nối API và xác thực khóa truy cập.

#### [F-02] Direct Copying of Ground Truth into Saved Predictions
- **Mức độ**: `CRITICAL`
- **Hệ thống bị ảnh hưởng**: Proposed C, Proposed D.
- **Bằng chứng kỹ thuật**: Trong `backend/app/evaluation/runner.py`:
  ```python
  prediction["bug_location"] = sample.get("bug_location")
  prediction["knowledge_components"] = sample.get("knowledge_components")
  prediction["hints"] = [sample.get("hint_1"), sample.get("hint_2"), sample.get("hint_3")]
  prediction["explanation_vi"] = sample.get("explanation_vi")
  ```
- **Hành vi quan sát**: Toàn bộ các trường dự đoán trùng khớp từng ký tự với nhãn vàng trong tập dữ liệu kiểm thử.
- **Hành vi kỳ vọng**: Dự đoán phải được sinh ra thuần túy từ văn bản phản hồi do mô hình AI tạo ra.
- **Tác động khoa học**: Điểm số hoàn hảo 100% là sản phẩm của toán tử gán biến trong Python, không phải năng lực suy luận của hệ thống AI.
- **Tác động kỹ thuật**: Nhãn vàng bị rò rỉ trực tiếp vào kho lưu trữ kết quả đầu ra.
- **Hành động khắc phục**: Áp dụng tầng cách ly `ModelInput`, chỉ truyền 4 trường đầu vào của bài toán.

#### [F-03] Silent Offline Execution Without Fail-Loud Safety
- **Mức độ**: `CRITICAL`
- **Hệ thống bị ảnh hưởng**: Evaluation Runner Pipeline.
- **Bằng chứng kỹ thuật**: Khi ngắt hoàn toàn kết nối mạng và không đặt bất kỳ biến môi trường API key nào, lệnh đánh giá vẫn chạy trọn vẹn với mã thoát 0.
- **Hành vi quan sát**: Runner âm thầm chạy và báo cáo thành công mà không đưa ra bất kỳ cảnh báo lỗi nghiêm trọng nào.
- **Hành vi kỳ vọng**: Hệ thống nghiên cứu phải dừng lập tức (Fail Loudly) và báo lỗi cấu hình nếu thiếu API key hoặc không có mạng.
- **Tác động khoa học**: Dẫn đến việc công bố các kết quả giả lập mà người thực hiện tưởng rằng là kết quả thật.
- **Tác động kỹ thuật**: Thiếu cơ chế kiểm soát lỗi nghiêm ngặt (circuit breaker) trong pipeline thử nghiệm.
- **Hành động khắc phục**: Cài đặt cơ chế kiểm tra kết nối và tính hợp lệ của API key trước khi khởi chạy batch.

#### [F-04] Synthetic and Randomized Computational Resource Metrics
- **Mức độ**: `CRITICAL`
- **Hệ thống bị ảnh hưởng**: Manifest and Resource Benchmarking.
- **Bằng chứng kỹ thuật**: Trong `backend/app/evaluation/runner.py`:
  ```python
  latency_ms = random.uniform(150.0, 420.0)
  total_tokens = random.randint(300, 850)
  cost = total_tokens * rate
  ```
- **Hành vi quan sát**: Độ trễ và số token tiêu thụ được tạo ra bằng module `random` của Python.
- **Hành vi kỳ vọng**: Độ trễ phải đo bằng đồng hồ bấm giờ thời gian thực (`time.perf_counter`) và token phải lấy từ metadata phản hồi của API.
- **Tác động khoa học**: Các phân tích về hiệu quả tài nguyên, độ trễ và chi phí vận hành trong bài báo là vô nghĩa.
- **Tác động kỹ thuật**: Báo cáo giám sát tài nguyên không phản ánh đúng năng lực tính toán của hệ thống.
- **Hành động khắc phục**: Đo đạc độ trễ mạng thực và trích xuất token usage thực tế từ API response.

---

### Nhóm Phát hiện Nghiêm trọng Bổ sung (HIGH FINDINGS)

#### [F-05] Complete Absence of ModelInput Abstraction Layer
- **Mức độ**: `HIGH`
- **Bằng chứng kỹ thuật**: Dataset loader trả về dictionary chứa toàn bộ 26 trường của sample và chuyển thẳng vào runner mà không có lớp lọc dữ liệu.
- **Tác động**: Gây ô nhiễm dữ liệu nhãn vàng xuyên suốt toàn bộ vòng đời thực nghiệm.

#### [F-06] Provenance-Blind Metric Calculator
- **Mức độ**: `HIGH`
- **Bằng chứng kỹ thuật**: `evaluate_metrics.py` chỉ đọc hai tệp JSONL và so khớp chuỗi mà không thẩm định chữ ký số hay manifest nguồn gốc của tệp dự đoán.
- **Tác động**: Không thể phân biệt được tệp dự đoán do LLM thật sinh ra hay do mã mock giả lập.

#### [F-07] Confounded Experimental Comparison (Proposed C vs Proposed D)
- **Mức độ**: `HIGH`
- **Bằng chứng kỹ thuật**: Cả hai hệ thống đều chạy trên cùng mã mock nội bộ; sự khác biệt về kết quả do code tự định nghĩa sẵn.
- **Tác động**: Mất hoàn toàn giá trị khoa học của luận điểm 'Ngữ cảnh học viên nâng cao độ chính xác chẩn đoán'.

#### [F-08] Unverified Cache and Prediction File Reuse
- **Mức độ**: `MEDIUM`
- **Bằng chứng kỹ thuật**: Các tệp `predictions.jsonl` có thể được tái sử dụng mù mà không gắn với commit hash hay run hash duy nhất.
- **Tác động**: Làm giảm tính minh bạch và khả năng tái lập độc lập của nghiên cứu.

---

## 4. DANH MỤC KẾT QUẢ BỊ HỦY BỎ VÀ ĐƯỢC GIỮ LẠI

### ❌ Danh mục Kết quả BỊ HỦY BỎ HIỆU LỰC (INVALIDATED RESULTS)
Toàn bộ các chỉ số dưới đây được công bố trong phiên bản `codesense-research-v1.0` **CHÍNH THỨC BỊ HỦY BỎ VÀ KHÔNG CÒN GIÁ TRI KHOA HỌC**:
1. **Overall Diagnosis Accuracy** (100.0% trên Proposed D) — *Bị hủy bỏ do sao chép nhãn vàng.*
2. **Bug Localization Accuracy** (100.0% trên Proposed D) — *Bị hủy bỏ do sao chép nhãn vàng.*
3. **Error Category Accuracy** (100.0% trên Proposed D) — *Bị hủy bỏ do sao chép nhãn vàng.*
4. **Knowledge Component Detection F1-Score** (1.000 trên Proposed D) — *Bị hủy bỏ do sao chép nhãn vàng.*
5. **Misconception Identification F1-Score** (1.000 trên Proposed D) — *Bị hủy bỏ do sao chép nhãn vàng.*
6. **Hint Quality Metrics** (Relevance = 1.000, Actionability = 1.000) — *Bị hủy bỏ do sao chép gợi ý vàng.*
7. **Inference Latency Metrics** (Trung bình 285.4 ms) — *Bị hủy bỏ do sinh ngẫu nhiên.*
8. **Token Consumption and Operational Cost** — *Bị hủy bỏ do sinh ngẫu nhiên.*
9. **Ablation Study Deltas** (Mức cải thiện của Proposed D so với Proposed C) — *Bị hủy bỏ do so sánh trên dữ liệu mock.*

###  Danh mục Kết quả ĐƯỢC BẢO TOÀN (UNAFFECTED RESULTS)
1. **Chất lượng nội dung bộ dữ liệu gốc `VietCSharpTutor-600`**: 600 bài toán lập trình C#, mã nguồn sinh viên và nhãn vàng sư phạm do chuyên gia biên soạn được bảo toàn giá trị làm benchmark chuẩn.
2. **Thống kê mô tả tập dữ liệu**: Phân bố chủ đề, độ dài mã nguồn, phân loại lỗi compiler ban đầu.
3. **Công thức toán học tính chỉ số**: Các công thức Exact Match, Token Set Jaccard và F1-Score trong `evaluate_metrics.py` là chuẩn xác về mặt lý thuyết.

---

## 5. CÁC ĐIỀU KIỆN CHẶN KHẮC PHỤC (BLOCKING REMEDIATION REQUIREMENTS)

Để pipeline đánh giá có thể được sử dụng hợp lệ cho các công bố khoa học trong tương lai, toàn bộ **6 điều kiện chặn sau đây phải được khắc phục triệt để**:

- [ ] **BLOCKER-01: Kiến trúc ModelInput cô lập nghiêm ngặt (Whitelist-only)**  
  Xây dựng lớp dữ liệu `ModelInput` bất biến chỉ chứa 4 trường đầu vào của học viên (`id`, `student_code`, `compiler_error`, `problem_statement_vi`). Tuyệt đối loại bỏ 100% nhãn vàng trước khi chuyển vào runner.
- [ ] **BLOCKER-02: Tích hợp Network Client gọi LLM thực tế**  
  Tích hợp thư viện chính thức kết nối Google Gemini API / OpenAI API. Xóa bỏ vĩnh viễn nhánh sao chép nhãn vàng trong `runner.py`.
- [ ] **BLOCKER-03: Chính sách thực thi dừng khi lỗi (Fail-Loud Enforcement)**  
  Nghiêm cấm cơ chế fallback ngầm về mock trong pipeline nghiên cứu. Khi thiếu API key hoặc lỗi mạng, hệ thống phải ném ngoại lệ dừng ngay lập tức.
- [ ] **BLOCKER-04: Đo đạc tài nguyên thực tế (Real Telemetry Instrumentation)**  
  Đo độ trễ bằng `time.perf_counter()` thực tế cho mỗi HTTP request; đọc số lượng token trực tiếp từ metadata phản hồi của API nhà cung cấp.
- [ ] **BLOCKER-05: Xác thực nguồn gốc thực nghiệm (Cryptographic Run Provenance)**  
  Mỗi lượt chạy phải tạo manifest chứa hash commit git, hash input, tham số mô hình và chữ ký định danh. Bộ tính toán chỉ số chỉ chấp nhận tệp có manifest hợp lệ.
- [ ] **BLOCKER-06: Đóng băng và gắn nhãn các artifact lịch sử**  
  Toàn bộ kết quả V1 cũ phải được gắn nhãn `HISTORICAL - INVALIDATED BY APT-047` và lưu trữ phục vụ đối soát, không ghi đè và không phá hủy.

---

## 6. KÝ DUYỆT KIỂM TOÁN

| Đại diện kiểm toán | Vai trò | Chữ ký điện tử | Phán quyết |
|---|---|---|:---:|
| **Independent Research Auditor** | Trưởng ban Kiểm toán Độc lập | `AUDIT-VERDICT-APT047-FAIL-8D97516` | **FAIL** |
