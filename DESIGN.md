# DESIGN.md — Claim What's Yours

Last updated: 2026-11-21
UI and UX source of truth. Mobile-first, built for low digital literacy.

---

## 1. Design principles

1. **Simple words.** Short sentences. No government jargon. Explain any unavoidable term.
2. **One thing per screen.** One question or one decision at a time.
3. **Show the why.** Every result has a visible reason.
4. **Honest tone.** "Likely eligible", never "guaranteed". Always point to the official source.
5. **Big and clear.** Large text, large tap targets, high contrast.
6. **Works on a basic phone.** 360px wide, light on data, no heavy images.

## 2. Voice and wording

| Use | Avoid |
|---|---|
| Likely eligible | Eligible, Approved, Guaranteed |
| Maybe, we need one more detail | Pending, Indeterminate |
| Why this matched | Rule evaluation |
| Documents to bring | Required documentation |
| Check this on the official site | Verified by us |

Disclaimer (shown on Results and Scheme pages):
> "This is a guide, not a decision. Please confirm on the official website or at your service centre."

## 3. Colour

| Token | Hex | Use |
|---|---|---|
| `--green-600` | `#15803D` | Primary buttons, "Likely eligible" |
| `--green-50` | `#F0FDF4` | Likely-eligible card background |
| `--amber-600` | `#B45309` | "Maybe" badge |
| `--amber-50` | `#FFFBEB` | Maybe card background |
| `--red-600` | `#B91C1C` | Failed rule icon, errors |
| `--gray-900` | `#111827` | Main text |
| `--gray-600` | `#4B5563` | Secondary text |
| `--gray-100` | `#F3F4F6` | Page background |
| `--white` | `#FFFFFF` | Cards |

Contrast: all text on its background must meet WCAG AA (4.5:1). Never use colour alone; pair every badge with an icon and a text label.

## 4. Typography

- Font: system sans-serif stack (`Inter`, `Noto Sans`, `Noto Sans Kannada`, system-ui) so Kannada renders without extra downloads
- Base size: 18px; line height 1.5
- Headings: 24px (page), 20px (section), semi-bold
- Minimum text size anywhere: 14px

## 5. Layout and spacing

- Mobile-first; design at 360px, scale up to a centred column (max 640px)
- 8px spacing scale (8, 16, 24, 32)
- Page padding 16px; card padding 16px; card radius 12px
- Tap targets at least 48x48px
- No horizontal scroll at 360px

## 6. Components

**Primary button:** full width, 52px tall, green, white text 18px, radius 12px.
**Secondary button:** same size, white background, green border and text.
**Mic button:** 56px circle beside the text box; pulsing ring while listening.

**Status badge**
- Likely eligible: green background, check icon, label "Likely eligible"
- Maybe: amber background, question icon, label "Maybe"
- Not eligible: gray, hidden from the main list (under "Not a match" at the bottom)

**Scheme card**
```
+--------------------------------------+
| [Likely eligible]                    |
| PM-KISAN                             |
| Income support for small farmers     |
| What you get: <short benefit line>   |
| [ Why this matched  v ]              |
| [ See documents and how to apply ]   |
+--------------------------------------+
```

**"Why?" list:** each row has an icon, a plain sentence, and the field value.
- Green check: "You are a farmer"
- Green check: "You own land (2 acres)"
- Amber question: "We need to know: do you pay income tax?"
- Red cross: "Income tax payers are not covered"

**Checklist item:** large checkbox, document name, optional help text ("Ask the village office for this").

**Step list:** numbered circles with one short sentence each.

**Source footer on every scheme:** "Official source: <link>. Last checked: <date>."

## 7. Screens

### 7.1 Describe (home)
- Heading: "Tell us about yourself"
- Large text box, placeholder: "Example: I am a farmer in Mandya with 2 acres. I am 35."
- Mic button (stretch), sample chips ("Farmer", "Farm worker", "Student")
- Primary button: "Find my schemes"
- Small note: "Please do not enter Aadhaar or bank numbers."

### 7.2 Quick questions
- One question per screen with a progress dots indicator
- Big option buttons (Yes / No / Not sure) or a number input
- "Skip" always available

### 7.3 Results
- Summary line: "We found 4 schemes that may suit you"
- Section "Likely eligible", then "Maybe", then collapsed "Not a match"
- Scheme cards (section 6), disclaimer at the bottom
- "Edit my details" link at the top

### 7.4 Scheme detail
- Name, benefit, status badge
- Tabs or stacked sections: Why this matched, Documents to bring, How to apply, Deadline
- Source footer
- Primary button: "Add to my applications"

### 7.5 My applications
- List with status chip and "Next step" line
- Tap to change status via a simple bottom sheet
- Reminder date shown with a bell icon

### 7.6 Admin (desktop-friendly)
- Table of schemes with last-verified date
- Edit form: fields, rules list (field, operator, value, reason), documents, steps, source URL
- Save validates against the schema and shows errors in plain words
- "Mark as verified today" button

## 8. States

| State | Behaviour |
|---|---|
| Loading | Skeleton cards and the text "Looking for schemes..." |
| Empty results | "No clear match yet. Try adding more details." with an Edit button |
| Extraction failed | "We could not read that. Please answer a few quick questions." and show the quick form |
| Offline | Banner "No internet. Showing saved results." |
| Error | Plain sentence plus Retry button; never show codes |

## 9. Accessibility

- Semantic HTML, labels on all inputs, focus outlines visible
- Screen reader text for badges and icons
- Voice input as an alternative to typing
- Respect reduced-motion setting
- Language toggle (English / Kannada) visible on every screen when Kannada is enabled

## 10. Responsiveness

| Width | Layout |
|---|---|
| 360 to 639px | Single column, bottom primary button |
| 640px and above | Centred column up to 640px; Admin uses a two-column layout |

## 11. Demo polish checklist

- [ ] All screens usable at 360px
- [ ] Sample chips pre-fill the text box
- [ ] "Why?" opens in one tap
- [ ] No placeholder text or lorem ipsum
- [ ] The words "guaranteed" and "eligible for sure" appear nowhere
- [ ] Admin edit changes a result live during the demo

## 12. Changelog

- 2026-11-21: Initial design.
