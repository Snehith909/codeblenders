# PROMPT.md — AI build prompts for PS5 (Claim What's Yours)

Built on the hackathon guidelines: Context over prompts, Slice thin, Define-Plan-Prove, Be specific, Replan after two failures.

Before every session, load these files into the AI: `CONTEXT.md`, `PRD.md`, `ARCHITECTURE.md`, `DESIGN.md`.

---

## A. Kickoff prompt (use once, at the start)

```
You are my pair-programmer for a hackathon project: "Claim What's Yours" (Problem Statement 5).

CONTEXT
Read CONTEXT.md, PRD.md, ARCHITECTURE.md and DESIGN.md in full. They are the source of truth.
If anything I ask conflicts with them, tell me before doing it.

WORKING RULES
1. Plan first. Before writing any code, give me a short plan (files to create or change, steps, risks). Wait for my approval.
2. One slice at a time. Do only the slice I name. Do not touch unrelated files.
3. Prove it. For each slice, list success criteria and write tests first. Run them and report pass/fail.
4. Never hardcode scheme rules in code. Rules live in data/schemes.json.
5. The LLM only extracts a profile from text. Eligibility is decided by the deterministic rules engine.
6. Use "likely eligible" wording only. Never collect Aadhaar or sensitive IDs.
7. If a fix fails twice, stop. Do not retry the same fix. Tell me what you think is wrong with the spec and propose an update to CONTEXT.md.
8. Keep explanations short and in simple English.

Confirm you have read all four files by summarising the project in 5 bullets. Then wait for my first slice.
```

---

## B. Slice prompt template (reuse for every slice)

```
SLICE: <name>

DEFINE
- User: small farmer in Karnataka
- Goal of this slice: <one sentence>
- Inputs: <data or function inputs>
- Outputs: <data or function outputs>
- Files allowed to change: <list>

PLAN
Give me a plan first. Do not write code until I say "approved".

PROVE
Success criteria:
- <criterion 1>
- <criterion 2>
Tests to write first:
- <test 1: input -> expected output>
- <test 2: input -> expected output>

CONSTRAINTS
- Follow CONTEXT.md sections 3 (guardrails) and 15 (AI rules)
- No new dependencies without asking
```

---

## C. Ready-to-use slice prompts

### Slice 1: Scheme data

```
SLICE: Scheme data file

DEFINE
- Goal: create data/schemes.json with 10 schemes for small and marginal farmers in Karnataka (central and state).
- Each scheme follows the schema in CONTEXT.md section 6.2: id, name, level, state, summary, benefit, rules[], documents[], apply_steps[], deadline, source_url, last_verified.
- Files allowed to change: data/schemes.json, data/schema.json (JSON schema for validation)

PLAN
Propose the list of 10 schemes first with their official source URLs. Wait for my approval.
If you are not sure about a rule or amount, mark it "needs_verification": true instead of guessing.

PROVE
- A validation script checks every scheme against data/schema.json and exits non-zero on errors
- Every scheme has at least 2 rules, 1 document, 2 apply steps, a source_url and last_verified
- Test: schemes.json loads and validates with 0 errors
```

### Slice 2: Rules engine

```
SLICE: Rules engine

DEFINE
- Goal: write evaluate(profile, scheme) in backend/engine.py.
- Input: Profile dict (CONTEXT.md 6.1) and one Scheme dict.
- Output: {scheme_id, status, matched_rules[], failed_rules[], unknown_rules[]}.
  status is one of likely_eligible | maybe | not_eligible, per CONTEXT.md section 7.
  Each rule entry includes id, field, and reason text.
- Also write match_all(profile, schemes) that returns results sorted: likely_eligible, maybe, not_eligible.
- Operators: eq, neq, gt, gte, lt, lte, in, not_in, exists.
- Files allowed to change: backend/engine.py, backend/tests/test_engine.py

PLAN
Give a plan first. Wait for "approved".

PROVE
Write tests first for T1-T5 in CONTEXT.md section 12:
- T1 -> PM-KISAN likely_eligible
- T2 -> not_eligible with the tax payer rule listed as failed
- T3 -> maybe with land_acres listed as unknown
- T4 -> not_eligible with the land rule failed
- T5 (all null) -> every scheme is maybe or not_eligible, never likely_eligible
Also test: an unknown operator raises a clear error.

CONSTRAINTS
- No LLM calls in this file
- No scheme-specific logic in code
```

### Slice 3: Profile extraction

```
SLICE: Text to profile extraction

DEFINE
- Goal: POST /api/extract takes {text} and returns a Profile JSON.
- Use the Claude API with a system prompt that: returns JSON only, returns null for anything not stated, never guesses income, land or category, never outputs ID numbers.
- Validate output against the Profile schema. If invalid, retry once, then return {error: "extraction_failed", fallback: "manual_form"}.
- Files allowed to change: backend/extract.py, backend/main.py, backend/tests/test_extract.py

PLAN
Give a plan first. Wait for "approved".

PROVE
Tests (mock the LLM call):
- "I am a farmer in Mandya with 2 acres, age 35" -> age 35, occupation farmer, land_acres 2, district Mandya, others null
- "hello" -> all null, missing_fields filled
- Invalid JSON from the LLM twice -> fallback response
- Input containing "my aadhaar is 1234..." -> no ID number appears in the output
```

### Slice 4: Results page with reasoning

```
SLICE: Results page

DEFINE
- Goal: a mobile-first results screen that calls /api/match and shows scheme cards.
- Each card: scheme name, status badge (Likely eligible / Maybe), one-line benefit, and an expandable "Why?" list of matched, failed and unknown rules with reason text.
- Follow DESIGN.md for colours, spacing and components.
- Files allowed to change: frontend/src/pages/Results.jsx, frontend/src/components/SchemeCard.jsx

PLAN
Give a plan first. Wait for "approved".

PROVE
- With the sample response from T1, the page shows PM-KISAN with the "Likely eligible" badge
- Tapping "Why?" shows each matched rule with its reason text
- "Maybe" cards show which information is missing
- The words "guaranteed" or "eligible for sure" appear nowhere
- Works at 360px width with no horizontal scroll
```

---

## D. Fix prompt (when something breaks)

```
The <feature> is failing. 
Expected: <what should happen>
Actual: <what happens, with the error message>
Test that fails: <test name>

Before changing code: explain the likely cause in 3 lines. Then propose the smallest fix.
Do not change files outside <file list>.
```

## E. Replan prompt (after a second failure)

```
This fix has failed twice. Stop changing code.
1. Re-read CONTEXT.md and the slice spec.
2. Tell me which assumption in the spec is probably wrong.
3. Propose an updated spec or CONTEXT.md change.
4. Wait for my approval, then restart this slice from the plan step.
```

## F. Specific vs vague (quick reference)

| Vague | Specific |
|---|---|
| add eligibility check | add `evaluate(profile, scheme)` returning matched, failed and unknown rules with reasons |
| make it look good | use the card component in DESIGN.md with a green "Likely eligible" badge and a "Why?" expander |
| add voice | add a mic button on Describe that uses Web Speech API (lang `kn-IN`) and fills the text box |
| fix the bug | `/api/match` returns 500 when `land_acres` is null; make null yield an unknown rule |
