# Product Rebranding Report: CodeSense AI (APT-002)

Established on: 2026-09-05
Task: APT-002 - Rename product to Adaptive Programming Tutor
Working Product Name: **CodeSense AI**
Research Identity: **Adaptive Programming Tutor for Beginner C# OOP Students**
Baseline Tag: `love-sense-ai-final` (Commit: `f0d6a0306d023cc0f60d41b8075c1926b4490f47`)

---

## 1. Executive Summary

As part of the project pivot from the romantic chat emotion analyzer (*Love Sense AI*) to an educational platform for computer science education (*CodeSense AI*), this task executes a non-destructive product rebranding. 

All user-facing surfaces, service display names, active documentation, and metadata have been transitioned to **CodeSense AI** while preserving the underlying database schema, generic infrastructure, Firebase identity setup, and historical pivot audit trails.

---

## 2. Classification of Domain & Branding Occurrences

A comprehensive repository search was conducted across all files (excluding `.git`, `node_modules`, and generated artifacts) for the five key legacy terms:
- `Love Sense`
- `Love Emotion`
- `relationship`
- `partner`
- `emotion`

Each occurrence has been audited and classified into one of three operational categories:
1. **Branding to replace**: Active product name, titles, logos, navbars, footers, active READMEs, and service display names. (Updated in this task).
2. **Legacy domain to remove later**: Database tables, SQLAlchemy models, Pydantic schemas, and analysis policies specific to relationship/chat sentiment. (Preserved intact for now to ensure continuous deployment and test stability until subsequent pivot tasks).
3. **Historical documentation to preserve**: Benchmark records, initial deployment logs, baseline freeze artifacts, and legacy completion reports.

---

### 2.1 Term: `Love Sense` (37 occurrences across 20 files)

| File Path | Classification | Actions & Rationale |
|---|---|---|
| `frontend/app/layout.tsx` | **1. Branding to replace** | Replaced title & metadata description with CodeSense AI. |
| `frontend/components/common/Navbar.tsx` | **1. Branding to replace** | Replaced logo text with `CodeSense AI` and updated icon to `Code2`. |
| `frontend/components/common/Footer.tsx` | **1. Branding to replace** | Replaced footer brand with `CodeSense AI` and tutor mission statement. |
| `frontend/app/page.tsx` | **1. Branding to replace** | Updated hero title, research identity subtitle, badge, and copy. |
| `frontend/app/login/page.tsx` | **1. Branding to replace** | Updated Card description to reference CodeSense AI Google auth. |
| `frontend/app/auth/page.tsx` | **1. Branding to replace** | Updated account isolation copy to reference CodeSense AI. |
| `frontend/app/analyze/page.tsx` | **1. Branding to replace** | Replaced banner notice to reference CodeSense AI. |
| `frontend/components/auth/AuthRequiredState.tsx` | **1. Branding to replace** | Replaced auth check loading description with CodeSense AI. |
| `frontend/public/logo.svg` | **1. Branding to replace** | Updated SVG `aria-label` to "CodeSense AI logo". |
| `frontend/README.md` | **1. Branding to replace** | Updated title and active introduction to CodeSense AI. |
| `README.md` (root) | **1. Branding to replace** | Updated title and introduction to CodeSense AI with pivot note. |
| `SETUP.md` | **1. Branding to replace** | Updated MVP setup title to CodeSense AI. |
| `DESIGN.md` | **1. Branding to replace** | Updated design guide title and brand definition to CodeSense AI. |
| `docs/README.md` | **1. Branding to replace** | Updated documentation index header to CodeSense AI. |
| `docs/API_DOCUMENTATION.md` | **1. Branding to replace** | Updated `/health` example response to `"service": "CodeSense AI API"`. |
| `docs/DEPLOYMENT.md` | **3. Historical & Active Deploy** | Preserved reference to existing deployed domains (`love-sense-ai.vercel.app`, `love-sense-ai.onrender.com`) to avoid breaking deployment. |
| `docs/pivot/BASELINE.md` | **3. Historical documentation** | Preserved baseline records of the frozen Love Sense AI state. |
| `docs/AUTH_FIREBASE.md` | **3. Historical / Reference** | Preserved architecture notes for Firebase Google auth. |
| `docs/DEMO_SCRIPT.md` | **3. Historical documentation** | Preserved historical demo script of baseline version. |
| `docs/ANALYSIS_QUALITY_BENCHMARK.md` | **3. Historical documentation** | Preserved benchmark cases of initial prototype. |
| `docs/OCR_AND_VISION_PLAN.md` | **3. Historical documentation** | Preserved OCR design document. |
| `docs/PRIVACY_DESIGN.md` | **3. Historical documentation** | Preserved privacy design notes. |

