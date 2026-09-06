# Tài Liệu API CodeSense AI (API Documentation)

Tài liệu chi tiết các điểm cuối API (Endpoints) của hệ thống **CodeSense AI - Adaptive Programming Tutor**.

- **Giao thức:** HTTPS / RESTful JSON
- **Base URL cục bộ:** `http://localhost:8000/api`
- **Tài liệu tương tác Swagger:** `http://localhost:8000/docs`

---

## 1. Xác Thực & Phân Quyền (Authentication & Authorization)

Hệ thống sử dụng **Firebase ID Token (JWT)** được gửi qua tiêu đề HTTP:
```http
Authorization: Bearer <FIREBASE_ID_TOKEN>
```
- **Khách (Guest):** Có thể sử dụng `/tutor/analyze` ở chế độ dùng thử mà không cần token.
- **Học viên (Authenticated User):** Cần token để truy cập dữ liệu cá nhân hóa (Profile, History, Mastery, Privacy Data).

---

## 2. Danh Mục Các Endpoint Hoạt Động (`implemented`)

### 2.1. Kiểm Tra Sức Khỏe Hệ Thống
#### `GET /health`
Kiểm tra trạng thái sẵn sàng của backend server.
- **Quyền:** Public
- **Response 200 OK:**
```json
{
  "status": "ok",
  "environment": "production",
  "version": "1.0.0",
  "timestamp": "2026-09-06T10:00:00Z"
}
```

---

### 2.2. Nhóm Endpoint Gia Sư Sư Phạm (Tutor Endpoints)

#### `POST /tutor/analyze`
Tiếp nhận bài làm của sinh viên, chẩn đoán lỗi có cấu trúc và trả về Hint 1 (Định hướng).
- **Quyền:** Public (Guest) hoặc Authenticated Student
- **Request Body:**
```json
{
  "problem_statement": "Viết lớp Student có constructor khởi tạo tên và GPA.",
  "student_code": "public class Student { string name; public Student(string name) { name = name; } }",
  "compiler_error": "Assignment made to same variable (CS1717)",
  "save_result_consent": true,
  "save_input_consent": false
}
```
- **Response 200 OK:**
```json
{
  "session_id": "sess_abc123",
  "bug_status": "has_bug",
  "error_category": "logic_error",
  "bug_type": "unassigned_field_shadowing",
  "bug_location": {
    "file": "Program.cs",
    "start_line": 1,
    "end_line": 1,
    "symbol": "name = name"
  },
  "evidence": "name = name;",
  "knowledge_components": ["OOP.Constructors", "OOP.ThisKeyword"],
  "possible_misconception": "Nghĩ rằng viết tên biến trùng nhau sẽ tự động gán vào trường của lớp mà không cần từ khóa this.",
  "current_hint_level": 1,
  "hint": "Hãy xem xét câu lệnh gán bên trong hàm tạo xem nó đang gán giá trị cho trường của lớp hay cho chính tham số.",
  "explanation_vi": "Trong C#, khi tham số và trường trùng tên, cần dùng từ khóa this để định danh trường đối tượng."
}
```

#### `POST /tutor/hint`
Yêu cầu mở tầng gợi ý tiếp theo (Hint 2: Khái niệm hoặc Hint 3: Hành động).
- **Quyền:** Public / Authenticated (theo `session_id`)
- **Request Body:**
```json
{
  "session_id": "sess_abc123",
  "current_hint_level": 1
}
```
- **Response 200 OK:**
```json
{
  "session_id": "sess_abc123",
  "current_hint_level": 2,
  "hint": "Từ khóa 'this' đại diện cho chính thực thể hiện tại. Dùng 'this.name' để phân biệt với tham số cục bộ 'name'.",
  "has_next_hint": true
}
```

