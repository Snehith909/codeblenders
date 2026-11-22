# CONTEXT.md — Claim What's Yours (PS5)

> Living document. Paste this at the start of every AI session. Update it after every feature.
> Last updated: 2026-11-21

---

## 1. Project in one paragraph

A web app where a person describes their situation in plain language (typed or spoken). The app turns that into a profile, matches it against government schemes stored as editable data, and shows: which schemes they are **likely eligible** for, **which rule** caused each match, which **documents** to bring, **how to apply** step by step, and **deadline reminders** with a simple tracker. Built for the Codebenders ACE Builders Hackathon 2026, Problem Statement 5 (Citizens and Public Services).

## 2. Target user (locked)

- **Group:** Small and marginal farmers
- **State:** Karnataka
- **Language:** English first, Kannada input/output as a stretch goal
- **Typical user:** Low digital literacy, uses a phone, does not know which details matter, may rely on middlemen today

## 3. Hard guardrails (never break)

- Say **"likely eligible"**, never "guaranteed" or "eligible for sure"
- **Never collect** Aadhaar numbers, bank account numbers, or any sensitive ID details
- Use **only public scheme information**; every scheme links to its official source with a "last verified" date
- Scheme rules are **editable data** (JSON/DB), never hardcoded in logic
- Test with **sample profiles only**, no real personal data
- Do not promise approval, payment amounts as certain, or act like a government portal

## 4. Must-have features (from the brief)

1. Plain-language input (typed; voice if time allows), not a long form
2. Eligibility matching that shows its reasoning (which rule matched / failed)
3. Personalised document checklist
4. Step-by-step apply guide
5. Deadline reminders and application tracking
6. Official source link + last-verified date on every scheme

## 5. Tech stack (defaults, change if needed)

| Layer | Choice |
|---|---|
| Frontend | React (Vite) or Next.js, mobile-first, Tailwind |
| Backend | FastAPI (Python) |
| Data | JSON file for schemes (v1), SQLite for tracker and reminders |
| LLM | Claude API for text-to-profile extraction only |
| Rules engine | Plain Python, deterministic, no LLM involved in eligibility |
| Voice (stretch) | Browser Web Speech API |

**Key principle:** The LLM only extracts a profile from text. Eligibility is decided by the rules engine, so results are explainable and repeatable.

## 6. Data model

### 6.1 Profile (output of extraction)

```json
{
  "age": 35,
  "gender": "male",
  "occupation": "farmer",
  "land_acres": 2.0,
  "land_ownership": "owned",
  "annual_income": 90000,
  "category": "general",
  "district": "Mandya",
  "has_bank_account": true,
  "is_income_tax_payer": false,
  "missing_fields": []
}
```

- Unknown values are `null`, and the field name is added to `missing_fields`.
- The app asks follow-up questions only for fields that matter to at least one scheme.

### 6.2 Scheme (editable data)

```json
{
  "id": "pm-kisan",
  "name": "PM-KISAN",
  "level": "central",
  "state": "ALL",
  "category": "farmer",
  "summary": "Income support for small and marginal farmer families.",
  "benefit": "Yearly income support paid in instalments",
  "rules": [
    {
      "id": "r1",
      "field": "occupation",
      "op": "eq",
      "value": "farmer",
      "reason": "Scheme is for farmer families"
    },
    {
      "id": "r2",
      "field": "land_acres",
      "op": "gt",
      "value": 0,
      "reason": "Must own cultivable land"
    },
    {
      "id": "r3",
      "field": "is_income_tax_payer",
      "op": "eq",
      "value": false,
      "reason": "Income tax payers are excluded"
    }
  ],
  "documents": ["Land record (RTC/Pahani)", "Bank passbook copy", "Mobile number"],
  "apply_steps": [
    "Visit the official portal or nearest service centre",
    "Register as a farmer with land details",
    "Submit documents and note the registration number"
  ],
  "deadline": null,
  "source_url": "https://pmkisan.gov.in",
  "last_verified": "2026-11-21"
}
```

> The values above are **sample data**. Verify every scheme against its official source before the demo and update `last_verified`.

### 6.3 Rule operators

`eq`, `neq`, `gt`, `gte`, `lt`, `lte`, `in`, `not_in`, `exists`

### 6.4 Application tracker entry

```json
{
  "id": "uuid",
  "scheme_id": "pm-kisan",
  "status": "documents_ready",
  "next_action": "Visit service centre",
  "reminder_date": "2026-12-05",
  "notes": ""
}
```

Status flow: `not_started` → `documents_ready` → `applied` → `under_review` → `approved` / `rejected`

## 7. Eligibility logic

For each scheme, evaluate every rule against the profile:

- **pass:** rule satisfied
- **fail:** rule not satisfied
- **unknown:** profile field is null

Result per scheme:

| Result | Condition |
|---|---|
| `likely_eligible` | All rules pass |
| `maybe` | No rule fails, but at least one is unknown (show which info is missing) |
| `not_eligible` | At least one rule fails (show the failed rule) |

