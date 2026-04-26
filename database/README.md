# Love Emotion Database

Database schema và migrations cho ứng dụng Love Emotion.

## Công nghệ

- PostgreSQL 14+
- UUID extension
- JSONB support

## Cài đặt

### 1. Cài đặt PostgreSQL

Tải và cài đặt PostgreSQL từ [postgresql.org](https://www.postgresql.org/download/)

### 2. Tạo database

```bash
# Kết nối PostgreSQL
psql -U postgres

# Tạo database
CREATE DATABASE loveemotion;

# Kết nối vào database
\c loveemotion
```

### 3. Chạy schema

```bash
psql -U postgres -d loveemotion -f schema.sql
```

### 4. Chạy migrations (tuần tự)

```bash
psql -U postgres -d loveemotion -f migrations/001_create_users.sql
psql -U postgres -d loveemotion -f migrations/002_create_profiles.sql
psql -U postgres -d loveemotion -f migrations/003_create_partner_profiles.sql
psql -U postgres -d loveemotion -f migrations/004_create_preferences.sql
psql -U postgres -d loveemotion -f migrations/005_create_analysis_sessions.sql
```

### 5. Seed data (optional)

```bash
psql -U postgres -d loveemotion -f seed.sql
```

## Cấu trúc Database

### Tables

#### users
- `id` (UUID) - Primary key
- `email` (VARCHAR) - Unique email
- `hashed_password` (VARCHAR) - Hashed password
- `is_active` (BOOLEAN) - Account status
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### profiles
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `name` (VARCHAR) - User name
- `age` (INTEGER) - User age
- `communication_style` (VARCHAR) - Communication style
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### partner_profiles
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `name` (VARCHAR) - Partner name
- `age` (INTEGER) - Partner age
- `notes` (TEXT) - Additional notes
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### preferences
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users (unique)
- `language` (VARCHAR) - Preferred language
- `notification_enabled` (BOOLEAN) - Notification setting
- `theme` (VARCHAR) - UI theme
- `created_at` (TIMESTAMP)
- `updated_at` (TIMESTAMP)

#### analysis_sessions
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to users
- `message` (TEXT) - Original message
- `emotion` (VARCHAR) - Detected emotion
- `confidence` (DECIMAL) - Confidence score (0-1)
- `suggested_reply` (TEXT) - Suggested reply
- `emotion_scores` (JSONB) - All emotion scores
- `created_at` (TIMESTAMP)

## Queries hữu ích

### Lấy lịch sử phân tích của user

```sql
SELECT * FROM analysis_sessions 
WHERE user_id = 'user-uuid'
ORDER BY created_at DESC
LIMIT 10;
```

### Thống kê cảm xúc

```sql
SELECT emotion, COUNT(*) as count
FROM analysis_sessions
GROUP BY emotion
ORDER BY count DESC;
```

### Lấy profile đầy đủ của user

```sql
SELECT 
    u.email,
    p.name,
    p.age,
    p.communication_style,
    pp.name as partner_name,
    pr.language,
    pr.theme
FROM users u
LEFT JOIN profiles p ON u.id = p.user_id
LEFT JOIN partner_profiles pp ON u.id = pp.user_id
LEFT JOIN preferences pr ON u.id = pr.user_id
WHERE u.id = 'user-uuid';
```

## Backup và Restore

### Backup

```bash
pg_dump -U postgres loveemotion > backup.sql
```

### Restore

```bash
psql -U postgres loveemotion < backup.sql
```

## Migration Management

Migrations được đánh số tuần tự (001, 002, ...) và nên chạy theo thứ tự.

Để tạo migration mới:
1. Tạo file mới với số thứ tự tiếp theo
2. Viết SQL DDL statements
3. Test trên database development
4. Commit vào version control