#### `POST /tutor/verify`
Học viên nộp mã nguồn đã sửa đổi để đối chiếu kiểm tra xem lỗi ban đầu đã được khắc phục hay chưa.
- **Request Body:**
```json
{
  "session_id": "sess_abc123",
  "revised_code": "public class Student { string name; public Student(string name) { this.name = name; } }"
}
```
- **Response 200 OK:**
```json
{
  "session_id": "sess_abc123",
  "is_fixed": true,
  "feedback_vi": "Tuyệt vời! Bạn đã sử dụng từ khóa 'this' chính xác để khắc phục hiện tượng che khuất biến.",
  "mastery_update": {
    "OOP.Constructors": 0.85,
    "OOP.ThisKeyword": 0.90
  }
}
```

---

### 2.3. Nhóm Endpoint Hồ Sơ & Năng Lực Học Viên (Student Endpoints)

#### `GET /student/profile`
Lấy thông tin năng lực và phong cách học tập của sinh viên hiện tại.
- **Quyền:** Authenticated Student
- **Response 200 OK:**
```json
{
  "user_id": "usr_xyz789",
  "email": "student@university.edu.vn",
  "display_name": "Nguyen Van A",
  "preferred_explanation_style": "socratic_guided",
  "preferred_difficulty": "beginner"
}
```

#### `GET /student/mastery`
Lấy bảng theo dõi mức độ thuần thục của từng Thành phần Kiến thức (KCs).
- **Quyền:** Authenticated Student
- **Response 200 OK:**
```json
{
  "user_id": "usr_xyz789",
  "mastery_scores": {
    "OOP.Classes": 0.92,
    "OOP.Fields": 0.88,
    "OOP.Properties": 0.85,
    "OOP.Constructors": 0.85,
    "OOP.ThisKeyword": 0.90,
    "OOP.Encapsulation": 0.78,
    "OOP.Polymorphism": 0.65
  },
  "overall_progress_percent": 83.3
}
```

#### `GET /student/history`
Lấy danh sách các phiên giải bài tập trước đó của học viên.
- **Quyền:** Authenticated Student
- **Response 200 OK:**
```json
{
  "total": 12,
  "sessions": [
    {
      "session_id": "sess_abc123",
      "problem_title": "Hồ sơ sinh viên",
      "topic": "constructor_this",
      "bug_status": "has_bug",
      "is_resolved": true,
      "created_at": "2026-09-06T09:30:00Z"
    }
  ]
}
```

#### `DELETE /student/data`
Xóa toàn bộ hồ sơ, lịch sử và điểm thuần thục của tài khoản hiện tại (Right to Erasure / GDPR).
- **Quyền:** Authenticated Student
- **Response 200 OK:**
```json
{
  "status": "success",
  "message": "Toàn bộ dữ liệu cá nhân của người dùng đã được xóa sạch hoàn toàn khỏi hệ thống."
}
```

---

### 2.4. Nhóm Endpoint OCR Mã Nguồn (OCR Endpoints)

#### `POST /ocr/extract`
Trích xuất chữ từ ảnh chụp màn hình mã nguồn bằng công cụ OCR cục bộ.
- **Quyền:** Public / Authenticated
- **Response 200 OK:**
```json
{
  "extracted_code": "public class Car {\n    public string Model;\n}",
  "confidence": 0.94
}
```

#### `POST /ocr/vision`
Trích xuất mã nguồn qua mô hình thị giác AI (AI Vision), chỉ thực thi khi có cờ consent.
- **Quyền:** Authenticated Student kèm `consent=true`.
- **Response 200 OK:**
```json
{
  "extracted_code": "using System;\nclass Program { ... }",
  "provider": "gemini-vision",
  "consent_verified": true
}
```

---

## 3. Bảng Phân Cấp Tính Năng (Feature Classification Matrix)

- **`implemented`:** 18 endpoints trên đã được kiểm thử 100% qua pytest và production readiness validator.
- **`planned`:** Endpoint quản lý bài tập theo chuyên đề `/api/exercises/adaptive` (v1.2).
- **`experimental`:** Endpoint đo lường tải nhận thức qua chuỗi thời gian nộp bài `/api/analytics/cognitive-load`.
- **`future work`:** Endpoint tổng hợp số liệu lớp học dành cho giảng viên `/api/instructor/classroom-summary` (v2.0).
