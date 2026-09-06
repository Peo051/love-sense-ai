-- Migration: Create skills taxonomy table and seed C# OOP beginner skills (V1)
-- Created: 2026-09-06
-- Target: PostgreSQL 14+ / Supabase

-- 1. Table: skills
CREATE TABLE IF NOT EXISTS skills (
    code VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    prerequisites JSONB NOT NULL DEFAULT '[]'::jsonb,
    difficulty INT NOT NULL CHECK (difficulty >= 1 AND difficulty <= 5),
    taxonomy_version VARCHAR(20) NOT NULL DEFAULT 'v1',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_skills_taxonomy_version ON skills(taxonomy_version);
CREATE INDEX IF NOT EXISTS idx_skills_difficulty ON skills(difficulty);

CREATE TRIGGER update_skills_updated_at
    BEFORE UPDATE ON skills
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

COMMENT ON TABLE skills IS 'Versioned skill taxonomy for adaptive programming tutoring';
COMMENT ON COLUMN skills.code IS 'Stable canonical skill code (e.g. csharp.class_object)';
COMMENT ON COLUMN skills.prerequisites IS 'List of canonical prerequisite skill codes in JSONB array';
COMMENT ON COLUMN skills.difficulty IS 'Pedagogical difficulty level from 1 (fundamental) to 5 (advanced)';

-- 2. Seed C# OOP Beginner Skills (v1)
INSERT INTO skills (code, name, description, prerequisites, difficulty, taxonomy_version)
VALUES
    (
        'csharp.class_object',
        'Lớp và Đối tượng',
        'Khái niệm khuôn mẫu (class) và thực thể cụ thể (object) trong lập trình hướng đối tượng C#',
        '[]'::jsonb,
        1,
        'v1'
    ),
    (
        'csharp.field',
        'Biến trường (Field)',
        'Biến thành viên dùng để lưu trữ trạng thái nội bộ của một đối tượng trong lớp',
        '["csharp.class_object"]'::jsonb,
        1,
        'v1'
    ),
    (
        'csharp.method',
        'Phương thức (Method)',
        'Hành vi và thao tác xử lý logic nghiệp vụ gắn với đối tượng hoặc lớp',
        '["csharp.class_object"]'::jsonb,
        1,
        'v1'
    ),
    (
        'csharp.parameter',
        'Tham số phương thức',
        'Dữ liệu đầu vào truyền vào phương thức hoặc hàm khởi tạo constructor',
        '["csharp.method"]'::jsonb,
        1,
        'v1'
    ),
    (
        'csharp.this',
        'Từ khóa this',
        'Con trỏ tham chiếu đến chính thực thể hiện tại của lớp, dùng để phân biệt tham số và trường dữ liệu',
        '["csharp.field", "csharp.parameter"]'::jsonb,
        2,
        'v1'
    ),
    (
        'csharp.constructor',
        'Hàm khởi tạo (Constructor)',
        'Phương thức đặc biệt được gọi khi khởi tạo đối tượng bằng toán tử new để thiết lập giá trị ban đầu',
        '["csharp.class_object", "csharp.field", "csharp.parameter"]'::jsonb,
        2,
        'v1'
    ),
    (
        'csharp.property',
        'Thuộc tính (Property)',
        'Cơ chế đóng gói truy cập và cập nhật trạng thái của đối tượng thông qua get và set',
        '["csharp.field"]'::jsonb,
        2,
        'v1'
    ),
    (
        'csharp.getter',
        'Bộ truy xuất Get',
        'Khối mã trả về giá trị của thuộc tính hoặc đọc từ biến trường nội bộ (backing field)',
        '["csharp.property"]'::jsonb,
        2,
        'v1'
    ),
    (
        'csharp.setter',
        'Bộ thiết lập Set',
        'Khối mã cập nhật giá trị thuộc tính và gán cho trường nội bộ thông qua từ khóa ngầm định value',
        '["csharp.property"]'::jsonb,
        2,
        'v1'
    ),
    (
        'csharp.validation',
        'Kiểm tra hợp lệ dữ liệu',
        'Logic kiểm tra tính hợp lệ của tham số hoặc giá trị mới truyền vào setter trước khi gán dữ liệu',
        '["csharp.setter"]'::jsonb,
        2,
        'v1'
    ),
    (
        'csharp.encapsulation',
        'Tính đóng gói (Encapsulation)',
        'Nguyên lý ẩn giấu chi tiết cài đặt và bảo vệ toàn vẹn dữ liệu bằng access modifiers và properties',
        '["csharp.field", "csharp.property", "csharp.validation"]'::jsonb,
        2,
        'v1'
    ),
    (
        'csharp.instance',
        'Thành viên thực thể (Instance)',
        'Thành viên gắn liền với từng đối tượng cụ thể và có không gian bộ nhớ riêng biệt',
        '["csharp.class_object", "csharp.field"]'::jsonb,
        2,
        'v1'
    ),
    (
        'csharp.static',
        'Thành viên tĩnh (Static)',
        'Thành viên thuộc về cấp độ lớp, được chia sẻ giữa mọi đối tượng và gọi không cần new',
        '["csharp.class_object", "csharp.instance"]'::jsonb,
        3,
        'v1'
    ),
    (
        'csharp.inheritance',
        'Tính kế thừa (Inheritance)',
        'Cơ chế cho phép một lớp con tái sử dụng và mở rộng các thành viên từ lớp cha',
        '["csharp.class_object", "csharp.encapsulation"]'::jsonb,
        3,
        'v1'
    ),
    (
        'csharp.override',
        'Ghi đè phương thức (Override)',
        'Định nghĩa lại hành vi của phương thức kế thừa từ lớp cha bằng từ khóa override và virtual/abstract',
        '["csharp.inheritance", "csharp.method"]'::jsonb,
        3,
        'v1'
    ),
    (
        'csharp.polymorphism',
        'Tính đa hình (Polymorphism)',
        'Khả năng xử lý các đối tượng thuộc các kiểu dữ liệu khác nhau thông qua một giao diện chung duy nhất',
        '["csharp.inheritance", "csharp.override"]'::jsonb,
        4,
        'v1'
    )
ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    prerequisites = EXCLUDED.prerequisites,
    difficulty = EXCLUDED.difficulty,
    taxonomy_version = EXCLUDED.taxonomy_version,
    updated_at = CURRENT_TIMESTAMP;
