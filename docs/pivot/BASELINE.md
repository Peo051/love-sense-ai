# Love Sense AI - Baseline Report (APT-001)

Established on: 2026-09-05
Baseline Git Tag: `love-sense-ai-final`
Task: APT-001 - Freeze Love Sense AI baseline

---

## 1. Project Commit & Git State

- **Branch**: `codex/fix-firebase-uid-production-schema`
- **Commit Hash**: `f0d6a0306d023cc0f60d41b8075c1926b4490f47`
- **Git Tag**: `love-sense-ai-final` (tagged at `f0d6a0306d023cc0f60d41b8075c1926b4490f47`)
- **Working Tree Status**:
  - Tracked files are 100% clean (no unstaged or staged modifications).
  - One untracked user file `repomix-output.md` (576 KB repository dump) is preserved intact without modification or deletion.
- **Secret Scanning**:
  - Scanned all tracked files in git for private keys, Firebase credentials, OpenAI/LLM API keys, and PostgreSQL connection URIs.
  - Zero exposed production credentials detected. Only public placeholders, mock configurations, and documentation templates exist.

---

## 2. Current Architecture

### 2.1 Monorepo Structure

```text
love-sense-ai/
├── backend/          # FastAPI REST API (Python 3.13)
│   ├── app/          # Core application (core, database, deps, models, routes, schemas, services)
│   ├── tests/        # Pytest test suite (94 tests)
│   └── requirements.txt
├── frontend/         # Next.js 16.2.4 (App Router, Turbopack, React 18, Tailwind CSS)
│   ├── app/          # App router pages (/, /analyze, /auth, /history, /login, /privacy, /profile)
│   ├── components/   # UI components (common, analyze, auth, home)
│   ├── contexts/     # React AuthContext (Firebase Client)
│   ├── lib/          # API client, OCR helpers, UI utilities
│   └── package.json
├── database/         # Database migrations and schema definitions
│   ├── migrations/   # Raw SQL migrations (001 to 009)
│   ├── schema.sql    # Full consolidated PostgreSQL schema
│   └── seed.sql      # Seed data
├── ai-service/       # Standalone experimental ML module (sentiment/emotion training)
├── data/             # Benchmark evaluation datasets
└── docs/             # Technical specifications, API docs, deployment guides
```

### 2.2 Production & Deployment Configuration

- **Frontend**:
  - Hosting: Vercel (`https://love-sense-ai.vercel.app`)
  - Build command: `npm run build` (Next.js 16 with Turbopack)
  - Key environment variables: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_FIREBASE_*`
- **Backend**:
  - Hosting: Render / Railway (`https://love-sense-ai.onrender.com`)
  - Run command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  - Python Environment: Python 3.13 / FastAPI / Uvicorn
  - Key environment variables: `APP_ENV=production`, `FRONTEND_URL`, `DATABASE_URL`, `SECRET_KEY`, `FIREBASE_SERVICE_ACCOUNT_JSON`, `LLM_*`, `RATE_LIMIT_*`
- **Database**:
  - Engine: PostgreSQL 14+ on Supabase
  - Connection Driver: `asyncpg` via SQLAlchemy async engine; fallback to `aiosqlite` for local dev
- **Authentication**:
  - Frontend: Firebase Web Client Auth (Google Sign-In)
  - Backend: Firebase Admin SDK verifying Bearer ID Tokens and auto-provisioning internal user records mapped by `firebase_uid`. Legacy password auth is preserved for testing/dev.
- **LLM / AI**:
  - OpenAI-compatible chat completion provider (configured for 9Router / OpenRouter)
  - Resilient retry policy (exponential backoff) with automatic fallback to safe mock response generator.

---

## 3. Current APIs

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `GET` | `/` | No | Root status message |
| `GET` | `/health` | No | System health check |
| `GET` | `/api/health` | No | API prefix health check |
| `POST` | `/api/register` | No | Legacy user registration |
| `POST` | `/api/token` | No | Legacy OAuth2 password token login |
| `GET` | `/api/me` | Bearer Token (Firebase or JWT) | Authenticated user profile and UID |
| `POST` | `/api/analyze` | Optional Bearer Token | Emotional analysis of chat text; rate-limited |
| `POST` | `/api/ocr/vision` | Optional (Requires Consent) | OCR text extraction via AI Vision; zero persistence |
| `GET` | `/api/profile` | Yes | Get user profile & partner profile |
| `POST` | `/api/profile` | Yes | Upsert user profile & partner profile |
| `DELETE` | `/api/profile` | Yes | Reset user profile & partner profile |
| `GET` | `/api/history` | Yes | List saved emotion analysis sessions |
| `GET` | `/api/history/{id}` | Yes | Retrieve single session detail |
| `DELETE` | `/api/history/{id}` | Yes | Delete single session |
| `DELETE` | `/api/history` | Yes | Clear all history sessions for user |
| `GET` | `/api/consent` | Yes | Retrieve privacy and storage consent settings |
| `POST` | `/api/consent` | Yes | Update privacy consent settings |
| `DELETE` | `/api/user-data` | Yes | Complete cascade wipe of profile, history, and consents |