Each result returns `matched_rules`, `failed_rules`, `unknown_rules`, each with its `reason` text. The UI must always show these.

## 8. LLM extraction contract

- **Input:** free text (for example "I am a farmer in Mandya with 2 acres, my age is 35")
- **Output:** strict JSON matching the Profile schema in 6.1
- **Rules for the prompt:**
  - Return only fields the user actually stated; use `null` otherwise
  - Never guess income, land or category
  - Never ask for or output Aadhaar or ID numbers
  - Return JSON only, no extra text
- Validate the output against the schema before using it. If it fails twice, show the manual form fallback.

## 9. Screens

1. **Home / Describe:** big text box, mic button (stretch), sample prompt chips
2. **Quick questions:** only the missing fields, one at a time
3. **Results:** scheme cards with status badge (likely / maybe), and "Why?" expandable showing matched rules
4. **Scheme detail:** documents checklist (tick-off), apply steps, official link, last verified date
5. **My applications:** tracker list with status and next action
6. **Reminders:** upcoming deadlines
7. **Admin:** list/edit schemes and rules (the "rules as editable data" proof)

## 10. API endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/extract` | text → profile JSON |
| POST | `/api/match` | profile → scheme results with reasons |
| GET | `/api/schemes` | list schemes |
| GET | `/api/schemes/{id}` | scheme detail |
| PUT | `/api/schemes/{id}` | admin edit scheme and rules |
| GET/POST | `/api/applications` | tracker list / create |
| PATCH | `/api/applications/{id}` | update status |
| GET | `/api/reminders` | upcoming reminders |

## 11. Seed scope

- **10 to 15 schemes** only, covering small farmers in Karnataka (central + state)
- Depth over breadth: complete rules, documents, steps, source link, verified date for each
- Fill the scheme list from official sources only, then record it here:

| # | Scheme | Level | Verified |
|---|---|---|---|
| 1 | PM-KISAN | Central | to verify |
| 2 | _add_ | | |

## 12. Test profiles (the "Prove" step)

| # | Profile | Expected |
|---|---|---|
| T1 | 35, farmer, 2 acres owned, not a tax payer | PM-KISAN → likely_eligible |
| T2 | 45, farmer, 3 acres, income tax payer | PM-KISAN → not_eligible (tax payer rule) |
| T3 | 30, farmer, land unknown | PM-KISAN → maybe (land missing) |
| T4 | 28, farm labourer, no land | PM-KISAN → not_eligible (land rule) |
| T5 | Text with no usable info | Extraction returns all nulls, app asks questions |

Add more as schemes are added. Every scheme gets at least one pass test and one fail test.

## 13. Build order (thin slices)

- [ ] 1. Scheme JSON file with 10-15 schemes
- [ ] 2. Rules engine + tests T1-T5
- [ ] 3. `/api/extract` (LLM text → profile)
- [ ] 4. Results page with "Why?" reasoning view
- [ ] 5. Documents checklist + apply steps page
- [ ] 6. Tracker + reminders
- [ ] 7. Admin edit screen
- [ ] 8. Kannada text + voice input (only if time allows)
- [ ] 9. Polish, demo script, pitch PPT

## 14. Business case (for the pitch)

- **Problem cost:** families lose benefits or pay middlemen for free help
- **Who pays:** NGOs and CSR funds (impact reports), banks (customer service), local service centres (faster processing), state government (higher scheme uptake)
- **Why they pay:** measurable reach, fewer rejected applications, verified and current scheme data
- **Impact metrics to show (with assumptions):** schemes matched per user, estimated benefit value unlocked, applications tracked

## 15. Rules for the AI assistant (read before coding)

1. Read this file first. If something conflicts with it, ask before changing it.
2. **Plan first:** propose a short plan and wait for approval before writing code.
3. Build **one slice at a time**; do not touch unrelated files.
4. Never hardcode scheme rules in code. Rules live in data.
5. Keep eligibility deterministic. The LLM never decides eligibility.
6. Never collect Aadhaar or sensitive IDs. Use "likely eligible" wording only.
7. After each feature, run the tests and report pass/fail.
8. **If a fix fails twice, stop.** Review the spec here, update this file, then retry.
9. Be specific in changes, for example: "add a function that takes a Profile and a Scheme and returns matched, failed and unknown rules."

## 16. Demo script (3 minutes)

1. Type: "I am a farmer in Mandya, I have 2 acres, I am 35."
2. App extracts the profile and asks one missing question
3. Results show 3-4 schemes with "likely eligible" badges
4. Open "Why?" to show the exact rules matched
5. Open one scheme: documents checklist and apply steps, official link, last verified date
6. Add to tracker, set a reminder
7. Open admin, edit a scheme rule, re-run, and show the result change instantly

## 17. Open decisions

- [ ] Final scheme list (needs official-source check)
- [ ] Kannada support: yes or no
- [ ] Hosting for demo (Vercel/Render or local)

## 18. Changelog

- 2026-11-21: Initial context created.
