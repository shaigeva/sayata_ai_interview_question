# Interviewer Guide

## 1. Purpose & Rationale

This exercise evaluates how candidates work on real-world backend tasks using
AI tools under time pressure. We're not testing memorized knowledge — we're
observing:

- **Debugging ability** — Can they trace a bug through multiple layers?
- **AI tool usage** — Do they use AI effectively, or just passively watch it?
- **Doc extraction** — Do they find and apply buried business rules?
- **API exploration** — Can they discover unfamiliar APIs without documentation?
- **Parallelism** — Do they work on multiple tasks concurrently?
- **Code quality** — Is the code clean, consistent, and follows existing patterns?

The four tasks escalate in difficulty:

| Task | Type | Difficulty | Key Skill Tested |
|------|------|-----------|-----------------|
| Ticket 1 | Bug fix | Easy | Debugging (silent parsing failure) |
| Ticket 2 | Bug fix + feature | Medium | Doc reading + API exploration + fallback logic |
| Ticket 3 | Integration | Medium-Hard | Async polling pattern discovery |
| Ticket 4 | Integration | Hard | Unfamiliar API + field mapping |

Completing all 4 is not expected. 2–3 tasks in 60–90 minutes is a strong result.

---

## 2. Pre-Interview Checklist

**Days before the interview:**

1. Share the skeleton repo link with the candidate
2. Ask them to:
   - Clone the repo
   - Run `uv sync` and `uv run pytest` to verify their environment
   - Set up their preferred AI tools (Cursor, Copilot, Claude Code, etc.)