---

### 2.2 Term: `Love Emotion` (22 occurrences across 17 files)

| File Path | Classification | Actions & Rationale |
|---|---|---|
| `backend/app/main.py` | **1. Branding to replace** | FastAPI `title`, `description`, root message, and root health check service name updated to `CodeSense AI API`. |
| `backend/app/routes/health.py` | **1. Branding to replace** | Updated `/api/health` response service name to `CodeSense AI API`. |
| `backend/app/core/config.py` | **1. Branding to replace** | Updated `project_name` to `CodeSense AI API`. Preserved `DEFAULT_DATABASE_URL` filename (`love_emotion_dev.db`) to avoid breaking local SQLite setups. |
| `backend/README.md` | **1. Branding to replace** | Updated title and introduction to CodeSense AI Backend. |
| `backend/.env.example` | **1. Branding to replace** | Updated header comment to CodeSense AI Backend. |
| `frontend/.env.example` | **1. Branding to replace** | Updated header comment to CodeSense AI Frontend. |
| `frontend/package.json` | **1. Branding to replace** | Updated `"name"` property to `"codesense-ai-frontend"`. |
| `backend/app/core/exceptions.py` | **2. Legacy domain to remove later** | `LoveEmotionException` base class preserved to maintain backwards compatibility with existing exception handling. |
| `database/schema.sql` & `seed.sql` | **2. Legacy domain to remove later** | Schema header comments and legacy database names preserved until database migration task. |
| `database/README.md` | **3. Historical documentation** | Preserved documentation for initial SQL schema setup. |
| `docs/PROJECT_GUIDE.md` | **3. Historical documentation** | Preserved project guide for initial architecture. |
| `ai-service/README.md` & `main.py` | **2. Legacy domain to remove later** | Standalone ML package to be refactored or superseded in subsequent tasks. |

---

### 2.3 Term: `relationship` (38 occurrences across 18 files)

| File Path | Classification | Actions & Rationale |
|---|---|---|
| `database/migrations/007_...sql`, `schema.sql`, `seed.sql` | **2. Legacy domain to remove later** | Column `relationship_status` in `profiles` table. Do NOT rename DB tables/columns yet. |
| `backend/app/models/profile.py`, `partner_profile.py`, `analysis_session.py`, `user.py`, `consent.py`, `preference.py` | **2. Legacy domain to remove later** | SQLAlchemy relationships between user and legacy models. Retained intact for test and schema stability. |
| `backend/app/schemas/profile_schema.py` | **2. Legacy domain to remove later** | Pydantic schema field `relationship_status`. |
| `backend/app/services/db_store.py` | **2. Legacy domain to remove later** | Database query helpers handling profile and partner context. |
| `backend/tests/test_profile.py`, `test_auth.py`, `test_profile_history_consent.py` | **2. Legacy domain to remove later** | Test cases asserting profile isolation and relationship fields. |
| `frontend/app/profile/page.tsx`, `page.test.tsx`, `lib/types.ts` | **2. Legacy domain to remove later** | Frontend profile editing form for relationship status. |
| `docs/pivot/BASELINE.md` | **3. Historical documentation** | Preserved baseline audit. |

---

### 2.4 Term: `partner` (117 occurrences across 21 files)

