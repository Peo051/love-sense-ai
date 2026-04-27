# Love Sense AI Documentation

This folder keeps the long-form project documents used for setup, demo, deployment, privacy review, and API reference.

## Start Here

| Document | Purpose |
| --- | --- |
| [SETUP.md](../SETUP.md) | Local setup, environment variables, and development commands. |
| [AUTH_FIREBASE.md](AUTH_FIREBASE.md) | Firebase Google Login architecture, token flow, and common auth errors. |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | Backend API routes, request/response shapes, auth requirements. |
| [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | Three-minute demo script for login, OCR review, analyze, history, and delete data. |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Vercel, Render, PostgreSQL/Supabase, Firebase, and LLM deployment checklist. |
| [PRIVACY_DESIGN.md](PRIVACY_DESIGN.md) | Consent rules, data deletion, logging safety, and privacy-first behavior. |

## Quality and AI Notes

| Document | Purpose |
| --- | --- |
| [ANALYSIS_QUALITY_BENCHMARK.md](ANALYSIS_QUALITY_BENCHMARK.md) | Synthetic benchmark cases for regression checks, not ground truth. |
| [OCR_AND_VISION_PLAN.md](OCR_AND_VISION_PLAN.md) | Local OCR, consented AI Vision OCR, and future vision-processing rules. |
| [TESTING.md](TESTING.md) | Test commands and verification scope. |
| [ROADMAP.md](ROADMAP.md) | Planned improvements after the current demo version. |
| [PROJECT_GUIDE.md](PROJECT_GUIDE.md) | High-level architecture and project rules. |

## Historical Notes

| Document | Purpose |
| --- | --- |
| [E2E_ANALYZE_LLM_FLOW.md](E2E_ANALYZE_LLM_FLOW.md) | Historical E2E analyze and LLM flow notes. |
| [E2E_FLOW_REPORT.md](E2E_FLOW_REPORT.md) | Historical E2E completion report. |

## Important Privacy Reminder

Love Sense AI does not automatically access messages or device notifications. Users manually enter text or upload their own screenshot, review extracted text, and choose whether data is saved. Analysis results are only a communication aid and must not be treated as a certain conclusion about another person.