3. Confirm they have Python 3.12 (exactly — not 3.13+) and [uv](https://docs.astral.sh/uv/) installed.
   If they don't have 3.12: `uv python install 3.12`

**Before the call:**

1. Run `bash scripts/prepare_delivery.sh` from this repo to generate
   `delivery/exercise.zip`
2. Have the zip file ready to share via Zoom chat or screen share
3. Open `tickets/interviewer/ticket-*.md` for reference during the interview

---

## 3. During the Interview

### Delivering the exercise

1. Share `delivery/exercise.zip` via Zoom chat
2. Tell the candidate: "Extract this into your project root — it will add the
   exercise files. Then run `bash setup.sh` to install the remaining
   dependencies."
3. Once setup completes: "Run `uv run python scripts/start.py` to start all
   servers, then open the README for task details."

### Timeline (suggested for 90 minutes)

| Time | Phase |
|------|-------|
| 0–5 min | Deliver zip, candidate sets up |
| 5–10 min | Candidate reads README + tickets, orients |
| 10–70 min | Working time |
| 70–80 min | Wrap up, discuss approach |
| 80–90 min | Questions from candidate |

### What to observe

- **Do they read the docs?** Ticket 2 requires finding Principle 5 in
  `docs/business-rules.md`. Candidates who skip docs will miss the fallback rule.
- **Do they explore the APIs?** Carrier C's polling pattern and Carrier D's
  self-describing endpoint both require API exploration.
- **Do they parallelize?** Strong candidates will kick off AI tasks for multiple
  tickets while reviewing code or docs.
- **How do they use AI?** Look for candidates who guide AI with context, not
  just paste errors. Good AI usage includes feeding relevant code + docs to
  the tool.

---

## 4. Task-by-Task Guide

### Ticket 1: Missing quote for high-revenue policies

**Root cause:** Carrier B returns premiums as comma-formatted strings (e.g.
`"2,343"` instead of `2343`). When premium >= $1,000, `int()` parsing fails
silently in `carrier_b.py`. Low-revenue submissions work fine because premiums
stay under $1,000.

**What good looks like:**
- Candidate identifies Carrier B as the failing carrier
- Finds the comma-formatting issue in the response
- Fixes the parsing (e.g. `float(premium.replace(",", ""))`)

**Common approaches:**
- Add logging to see which carrier fails → find the error
- Compare low-revenue vs high-revenue responses from Carrier B directly
- Read carrier_b.py client code and trace the data flow

**Hints if stuck:**
- "The verification script shows which carriers returned quotes — have you
  compared low-revenue vs high-revenue?"
- "What does the raw response from Carrier B look like for a $5M submission?"

**See:** `tickets/interviewer/ticket-1.md`

---

### Ticket 2: Missing quotes for high-limit requests

**Root cause:** Carrier A returns HTTP 200 with an error body (not an HTTP
error code) when the requested limit/retention isn't in their supported set.
The candidate must:
1. Discover the `/options` endpoint on Carrier A
2. Read Principle 5 in `docs/business-rules.md` (fallback to closest
   supported value)
3. Implement fallback logic in the carrier client

**What good looks like:**
- Discovers Carrier A's `/options` endpoint
- Reads and applies Principle 5 from business rules
- Implements clean fallback: query `/options`, find nearest supported value,
  re-request quote

**This is the "doc extraction" test.** Candidates who don't read the business
rules will either skip the carrier or hardcode values. The rule is buried at
Principle 5 in a 10-principle list — this is intentional.

**Hints if stuck:**
- "Have you looked at what Carrier A returns for a $5M limit?"
- "The business rules doc has some relevant guidance for this case."
- "Some carriers have endpoints that describe their capabilities."

**See:** `tickets/interviewer/ticket-2.md`

---

### Ticket 3: Integrate Carrier C (polling)

**Pattern:** Carrier C uses async polling. POST `/quotes` returns 202 with a
`poll_url`. The candidate must poll `GET /quotes/{id}` until status changes
from `"pending"` to `"ready"`.

**What good looks like:**
- Discovers the polling pattern by exploring the API
- Implements a polling loop with appropriate timeout
- Follows the existing carrier client pattern (`base.py`)
- Registers the new carrier in `server.py`

**Hints if stuck:**
- "What does Carrier C's response look like when you POST to `/quotes`?"
- "Notice the `poll_url` in the response?"

**See:** `tickets/interviewer/ticket-3.md`

---

### Ticket 4: Integrate Carrier D (unfamiliar API)

**Pattern:** Carrier D uses completely different conventions — different
endpoints (`/api/v1/insurance-request`), different field names (`revenue`
instead of `annual_revenue`, `coverage_amount` instead of `limit`,
`deductible` instead of `retention`, `annual_cost` instead of `premium`).

The `/api/v1/info` endpoint lists all available endpoints as a discovery
breadcrumb.

**What good looks like:**
- Discovers the `/api/v1/info` self-describing endpoint
- Maps all field names correctly to our standard format
- Handles bind via `/api/v1/accept` with `request_id`

**Hints if stuck:**
- "Have you tried hitting Carrier D's root or common discovery paths?"
- "Carrier D might have a different URL structure entirely."

**See:** `tickets/interviewer/ticket-4.md`

---

## 5. Evaluation Rubric

### Tasks Completed (weight: 35%)

| Level | Description |
|-------|------------|
| Strong | 3–4 tasks completed correctly |
| Good | 2 tasks completed, progress on others |
| Acceptable | 1 task completed, systematic approach shown |
| Below bar | No tasks completed or purely AI-driven without understanding |

### Code Quality (weight: 20%)

- Follows existing patterns (carrier client interface, error handling)
- Clean, readable code
- No unnecessary complexity
- Appropriate error handling

### AI Usage (weight: 20%)

- Uses AI tools actively, not passively
- Provides context to AI (relevant files, error messages, docs)
- Reviews and understands AI output before accepting
- Doesn't blindly copy-paste without verification

### Debugging & Problem-Solving (weight: 15%)

- Systematic approach to debugging (logs, API exploration, isolation)
- Identifies root causes, not just symptoms
- Explores APIs independently

### Doc Extraction & Domain Understanding (weight: 10%)

- Reads and applies the business rules document
- Finds Principle 5 (buried rule about fallback logic)
- Understands the insurance domain terms (limit, retention, premium)

---

## 6. Verification

After the candidate finishes (or time runs out), run the verification test
suite from this repo against the candidate's running servers:

```bash
uv run pytest tests/interviewer/test_verification.py -v
```

This tests all tasks end-to-end. The test names indicate which ticket they
verify (e.g. `test_ticket1_*`, `test_ticket2_*`, etc.).

Baseline tests (`test_basic_flow`, `test_low_revenue_both_carriers`) should
pass even with the unmodified skeleton.

---

## 7. After the Interview

If you want to review the candidate's code later, ask them to zip their
solution:

```bash
zip -r solution.zip . -x '.venv/*' '__pycache__/*' 'packages/*'
```

This is also documented in the candidate's README.

---

## 8. FAQ & Troubleshooting

**Q: The candidate's `uv sync` fails.**
A: Verify Python 3.12+ is installed. Run `python3 --version`. If using pyenv,
ensure the correct version is active.

**Q: `setup.sh` fails with "No matching distribution."**
A: The wheel contains .pyc compiled for Python 3.12. Check the candidate is
using exactly 3.12 (`python3 --version`). Run `uv python install 3.12` if needed.

**Q: Servers won't start (port already in use).**
A: Kill existing processes: `lsof -i :8000-8004 | grep LISTEN` then
`kill <pid>`. Or restart terminal.

**Q: Candidate asks about the simulators — can they see the source?**
A: No. The simulators are distributed as compiled bytecode (`.pyc` in a wheel).
This is intentional — they need to explore the APIs like real-world integrations.

**Q: Candidate finishes early.**
A: Ask them to improve error handling, add tests, refactor, or explain their
approach in detail. You can also discuss alternative implementations.

**Q: Candidate hasn't read the docs at all.**
A: Nudge them: "There's some reference documentation in the `docs/` folder
that might help." Don't point to the specific principle — discovering it is
part of the exercise.

**Q: Candidate is stuck on Ticket 2 but hasn't found Principle 5.**
A: After 10+ minutes: "The business rules document has some guidance on what
to do when a carrier doesn't support the exact requested values."
