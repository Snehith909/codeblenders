# ARCHITECTURE.md — Claim What's Yours

Last updated: 2026-11-21
Source of truth for structure. If code and this file disagree, fix one of them and log it in the changelog.

---

## 1. Principles

1. **Rules are data.** Scheme rules live in JSON, never in code.
2. **LLM extracts, engine decides.** The LLM turns text into a profile. Eligibility is deterministic Python.
3. **Explain everything.** Every result carries the rules that produced it.
4. **No sensitive data.** No Aadhaar or IDs are collected, stored or logged.
5. **Thin slices.** Each module is small, testable on its own, and replaceable.

## 2. System overview

```
+-----------------------------+
|  Frontend (React, mobile)   |
|  Describe | Questions |     |
|  Results | Scheme | Tracker |
|  Admin                      |
+--------------+--------------+
               | HTTPS / JSON
               v
+-----------------------------+
|  Backend (FastAPI)          |
|                             |
|  /api/extract ---> Extractor ---> Claude API
|  /api/match   ---> Rules Engine <--- schemes.json
|  /api/schemes ---> Scheme Store (read/write JSON)
|  /api/applications ---> Tracker ---> SQLite
|  /api/reminders    ---> Reminders ---> SQLite
+-----------------------------+
```

## 3. Components

| Component | Responsibility | Depends on |
|---|---|---|
| Frontend | UI, voice input (Web Speech API), local session | Backend API |
| Extractor | Text to Profile JSON, schema validation, retry once, fallback | Claude API |
| Rules Engine | Evaluate profile against scheme rules, return reasoned results | Scheme Store |
| Scheme Store | Load, validate, update `data/schemes.json` | File system |
| Tracker | Save applications and status changes | SQLite |
| Reminders | Compute upcoming deadlines and tracker reminders | SQLite, Scheme Store |
| Admin API | Edit schemes and rules with validation | Scheme Store |

## 4. Data flow: main journey

1. User types or speaks a description on **Describe**.
2. Frontend calls `POST /api/extract` with `{text}`.
3. Extractor calls the Claude API, validates the JSON, returns `{profile, missing_fields}`.
4. Frontend shows the profile for quick edit and asks only the needed follow-up questions.
5. Frontend calls `POST /api/match` with the final profile.
6. Rules Engine loads schemes, evaluates each, returns results sorted by status.
7. User opens a scheme to see documents, apply steps, source link and verified date.
8. User saves it to the tracker (`POST /api/applications`); reminders are generated from the deadline.

## 5. Eligibility engine

```
evaluate(profile, scheme):
  for rule in scheme.rules:
      value = profile[rule.field]
      if value is None:        -> unknown
      elif apply(op, value):   -> matched
      else:                    -> failed
  if any failed:               status = not_eligible
  elif any unknown:            status = maybe
  else:                        status = likely_eligible
  return {scheme_id, status, matched, failed, unknown}
```

Operators: `eq neq gt gte lt lte in not_in exists`.
No network calls, no LLM, no randomness, so results are repeatable.

## 6. Data stores

| Data | Store | Notes |
|---|---|---|
| Schemes and rules | `data/schemes.json` | Validated by `data/schema.json`; edited via Admin |
| Applications, reminders | SQLite (`app.db`) | Sample data only |
| Profile | Browser session only | Not persisted on the server in v1 |

### SQLite tables

```
applications(id TEXT PK, scheme_id TEXT, status TEXT, next_action TEXT,
             reminder_date TEXT, notes TEXT, created_at TEXT, updated_at TEXT)
```

## 7. API contract (summary)

| Method | Path | Request | Response |
|---|---|---|---|
| POST | `/api/extract` | `{text}` | `{profile, missing_fields}` or `{error, fallback}` |
| POST | `/api/match` | `{profile}` | `{results:[{scheme_id, status, matched[], failed[], unknown[]}]}` |
| GET | `/api/schemes` | | `[scheme]` |
| GET | `/api/schemes/{id}` | | `scheme` |
| PUT | `/api/schemes/{id}` | `scheme` | `scheme` (validated) |
| GET | `/api/applications` | | `[application]` |
| POST | `/api/applications` | `{scheme_id}` | `application` |
| PATCH | `/api/applications/{id}` | `{status, notes?, reminder_date?}` | `application` |
| GET | `/api/reminders` | | `[{scheme_id, date, message}]` |

Errors use `{error: "<code>", message: "<plain English>"}` with proper HTTP status.

## 8. Folder structure

```
claim-whats-yours/
├── CONTEXT.md
├── PRD.md
├── ARCHITECTURE.md
├── DESIGN.md
├── PROMPT.md
├── data/
│   ├── schemes.json
│   └── schema.json
├── backend/
│   ├── main.py          # FastAPI app and routes
│   ├── engine.py        # rules engine
│   ├── extract.py       # LLM extraction
│   ├── store.py         # scheme store
│   ├── tracker.py       # applications and reminders (SQLite)
│   └── tests/
│       ├── test_engine.py
│       ├── test_extract.py
│       └── test_store.py
└── frontend/
    └── src/
        ├── pages/       # Describe, Questions, Results, Scheme, Tracker, Admin
        ├── components/  # SchemeCard, WhyList, Checklist, StatusBadge
        └── api.js
```

## 9. Security and privacy

- No Aadhaar, bank or ID fields exist in any schema; extractor prompt forbids them and output is filtered
- Do not log raw user text or profiles
- Claude API key in environment variable, never in the repo or frontend
- Admin routes protected by a simple shared admin key for the demo
- CORS limited to the frontend origin
- Sample data only; no real addresses or personal details

## 10. Error handling and fallbacks

| Failure | Behaviour |
|---|---|
| LLM returns invalid JSON | Retry once, then show the manual quick-form |
| LLM or network down | Manual quick-form; matching still works (no LLM needed) |
| Scheme file invalid after admin edit | Reject save, show validation errors, keep the old file |
| Unknown rule operator | Fail loudly in tests; at runtime mark the rule unknown and log it |

## 11. Testing strategy

- **Engine:** unit tests for each operator and profiles T1-T5 (CONTEXT.md section 12)
- **Extractor:** mocked LLM tests, including a no-ID-leak test
- **Store:** schema validation test for every scheme
- **API:** one happy-path test per endpoint
- **UI:** manual checklist at 360px width using the demo script

## 12. Deployment (demo)

- Frontend: Vercel or Netlify
- Backend: Render or Railway (or local for the demo)
- Env vars: `ANTHROPIC_API_KEY`, `ADMIN_KEY`, `ALLOWED_ORIGIN`

## 13. Decisions log

| Decision | Reason |
|---|---|
| JSON file for schemes, not a DB | Fastest to edit and demo; DB can replace it later |
| LLM only for extraction | Keeps eligibility explainable and repeatable |
| No login in v1 | Saves time and avoids storing personal data |
| SQLite for tracker | Zero setup, enough for a demo |

## 14. Changelog

- 2026-11-21: Initial architecture.
