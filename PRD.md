# PRD.md — Claim What's Yours

Product Requirements Document | Hackathon: Codebenders ACE Builders 2026 | Problem Statement 5
Last updated: 2026-11-21

---

## 1. Problem

India has hundreds of central and state schemes (scholarships, pensions, health cover, housing, farm benefits). Many eligible families never claim them because:
- Information is scattered across websites and notices
- Eligibility rules are hard to read
- The document list is unclear
- People depend on middlemen who charge for help that should be free

## 2. Target user

**Primary:** Small and marginal farmers in Karnataka.

**Persona: Ramesh, 35, Mandya**
- Owns 2 acres, farms paddy and sugarcane
- Uses a basic Android phone, comfortable with WhatsApp and voice messages
- Does not know which schemes exist or which details matter
- Currently pays a middleman to fill forms

**Secondary users:** NGO workers and service centre staff who help farmers apply.

## 3. Product goal

A person describes their situation in plain words and in under 2 minutes learns:
1. Which schemes they are likely eligible for, and why
2. Which documents they need
3. Exactly how to apply
4. When deadlines are, with reminders

## 4. Goals and non-goals

### Goals
- Plain-language input instead of a long form
- Explainable eligibility (show the rule behind every result)
- Document checklist and step-by-step apply guide
- Application tracker and deadline reminders
- Rules stored as editable data so the product stays accurate

### Non-goals (v1)
- Submitting applications on the user's behalf
- Collecting Aadhaar or any sensitive ID details
- Guaranteeing eligibility or approval
- Covering all states or all schemes
- User accounts and login (v1 uses a local session)
- Real-time sync with government portals

## 5. User stories

| ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|
| U1 | Farmer | describe myself in a sentence | I do not fill a long form | Must |
| U2 | Farmer | see which schemes fit me | I know what to claim | Must |
| U3 | Farmer | see why a scheme matched | I can trust the result | Must |
| U4 | Farmer | get a document checklist | I arrive at the office prepared | Must |
| U5 | Farmer | see step-by-step apply instructions | I do not need a middleman | Must |
| U6 | Farmer | get reminders before deadlines | nothing lapses | Must |
| U7 | Farmer | track my application status | I know what to do next | Must |
| U8 | Farmer | speak instead of type | typing is hard for me | Should |
| U9 | Farmer | use Kannada | I understand everything | Should |
| U10 | Admin | edit scheme rules in a screen | data stays current when rules change | Must |
| U11 | Farmer | open the official source for every scheme | I can verify it myself | Must |

## 6. Functional requirements

| ID | Requirement | Story |
|---|---|---|
| FR1 | Accept free-text input and convert it to a structured profile | U1 |
| FR2 | Ask follow-up questions only for missing fields that affect at least one scheme | U1 |
| FR3 | Evaluate every scheme against the profile using stored rules | U2 |
| FR4 | Return status per scheme: likely eligible, maybe, not eligible | U2 |
| FR5 | Show matched, failed and unknown rules with plain-language reasons | U3 |
| FR6 | Show a personalised, tick-off document checklist per scheme | U4 |
| FR7 | Show numbered apply steps per scheme | U5 |
| FR8 | Create reminders from scheme deadlines | U6 |
| FR9 | Let the user save a scheme as an application and update its status | U7 |
| FR10 | Support voice input (Web Speech API) | U8 |
| FR11 | Support Kannada text input and UI labels | U9 |
| FR12 | Admin screen to view and edit scheme data and rules | U10 |
| FR13 | Every scheme shows official source link and last-verified date | U11 |

## 7. Non-functional requirements

- **Trust and wording:** only "likely eligible" or "maybe"; never "guaranteed"
- **Privacy:** no Aadhaar, no bank numbers, no real personal data; sample profiles only in the demo
- **Accuracy:** eligibility is deterministic (same profile gives same result); LLM is used only for extraction
- **Performance:** match results in under 2 seconds on a normal connection
- **Usability:** mobile-first, works at 360px, large tap targets, simple language
- **Maintainability:** new scheme added by editing data, no code change

## 8. Success metrics

**Demo and judging**
- Live demo from sentence to results to checklist in under 3 minutes
- Admin edits a rule and the result changes live

**Product (for the pitch)**
- Time to first result: under 2 minutes
- Number of schemes matched per sample profile
- Test profiles T1-T5 produce expected results (100% pass)
- Every scheme has a source link and verified date (100%)

## 9. Business case

| Payer | Why they pay |
|---|---|
| NGOs and CSR funds | Reach and impact reports on benefits unlocked for families |
| Banks | Customer service for rural account holders, goodwill and engagement |
| Local service centres | Faster, better-prepared applicants and fewer rejected forms |
| State government | Higher scheme uptake and less leakage to middlemen |

**Possible model:** per-district licence or impact-report subscription for sponsors, with a free tier for farmers.

## 10. Scope for the hackathon

**In scope:** FR1-FR9, FR12, FR13 and 10-15 schemes for one user group in one state.
**Stretch:** FR10 voice, FR11 Kannada.
**Out of scope:** everything in section 4 non-goals.

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Scheme data is wrong or outdated | Official-source links, last-verified date, "needs_verification" flag, admin edit screen |
| LLM extracts wrong values | Strict JSON schema, nulls when unsure, user can edit the profile before matching |
| User over-trusts results | "Likely eligible" wording and a visible disclaimer to confirm at the official source |
| Too many schemes, too little time | Cap at 10-15 schemes, depth over breadth |
| Voice or Kannada not finished | Marked stretch; core demo works without them |

## 12. Open questions

- Final scheme list (verify each from official sources)
- Include Kannada in the demo or not
- Where to host the demo
