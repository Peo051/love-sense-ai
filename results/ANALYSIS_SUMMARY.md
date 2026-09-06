# Báo Cáo Phân Tích Thực Nghiệm Khoa Học (Experimental Analysis Report)

> [!CAUTION]
> **CẢNH BÁO TÍNH TOÀN VẸN NGHIÊN CỨU (RESEARCH INTEGRITY WARNING):**  
> Toàn bộ các bảng số liệu, chỉ số hiệu năng (100% Accuracy, F1 = 1.000, 0% Leakage) và kiểm định McNemar trong báo cáo này thuộc phiên bản lịch sử `codesense-research-v1.0` và **ĐÃ BỊ HỦY BỎ HIỆU LỰC HOÀN TOÀN (INVALIDATED)** theo kết luận kiểm toán độc lập [APT-047](../docs/audit/APT047_EVALUATION_INTEGRITY_VERDICT.md) (commit `4b07ec2`).  
> - Bảng phân loại chi tiết: xem [V1_RESULT_STATUS.md](../docs/research/V1_RESULT_STATUS.md).  
> - Bộ dữ liệu `VietCSharpTutor-600` được định danh là: **INTERNAL REGRESSION BENCHMARK ONLY**.  
> - Các tệp kết quả lịch sử được bảo toàn nguyên trạng phục vụ đối soát kiểm toán học thuật.

---


Báo cáo phân tích toàn diện trên tập **Test Split Đóng Băng (Frozen Test Split - 120 mẫu)** của bộ dữ liệu `VietCSharpTutor-600`.

---

## 1. Bảng So Sánh Hiệu Năng Tổng Thể (Systems Overall Comparison)
| Hệ Thống Đánh Giá | Diag Acc (95% CI) | Loc Acc | Error Cat Acc | KC F1 | Leakage Rate | Hint Policy | Chi Phí (USD) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline_A** | `71.7% [64.2%, 79.2%]` | `38.5%` | `69.2%` | `0.000` | `100.0%` | `0.0%` | `$0.02641` |
| **Baseline_B** | `74.2% [65.8%, 81.7%]` | `58.3%` | `67.5%` | `0.323` | `3.1%` | `100.0%` | `$0.03074` |
| **Proposed_C** | `88.3% [82.5%, 93.3%]` | `86.5%` | `94.2%` | `0.895` | `0.0%` | `100.0%` | `$0.03574` |
| **Proposed_D** | `100.0% [100.0%, 100.0%]` | `100.0%` | `100.0%` | `1.000` | `0.0%` | `100.0%` | `$0.04034` |

---

## 2. Kết Quả Kiểm Định Thống Kê Ghép Cặp (Paired McNemar Test)
| Cặp So Sánh | Đột Phá Tuyệt Đối ($\Delta$) | Chi-square ($\chi^2$) | p-value | Ý Nghĩa Thống Kê ($p < 0.01$) | Odds Ratio |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `Proposed_C_vs_Baseline_A` | `+29.2%` | `21.8113` | `0.0` | **CÓ Ý NGHĨA** (p < 0.01) | `4.889` |
| `Proposed_C_vs_Baseline_B` | `+16.7%` | `8.5952` | `0.00337` | **CÓ Ý NGHĨA** (p < 0.01) | `2.818` |
| `Proposed_D_vs_Proposed_C` | `+11.7%` | `12.0714` | `0.00051` | **CÓ Ý NGHĨA** (p < 0.01) | `inf` |
| `FULL_vs_NO_STUDENT_MODEL` | `+6.7%` | `6.125` | `0.01333` | CÓ Ý NGHĨA (p < 0.05) | `inf` |
| `FULL_vs_NO_PROGRESSIVE_HINT` | `+0.0%` | `0.0` | `1.0` | Không đáng kể | `1.0` |
| `FULL_vs_NO_STRUCTURED_DIAGNOSIS` | `+29.2%` | `33.0286` | `0.0` | **CÓ Ý NGHĨA** (p < 0.01) | `inf` |
| `FULL_vs_DIRECT_BASELINE` | `+30.8%` | `35.027` | `0.0` | **CÓ Ý NGHĨA** (p < 0.01) | `inf` |

---

## 3. Nghiên Cứu Triệt Tiêu Thành Phần (Ablation Study)
| Cấu Hình Ablation | Diag Acc | Solution Leakage | Hint Policy | JSON Valid | Ghi Chú Sư Phạm |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `FULL` | `100.0%` | `0.0%` | `100.0%` | `100.0%` | Pipeline hoàn chỉnh, hiệu năng sư phạm toàn diện nhất |
| `NO_STUDENT_MODEL` | `93.3%` | `0.0%` | `100.0%` | `100.0%` | Thiếu mô hình học viên -> suy luận quan niệm sai lầm kém hơn |
| `NO_PROGRESSIVE_HINT` | `100.0%` | `100.0%` | `0.0%` | `100.0%` | Rò rỉ giải pháp nghiêm trọng (tiết lộ code ngay từ hint 1) |
| `NO_STRUCTURED_DIAGNOSIS` | `76.7%` | `0.0%` | `100.0%` | `66.7%` | Bỏ JSON schema -> tỷ lệ tuân thủ và localization giảm mạnh |
| `DIRECT_BASELINE` | `85.0%` | `100.0%` | `0.0%` | `100.0%` | Baseline thông thường -> tỷ lệ rò rỉ giải pháp cao, không có KCs |

---

## 4. Báo Cáo Phân Tích Lỗi Định Tính (Qualitative Error Analysis)
- **Số ca chẩn đoán sai (False Diagnoses):** `0`
- **Số ca ảo giác lỗi trên code đúng (No-Bug Hallucinations):** `0`
- **Số ca rò rỉ mã giải pháp sớm (Solution Leakages):** `0`
- **Số ca định vị lệch dòng lỗi (Wrong Bug Localization):** `0`
- **Số ca nhận diện sai quan niệm (Incorrect Misconceptions):** `0`
- **Số ca vi phạm chính sách gợi ý (Poor Hints):** `0`

### Kết luận khoa học:
1. **RQ1 (Chẩn đoán cấu trúc):** Hệ thống có định dạng có cấu trúc (`Proposed C & D`) vượt trội có ý nghĩa thống kê ($p < 0.001$) so với Direct Prompting (`Baseline A`) về độ chính xác chẩn đoán và định vị lỗi.
2. **RQ2 (Chính sách gợi ý tăng dần):** Việc áp dụng 3 bậc thang gợi ý giúp triệt tiêu hoàn toàn hiện tượng rò rỉ giải pháp ($0.0\%$ so với $>60\%$ ở Baseline A và biến thể NO_PROGRESSIVE_HINT).
3. **RQ3 (Mô hình hóa người học):** Khi tích hợp thông tin lịch sử nộp bài và trạng thái thuần thục (Mastery), độ chính xác suy luận quan niệm sai lầm và độ thích ứng của lời giải thích đạt mức cao nhất ($>90\%$).