---

## 4. Database Tables & Schema

Migrations applied (`database/migrations/`):
- `001_create_users.sql`
- `002_create_profiles.sql`
- `003_create_partner_profiles.sql`
- `004_create_preferences.sql`
- `005_create_analysis_sessions.sql`
- `006_add_consent_and_privacy_controls.sql`
- `007_add_auth_scoped_models.sql`
- `008_harden_user_scoped_persistence.sql`
- `009_add_firebase_uid_to_users.sql`

Table details:
1. `users`:
   - `id` (UUID, PK), `email` (VARCHAR 255, Unique), `firebase_uid` (VARCHAR 128, Unique, Indexed), `hashed_password` (VARCHAR 255), `is_active` (BOOL), `created_at`, `updated_at`.
2. `profiles`:
   - `id` (UUID, PK), `user_id` (UUID FK -> users.id, Cascade, Unique), `nickname`, `primary_language`, `communication_style`, `relationship_status`, timestamps.
3. `partner_profiles`:
   - `id` (UUID, PK), `user_id` (UUID FK -> users.id, Cascade, Unique), `nickname`, `likes`, `dislikes`, `texting_style`, `when_happy`, `when_sad`, `when_angry`, `likes_checkins`, `dislikes_repeated_questions`, `height_cm`, `weight_kg`, `appearance`, `private_notes`, timestamps.
4. `preferences`:
   - `id` (UUID, PK), `user_id` (UUID FK -> users.id, Cascade, Unique), `language`, `notification_enabled`, `theme`, timestamps.
5. `consents`:
   - `id` (UUID, PK), `user_id` (UUID FK -> users.id, Cascade), `history_enabled`, `save_input`, `save_result`, `consent_type`, `is_accepted`, `accepted_at`, timestamps. Unique constraint on `(user_id, consent_type)`.
6. `analysis_sessions`:
   - `id` (UUID, PK), `user_id` (UUID FK -> users.id, Cascade), `analyzed_at`, `overall_emotion`, `confidence`, `emotion_distribution` (JSONB), `summary`, `context_note`, `suggested_reply`, `warning`, `save_input`, `save_result`, `consent_type`, `is_accepted`, `accepted_at`, `chat_text`. Check constraint prevents non-null `chat_text` without explicit consent.

---

## 5. Test & Quality Results

| Suite / Check | Command | Result | Pass/Fail | Duration / Notes |
|---|---|---|---|---|
| **Backend Pytest** | `pytest tests -v` | 94 / 94 passed | **PASS** | 49.25s (SQLite in-memory test isolation) |
| **Frontend Vitest** | `npm run test` | 27 / 27 passed (6 files) | **PASS** | 116.45s (jsdom + React Testing Library) |
| **TypeScript Typecheck** | `npm run typecheck` | 0 errors | **PASS** | `tsc --noEmit` exited cleanly |
| **Frontend Production Build** | `npm run build` | 9 static routes generated | **PASS** | Next.js 16 Turbopack production build succeeded |
| **Linters** | None configured | N/A | N/A | No ESLint, Flake8, or Ruff configured |
| **Secret Scan** | Automated pattern scan | 0 leaked secrets | **PASS** | Verified tracked git index |

---

## 6. Reusable Infrastructure

The following architectural components are general-purpose and directly reusable for the **Adaptive Programming Tutor**:

1. **Authentication & Identity**:
   - `backend/app/core/firebase.py`, `backend/app/core/auth.py`, `backend/app/deps/auth.py`
   - `frontend/contexts/AuthContext.tsx`, `frontend/lib/firebase.ts`, `frontend/lib/auth.ts`, `frontend/components/auth/AuthRequiredState.tsx`
   - Maps Google Firebase tokens to local PostgreSQL database records; handles guest mode and authenticated state cleanly.
2. **Database & Persistence Engine**:
   - `backend/app/database/connection.py`, `backend/app/database/session.py`
   - Dual support for PostgreSQL (`asyncpg`) in production and SQLite (`aiosqlite`) in development with async sessions.
   - User-scoped queries and transactions.
3. **LLM Client Layer**:
   - `backend/app/services/llm_client.py`
   - OpenAI-compatible REST integration with timeout, retry backoff, response validation, and transparent mock mode fallback.
4. **OCR & Vision Service**:
   - `backend/app/services/vision_ocr_service.py`, `backend/app/routes/ocr.py`
   - Client-side Tesseract.js (`frontend/lib/ocr.ts`) + AI Vision model endpoint.
   - Can extract code snippets from IDE screenshots, compiler errors, or whiteboard photos.
