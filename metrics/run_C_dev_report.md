# Báo Cáo Đánh Giá Sư Phạm: run_C_dev_20260906_103331

- **Tổng số mẫu đánh giá:** `360`
- **Thời gian phản hồi trung bình:** `288.67 ms` (P50: `292.04 ms`, P95: `404.54 ms`)
- **Tổng Tokens tiêu thụ:** `321584` (Prompt: `188223`, Completion: `133361`)
- **Ước tính chi phí:** `$0.10825 USD`

---

## 1. Các Chỉ Số Sư Phạm Cốt Lõi (Overall Metrics)
| Chỉ Số Đánh Giá | Giá Trị Đạt Được | Ý Nghĩa Sư Phạm |
| :--- | :--- | :--- |
| **Diagnosis Accuracy** | `88.89%` | Độ chính xác nhận diện đúng lỗi |
| **Bug Localization Accuracy** | `88.19%` | Định vị chính xác dòng và symbol lỗi |
| **Error Category Accuracy** | `92.50%` | Phân loại đúng nhóm lỗi kỹ thuật |
| **Knowledge Component F1** | `0.8989` | F1 gắn thẻ kiến thức thành phần (KCs) |
| **Misconception Accuracy** | `88.19%` | Suy luận đúng quan niệm sai lầm của người học |
| **No-Bug False Positive Rate** | `11.11%` | Tỷ lệ báo lỗi oan trên code đúng (càng thấp càng tốt) |
| **Insufficient-Context Accuracy** | `94.44%` | Khả năng phát hiện code bị khuyết ngữ cảnh |
| **Evidence Faithfulness** | `100.00%` | Bằng chứng trích xuất nguyên văn từ bài làm |
| **Solution Leakage Rate** | `0.00%` | Tỷ lệ lộ code giải pháp ở Hint 1 & 2 (càng thấp càng tốt) |
| **JSON Valid Rate** | `100.00%` | Tỷ lệ tuân thủ định dạng dữ liệu có cấu trúc |
| **Hint Policy Compliance** | `100.00%` | Tuân thủ 3 bậc thang gợi ý sư phạm |

---

## 2. Chi Tiết Theo Từng Chủ Đề OOP (Per-Topic Breakdown)
| Chủ Đề (`topic`) | Diag Acc | Loc Acc | Error Cat | KC F1 | Leakage | Policy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `class_object` | 88.9% | 88.9% | 100.0% | 0.944 | 0.0% | 100.0% |
| `constructor_this` | 77.8% | 77.8% | 77.8% | 0.778 | 0.0% | 100.0% |
| `correct_code` | 88.9% | 0.0% | 88.9% | 0.933 | 0.0% | 0.0% |
| `encapsulation_validation` | 88.9% | 88.9% | 88.9% | 0.889 | 0.0% | 100.0% |
| `field_property` | 94.4% | 94.4% | 100.0% | 0.944 | 0.0% | 100.0% |
| `getter_setter` | 91.7% | 91.7% | 91.7% | 0.917 | 0.0% | 100.0% |
| `inheritance_polymorphism` | 83.3% | 83.3% | 83.3% | 0.833 | 0.0% | 100.0% |
| `insufficient_context` | 94.4% | 0.0% | 94.4% | 0.944 | 0.0% | 0.0% |
| `method_parameter` | 91.7% | 91.7% | 100.0% | 0.917 | 0.0% | 100.0% |
| `static_instance` | 88.9% | 88.9% | 100.0% | 0.889 | 0.0% | 100.0% |