| File Path | Classification | Actions & Rationale |
|---|---|---|
| `database/migrations/003_create_partner_profiles.sql`, `007_...sql`, `schema.sql`, `seed.sql` | **2. Legacy domain to remove later** | `partner_profiles` table definition and seed data. Database tables must not be renamed blindly. |
| `backend/app/models/partner_profile.py`, `__init__.py`, `user.py` | **2. Legacy domain to remove later** | `PartnerProfile` ORM model. Will be replaced by `StudentProfile` / `LearningGoal` in future tasks. |
| `backend/app/schemas/profile_schema.py` | **2. Legacy domain to remove later** | `PartnerProfileSchema` Pydantic models. |
| `backend/app/services/db_store.py` | **2. Legacy domain to remove later** | CRUD operations for partner profiles. |
| `backend/tests/test_profile.py`, `test_auth.py`, `test_profile_history_consent.py` | **2. Legacy domain to remove later** | Tests verifying partner profile lifecycle. |
| `frontend/app/profile/page.tsx`, `page.test.tsx`, `lib/types.ts` | **2. Legacy domain to remove later** | Frontend UI form for partner characteristics. |
| `docs/ROADMAP.md`, `PRIVACY_DESIGN.md`, `PROJECT_GUIDE.md`, `DEPLOYMENT.md` | **3. Historical documentation** | Architecture and privacy guidelines mentioning partner privacy. |
| `docs/pivot/BASELINE.md` | **3. Historical documentation** | Baseline record. |

---

### 2.5 Term: `emotion` (323 occurrences across 64 files)

| File Path | Classification | Actions & Rationale |
|---|---|---|
| `backend/app/routes/analyze.py` | **2. Legacy domain to remove later** | Emotional analysis route. Will be adapted to code tutoring route in future tasks. |
| `backend/app/schemas/analyze_schema.py`, `history_schema.py` | **2. Legacy domain to remove later** | `EmotionDistribution`, `overall_emotion`, `confidence` schemas. |
| `backend/app/services/ai_service.py`, `analysis_policy.py`, `analysis_output_validator.py`, `prompt_builder.py` | **2. Legacy domain to remove later** | Logic for validating emotion distribution and generating relationship advice. |
| `backend/app/models/analysis_session.py` | **2. Legacy domain to remove later** | ORM model storing emotion analysis sessions. |
| `backend/tests/test_analyze*.py`, `test_analysis*.py`, `test_ai_service_llm.py` | **2. Legacy domain to remove later** | Tests validating emotion analysis, benchmarks, and safety checks. |
| `frontend/app/analyze/page.tsx`, `page.test.tsx` | **2. Legacy domain to remove later** | Frontend analysis form and emotion distribution display. |
| `frontend/app/history/page.tsx`, `page.test.tsx` | **2. Legacy domain to remove later** | Session history list displaying emotion tags. |
| `frontend/components/analyze/AnalysisResultPanel.tsx` | **2. Legacy domain to remove later** | Emotion breakdown visualization. |
| `frontend/lib/types.ts` | **2. Legacy domain to remove later** | TypeScript interfaces for `AnalysisResult`, `EmotionDistribution`. |
| `ai-service/` (all files) | **2. Legacy domain to remove later** | Standalone ML model training scripts and emotion dataset configs. |
| `database/migrations/002`, `003`, `005`, `007`, `schema.sql`, `seed.sql` | **2. Legacy domain to remove later** | Database tables with emotion session records. |
| `docs/ANALYSIS_QUALITY_BENCHMARK.md`, `E2E_*.md` | **3. Historical documentation** | Historical test reports and benchmarks. |
| `docs/pivot/BASELINE.md` | **3. Historical documentation** | Baseline record. |
| `README.md`, `DESIGN.md`, `SETUP.md` | **1. Branding to replace** | Intro sections updated to CodeSense AI; legacy references scoped with transition notes. |

---

## 3. Summary of Applied Modifications

### 3.1 Frontend Branding Updates
1. **`frontend/app/layout.tsx`**:
   - Title: `CodeSense AI - Adaptive Programming Tutor for Beginner C# OOP Students`
   - Description: Vietnamese description focused on adaptive C# OOP programming tutoring.
2. **`frontend/components/common/Navbar.tsx`**:
   - Header text: `CodeSense AI`
   - Icon: Switched from `HeartHandshake` to `Code2`.
3. **`frontend/components/common/Footer.tsx`**:
   - Title: `CodeSense AI`
   - Subtitle: `Adaptive Programming Tutor for Beginner C# OOP Students...`