5. **Privacy, Consent & Data Governance**:
   - `backend/app/routes/consent.py`, `backend/app/routes/user_data.py`, `backend/app/models/consent.py`
   - Full GDPR-compliant data cascade deletion and opt-in storage consent.
6. **Rate Limiting**:
   - `backend/app/services/rate_limiter.py`
   - Sliding-window rate limiter supporting both IP-based anonymous limits and user-scoped authenticated limits.
7. **Frontend UI System & API Client**:
   - `frontend/components/common/` (Button, Card, Badge, Alert, Modal ConfirmDialog, PageShell)
   - `frontend/lib/api.ts` (Bearer token auto-injection, custom error handling, retry handling).
8. **Deployment Architecture**:
   - Vercel (Frontend) + Render/Railway (Backend) + Supabase (Database).

---

## 7. Deprecated-Domain Modules (Love / Emotion Specific)

The following modules are specific to the romantic/relationship domain and will be phased out or replaced during the pivot:

1. **Database & Schema**:
   - `partner_profiles` table (relationship quirks, texting style, likes/dislikes, physical notes).
   - `analysis_sessions` emotion fields (`overall_emotion`, `emotion_distribution`, `suggested_reply`, `context_note`).
2. **Backend Domain Logic**:
   - `backend/app/models/partner_profile.py`, `backend/app/models/analysis_session.py`
   - `backend/app/routes/analyze.py` (emotion detection endpoint)
   - `backend/app/schemas/analyze_schema.py`
   - `backend/app/services/ai_service.py` (romantic mock generator)
   - `backend/app/services/analysis_output_validator.py` (validating emotion tags and filtering love-specific claims like "hết yêu", "phản bội")
   - `backend/app/services/analysis_policy.py`, `backend/app/services/prompt_builder.py`, `backend/app/services/profile_context.py`
   - `backend/app/services/safety_filter.py` (filters tailored for relationship harassment/abuse)
   - `backend/app/routes/profile.py` (partner profile management)
3. **Frontend Domain Pages & Components**:
   - `frontend/app/analyze/page.tsx` (conversation chat analysis view)
   - `frontend/components/analyze/AnalysisForm.tsx`, `AnalysisResultPanel.tsx`
   - `frontend/app/profile/page.tsx` (partner profile inputs)
   - `frontend/components/home/HeroVisual.tsx` (romantic hero assets)
   - `frontend/lib/types.ts` (romantic emotion interfaces)
4. **Experimental ML Package**:
   - `ai-service/` (Sentiment/emotion predictors, teencode dictionaries, training datasets).
   - `data/evaluation/chat_sentiment_cases.json` (relationship chat evaluation dataset).

---

## 8. Known Issues & Technical Debt

1. **Decoupled `ai-service`**:
   - The `ai-service/` directory contains legacy standalone scikit-learn models and scripts that are not connected to the FastAPI backend (backend uses its own `llm_client.py`).
2. **Vitest Performance on Windows**:
   - Running the frontend Vitest suite with JSDOM on Windows requires ~116s due to thread and DOM overhead.
3. **Manual SQL Migration Tracking**:
   - Migrations are sequential `.sql` files (`database/migrations/001-009`) without an automated migration tool like Alembic.
4. **Absence of Configured Linters**:
   - Neither the backend (flake8/black/ruff) nor the frontend (eslint) has a linter script wired up in their configuration files.

---

## 9. Pivot Assumptions (Adaptive Programming Tutor)

1. **Target Domain**:
   - Repurpose the system into an **Adaptive Programming Tutor** that helps students learn programming concepts, debug code snippets, receive hints without giving away complete solutions, and track exercise progress.
2. **Architecture Preservation**:
   - Maintain the existing Next.js + FastAPI + Supabase + Firebase stack without disruption to the underlying CI/CD and deployment workflows.
3. **LLM Client Adaptation**:
   - Shift prompts from relationship advice to pedagogical coding guidance: Socratic questioning, syntax/logic bug explanations, time/space complexity analysis, and progressive hinting.
4. **Vision/OCR Re-allocation**:
   - Repurpose the OCR pipeline from chat screenshots to code screenshots, terminal error logs, compiler tracebacks, and whiteboard sketches.
5. **Database Model Evolution**:
   - Replace `partner_profiles` with `student_profiles` (learning level, preferred programming languages, goal topics).
   - Replace `analysis_sessions` with `coding_sessions` or `exercise_submissions` (problem ID, student code snippet, programming language, error output, tutor feedback, hints provided).
6. **Privacy & Data Retention**:
   - Retain the consent framework (`consents` and `/api/user-data` cascade delete) to allow students to control whether their submitted code is retained for progress analytics or erased.
