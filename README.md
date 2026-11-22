# Claim What's Yours

Describe your situation in plain words. Find the government schemes you are **likely eligible** for, see **why**, know which **documents** to bring, and follow the **steps to apply**.

Built for the Codebenders ACE Builders Hackathon 2026, Problem Statement 5 (Citizens and Public Services).

> This is a guide, not a decision. Always confirm on the official website or at your service centre.

---

## The problem

Many Indian families never claim schemes they qualify for. Rules are hard to read, information is scattered, and middlemen charge for help that should be free.

## Who it is for

Small and marginal farmers in Karnataka (one group, one state, to keep the scope sharp).

## What it does

- Takes plain-language input (typed, voice as a stretch goal) instead of a long form
- Matches the person against stored scheme rules
- Shows **which rule** caused each match, so results are explainable
- Gives a personalised **document checklist** and **step-by-step apply guide**
- Tracks applications and sends **deadline reminders**
- Links every scheme to its **official source** with a "last verified" date
- Lets an admin edit scheme rules as data, with no code change

## How it works

1. The user types: "I am a farmer in Mandya with 2 acres. I am 35."
2. The LLM turns the text into a structured profile (extraction only).
3. A deterministic rules engine checks the profile against each scheme.
4. Results show as **Likely eligible**, **Maybe**, or **Not a match**, each with the matched, failed and unknown rules.

**Key principle:** the LLM extracts, the rules engine decides. Results are repeatable and explainable.

## Guardrails

- Says "likely eligible", never "guaranteed"
- Does not collect Aadhaar numbers or any sensitive ID details
- Uses only public scheme information
- Scheme rules are editable data, not hardcoded
- Sample or synthetic profiles only

## Tech stack

| Layer | Choice |
|---|---|
| Frontend | React (Vite), Tailwind, mobile-first |
| Backend | FastAPI (Python) |
| Data | `data/schemes.json`, SQLite for the tracker |
| LLM | Claude API (profile extraction only) |
| Rules engine | Plain Python |

## Project structure

```
claim-whats-yours/
├── README.md
├── CONTEXT.md        # living project context (read first)
├── PRD.md            # product requirements
├── ARCHITECTURE.md   # system design
├── DESIGN.md         # UI and UX rules
├── PROMPT.md         # AI build prompts
├── data/
│   ├── schemes.json
│   └── schema.json
├── backend/
│   ├── main.py
│   ├── engine.py
│   ├── extract.py
│   ├── store.py
│   ├── tracker.py
│   └── tests/
└── frontend/
    └── src/
```

## Getting started

> The code is built slice by slice. Folders above fill up as each slice is completed.

### Prerequisites

- Python 3.10+
- Node.js 18+
- An Anthropic API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```
ANTHROPIC_API_KEY=your_key_here
ADMIN_KEY=choose_a_demo_key
ALLOWED_ORIGIN=http://localhost:5173
```

Run it:

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### Run tests

```bash
cd backend
pytest
```

## Build with AI (our workflow)

We follow the hackathon guidelines:

- **Context over prompts:** load `CONTEXT.md`, `PRD.md`, `ARCHITECTURE.md` and `DESIGN.md` into every AI session
- **Slice thin:** one small feature at a time
- **Define, Plan, Prove:** write the spec, approve the plan, then test
- **Be specific:** exact inputs, outputs and files
- **Replan after two failures:** stop, fix the spec, then retry

Ready-made prompts are in `PROMPT.md`.

## Build order

- [ ] 1. Scheme data (10-15 schemes)
- [ ] 2. Rules engine and tests
- [ ] 3. Text-to-profile extraction
- [ ] 4. Results page with "Why?" view
- [ ] 5. Documents checklist and apply steps
- [ ] 6. Tracker and reminders
- [ ] 7. Admin edit screen
- [ ] 8. Kannada and voice input (stretch)
- [ ] 9. Polish, demo script and pitch

## Demo script (3 minutes)

1. Type a one-sentence description
2. App extracts the profile and asks one missing question
3. Results show schemes with "Likely eligible" badges
4. Open "Why?" to see the exact rules matched
5. Open a scheme for documents, steps, official link and verified date
6. Add to tracker and set a reminder
7. In Admin, edit a rule and watch the result change live

## Business case

| Payer | Why |
|---|---|
| NGOs and CSR funds | Impact reports on benefits unlocked |
| Banks | Rural customer service and engagement |
| Service centres | Better-prepared applicants, fewer rejections |
| State government | Higher scheme uptake, less reliance on middlemen |

## Data notice

Scheme data in this repo is sample data for the hackathon. Verify every scheme at its official source before relying on it.

## Team

- Snehith, Final-year AI/ML Engineering, VCET

## License

Hackathon project. Add a license before open-sourcing.
