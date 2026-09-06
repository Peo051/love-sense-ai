# Chiến Lược & Quy Trình Kiểm Thử (Testing Strategy & Protocol)

Tài liệu hướng dẫn và đặc tả toàn bộ quy trình kiểm thử tự động của hệ thống **CodeSense AI**.

---

## 1. Tổng Quan Chiến Lược Kiểm Thử (Test Pyramid)

Hệ thống áp dụng kim tự tháp kiểm thử đa tầng với 100% tỷ lệ vượt qua (Pass Rate):

```
            / \
           /   \        Production Readiness (18 Flows + 7 Security Checks)
          / E2E \       Vitest Frontend Suite (37 Tests)
         /-------\      
        /  Integ. \     Dataset & Ablation Integration Tests (16 Tests)
       /-----------\    
      /  Unit Tests \   Backend Core & Evaluation Unit Tests (259 Tests)
     /---------------\  
```

- **Backend Unit & Integration Tests:** 275 bài kiểm thử tự động (pytest).
- **Frontend Component & Page Tests:** 37 bài kiểm thử giao diện (vitest).
- **Kiểm định dữ liệu chuẩn mực:** 100% mẫu trong `VietCSharpTutor-600` hợp lệ qua `validate_vietcsharptutor.py`.
- **Kiểm định vận hành Production:** 100% PASS trên 18 luồng chức năng và 7 tiêu chuẩn bảo mật.

---

## 2. Hướng Dẫn Thực Thi Kiểm Thử Cục Bộ

### 2.1. Kiểm thử Backend (Pytest)
Kích hoạt môi trường ảo Python và chạy toàn bộ suite kiểm thử:
```bash
cd backend
pytest -v
```
Chạy riêng các module kiểm thử sư phạm mới:
```bash
# Kiểm định Dataset Validator:
pytest tests/test_dataset_validator.py -v

# Kiểm định Evaluation Runner & Manifests:
pytest tests/test_evaluation_runner.py -v

# Kiểm định 11 Chỉ Số Sư Phạm (Tính tay độc lập):
pytest tests/test_tutoring_metrics.py -v

# Kiểm định Nghiên Cứu Triệt Tiêu (Ablation):
pytest tests/test_ablation.py -v
```

### 2.2. Kiểm thử Frontend (Vitest)
Cài đặt dependencies và chạy kiểm thử giao diện:
```bash
cd frontend
npm test -- --run
```

### 2.3. Kiểm định Toàn Vẹn Bộ Dữ Liệu
Kiểm tra tính nhất quán 25 trường, ràng buộc ngữ nghĩa và rò rỉ ranh giới split:
```bash
python scripts/validate_vietcsharptutor.py \
  --data data/vietcsharptutor/vietcsharptutor_600.jsonl \
  --schema data/vietcsharptutor/schema.json \
  --report data/vietcsharptutor/benchmark_report.md
```

### 2.4. Kiểm định Sẵn Sàng Vận Hành (Production Readiness)
Kiểm tra 18 luồng người dùng và 7 kiểm tra an ninh hệ thống:
```bash
python scripts/validate_production_readiness.py
```

---

## 3. Phân Định Kiểm Thử Theo 4 Tầng (4 Tiers)

- **`implemented`:** 275 backend tests, 37 frontend tests, validation script, dataset integrity suite.
- **`planned`:** Kiểm thử tải và kiểm thử áp lực (Stress & Load Testing với Locust) cho 500 người dùng đồng thời (v1.2).
- **`experimental`:** Kiểm thử tự động bằng kỹ thuật Fuzzing trên các biến thể cú pháp C# bất thường (C# Roslyn Fuzzing).
- **`future work`:** Kiểm định E2E phân tán đa trình duyệt (Playwright Multi-browser Cloud Farm) tích hợp CI/CD tự động (v2.0).