4. **`frontend/app/page.tsx`**:
   - Hero Badge: `CodeSense AI • Adaptive Programming Tutor`
   - Headline: `CodeSense AI`
   - Subheading: `Adaptive Programming Tutor for Beginner C# OOP Students`
   - Feature blocks & summary sections updated with tutoring copy.
5. **`frontend/app/login/page.tsx`**:
   - Updated authentication card description to `CodeSense AI`.
6. **`frontend/app/auth/page.tsx`**:
   - Updated user data isolation description to `CodeSense AI`.
7. **`frontend/app/analyze/page.tsx`**:
   - Updated header banner copy to `CodeSense AI`.
8. **`frontend/components/auth/AuthRequiredState.tsx`**:
   - Updated loading state description to `CodeSense AI`.
9. **`frontend/public/logo.svg`**:
   - Updated `aria-label` to `CodeSense AI logo`.
10. **`frontend/package.json`**:
    - Updated name to `codesense-ai-frontend`.

### 3.2 Backend Service Display Updates
1. **`backend/app/main.py`**:
   - FastAPI title: `CodeSense AI API`
   - FastAPI description: `API hệ thống gia sư lập trình thích ứng (Adaptive Programming Tutor for Beginner C# OOP Students)`
   - `GET /`: `{"message": "CodeSense AI API"}`
   - `GET /health`: `{"status": "healthy", "service": "CodeSense AI API"}`
2. **`backend/app/routes/health.py`**:
   - `GET /api/health`: `{"status": "healthy", "service": "CodeSense AI API"}`
3. **`backend/app/core/config.py`**:
   - `project_name`: `CodeSense AI API`
4. **`backend/README.md`**:
   - Title & header: `CodeSense AI Backend` (Adaptive Programming Tutor for Beginner C# OOP Students).
5. **`backend/.env.example` & `frontend/.env.example`**:
   - Cosmetic comment headers updated to CodeSense AI.

### 3.3 Active Documentation Updates
1. **`README.md` (root)**:
   - Header: `# CodeSense AI`
   - Research Identity: `Adaptive Programming Tutor for Beginner C# OOP Students`
   - Added pivot note directing readers to `love-sense-ai-final` git tag and `docs/pivot/BASELINE.md`.
2. **`SETUP.md`**:
   - Header: `# CodeSense AI - Setup MVP`
3. **`DESIGN.md`**:
   - Header: `# CodeSense AI Frontend Design Guide`
   - App Name: `CodeSense AI (Research: Adaptive Programming Tutor for Beginner C# OOP Students)`
4. **`docs/README.md`**:
   - Header: `# CodeSense AI Documentation`
5. **`docs/API_DOCUMENTATION.md`**:
   - Updated `/health` response example to `"service": "CodeSense AI API"`.

---

## 4. Verification & Quality Assurance

All test suites and build pipelines were executed following the rebranding changes:

| Verification Suite | Target | Status | Notes |
|---|---|---|---|
| **Backend Pytest** | `backend/tests/` | **94 / 94 Passed** (100%) | Duration: ~49.31s. Zero regressions. |
| **TypeScript Typecheck** | `frontend/` (`tsc --noEmit`) | **Passed (Exit code 0)** | Zero type errors. |
| **Frontend Vitest** | `frontend/` (`vitest run`) | **27 / 27 Passed** (100%) | 6 test suites passed cleanly. |
| **Production Build** | `frontend/` (`next build`) | **Build Succeeded** | 9 static routes prerendered with Turbopack. |

---

## 5. Non-Goals Respected

- **No database table renaming**: Tables `users`, `profiles`, `partner_profiles`, `preferences`, `consents`, and `analysis_sessions` remain unaltered.
- **Firebase identity maintained**: Firebase auth client and admin verification logic remain intact; no credentials or providers were changed.
- **Deployment stability preserved**: Existing production domain links (`love-sense-ai.vercel.app`, `love-sense-ai.onrender.com`) remain active in configs and docs to avoid breaking active deployments.
- **No infrastructure renaming**: Reusable modules (`auth.py`, `connection.py`, `llm_client.py`, `rate_limiter.py`, `ocr.ts`, `api.ts`) preserved without unnecessary renaming.
- **Traceability guaranteed**: The original baseline remains tagged at `love-sense-ai-final` and documented in `docs/pivot/BASELINE.md`.
