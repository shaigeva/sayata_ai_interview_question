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

## 2. Pre-Interview Setup (days before)

### Build the delivery artifacts

From this repo:

```bash
bash scripts/prepare_delivery.sh
```

This produces two files in `delivery/`:
- `skeleton.zip` — send now (environment setup only, no exercise content)
- `exercise.zip` — send during the interview

### Send skeleton.zip to the candidate

Send `delivery/skeleton.zip` to the candidate via email/Slack/etc. along with
the following message (copy-paste):

> **Interview exercise — environment setup**
>
> Please complete these steps before our interview:
>
> 1. Make sure you have **Python 3.12** (exactly — not 3.13+) and
>    **[uv](https://docs.astral.sh/uv/)** installed.
>    If you don't have Python 3.12: `uv python install 3.12`
>
> 2. Create a new folder, copy the zip into it, and extract:
>    ```
>    mkdir sayata-interview
>    cp ~/Downloads/skeleton.zip sayata-interview/
>    cd sayata-interview
>    unzip skeleton.zip
>    ```
>
> 3. Install dependencies and run the tests:
>    ```
>    uv sync
>    uv run pytest -v
>    ```
>    You should see **2 tests pass** (an import check and a server health check).
>
> 4. Set up your preferred AI tools (Cursor, Copilot, Claude Code, etc.) in
>    this project.
>
> 5. You're expected to use AI tooling during the interview — that's part of
>    what we're evaluating.
>
> During the interview you'll receive a second zip with the actual exercise.
> This setup is just to make sure your environment is ready so we don't
> spend interview time on installation.

### How the candidate verifies skeleton setup

They should see this when they run `uv run pytest -v`:

```
tests/test_setup.py::test_imports PASSED
tests/test_setup.py::test_server_health PASSED

2 passed
```

If they report issues, common fixes:
- Wrong Python version → `uv python install 3.12`
- `uv` not installed → `curl -LsSf https://astral.sh/uv/install.sh | sh`

---

## 3. During the Interview

### Before the call

1. Have `delivery/exercise.zip` ready to share via Zoom chat
2. Open `tickets/interviewer/ticket-*.md` for reference

### Delivering the exercise (first 5 minutes)

Share `delivery/exercise.zip` via Zoom chat and tell the candidate (copy-paste):

> Extract this zip into your project folder — the same one from the setup.
> It will add the exercise files alongside what's already there.
>
> ```
> cd sayata-interview
> unzip exercise.zip
> bash setup.sh
> ```
>
> Then start the servers:
> ```
> uv run python scripts/start.py
> ```
>
> Open `README.md` for the full instructions and tasks.

### How the candidate verifies exercise setup

After extracting, the candidate should confirm:

1. **`setup.sh` completes without errors** — it installs the carrier
   simulator package.

2. **Key files are in place** — they should see both the original skeleton
   files and the new exercise files:
   ```
   ls README.md README_PREP.md
   ls src/sayata/server.py src/sayata/server_stub.py
   ls tickets/
   ls docs/
   ```
   - `README.md` (new — exercise instructions) alongside `README_PREP.md`
     (original setup readme)
   - `src/sayata/server.py` (new — the real server) alongside
     `src/sayata/server_stub.py` (original stub)
   - `tickets/` directory with `ticket-1.md` through `ticket-4.md`
   - `docs/` directory with `architecture.md`, `business-rules.md`,
     `glossary.md`, `frontend-guidelines.md`

3. **Servers start and respond** — after running `uv run python scripts/start.py`,
   in a second terminal:
   ```
   uv run python scripts/verify.py
   ```
   This should show the server is up, carrier simulators are running on
   ports 8001–8004, and a basic submission returns 2 quotes.

If something looks wrong, the most common issue is extracting the zip into a
subfolder instead of the project root. The fix: re-extract with
`unzip -o exercise.zip` from the project root.

### Timeline (suggested for 90 minutes)

| Time | Phase |
|------|-------|
| 0–5 min | Deliver zip, candidate sets up and verifies |
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

## 6. Testing & Verification

The exercise has three testing layers, each serving a different audience and
purpose. Only the first two are visible to candidates.

### Layer 1: Candidate unit tests (`tests/test_stub.py`)

**Audience:** Candidate
**Requires:** Nothing running — pure unit tests

```bash
uv run pytest tests/ -v
```

Shipped in the exercise zip. Two tests that prove the test infrastructure works
by instantiating Pydantic models (`Submission`, `Quote`). These always pass.
Candidates can extend this file or create new test files.

### Layer 2: Candidate verification script (`scripts/verify.py`)

**Audience:** Candidate
**Requires:** All servers running (`uv run python scripts/start.py`)

```bash
uv run python scripts/verify.py
```

A non-pytest script that sends real HTTP requests to the running servers and
prints human-readable results. It runs three scenarios:

1. **Low-revenue submission** ($500K) — should return 2 quotes (baseline)
2. **High-revenue submission** ($5M) — tests Ticket 1 (Carrier B comma bug)
3. **High-limit submission** ($5M limit) — tests Ticket 2 (Carrier A fallback)

Also pings all four carrier simulators to confirm they're running. This gives
candidates quick visual feedback without needing to write tests.

### Layer 3: Interviewer test suite (`tests/interviewer/test_verification.py`)

**Audience:** Interviewer only (never shipped to candidates)
**Requires:** All servers running, candidate's code in place

```bash
uv run pytest tests/interviewer/test_verification.py -v
```

Full pytest suite with 14 tests covering every task. Run this from **this
repo** (not the candidate's repo) against the candidate's running servers on
localhost:8000. The tests hit the same server the candidate is running.

#### Test breakdown by ticket

| Test | Ticket | What it verifies |
|------|--------|-----------------|
| `test_basic_flow` | Baseline | Low-revenue submit → 2 quotes → bind |
| `test_submission_not_found` | Baseline | 404 for nonexistent submission |
| `test_low_revenue_both_carriers` | Baseline | Both A and B return quotes |
| `test_ticket1_high_value_policy` | 1 | $5M revenue → quotes from both A and B |
| `test_ticket1_premium_is_numeric` | 1 | Carrier B premium is a number, not string |
| `test_ticket2_high_limit_request` | 2 | $5M limit → quotes from both A and B |
| `test_ticket2_uses_closest_limit` | 2 | Carrier A falls back to closest limit (3M for 5M) |
| `test_ticket2_unsupported_retention` | 2 | Carrier A falls back to closest retention |
| `test_ticket3_carrier_c_present` | 3 | Carrier C quote appears (after polling delay) |
| `test_ticket3_carrier_c_quote_fields` | 3 | Carrier C quote has all standard fields |
| `test_ticket4_carrier_d_present` | 4 | Carrier D quote appears |
| `test_ticket4_carrier_d_quote_normalized` | 4 | Carrier D quote normalized to standard format |
| `test_ticket4_carrier_d_bind` | 4 | Carrier D quote can be bound |
| `test_all_carriers_combined` | All | Standard submission returns all 4 carriers |

The baseline tests should pass with the unmodified skeleton. Ticket-specific
tests fail until the candidate fixes/implements that task.

Tests for tickets 3 and 4 include `time.sleep()` calls (up to 10 seconds) to
wait for async polling to complete. The full suite takes ~35 seconds to run.

#### Running a subset

To check a specific ticket:

```bash
uv run pytest tests/interviewer/test_verification.py -v -k "ticket1"
uv run pytest tests/interviewer/test_verification.py -v -k "ticket2"
uv run pytest tests/interviewer/test_verification.py -v -k "ticket3"
uv run pytest tests/interviewer/test_verification.py -v -k "ticket4"
```

### Pre-interview: testing the delivery artifacts

Before the interview, verify that the full delivery pipeline works end-to-end.
Run the automated end-to-end test:

```bash
bash scripts/test_delivery.sh
```

This script builds both zips, simulates the full candidate flow in a temp
directory (extract skeleton → `uv sync` → extract exercise → `setup.sh` →
start servers → `verify.py` → baseline tests → leak checks), and reports
pass/fail for 13 checks.

You can also run it manually:

```bash
bash scripts/prepare_delivery.sh

mkdir /tmp/test_interview && cd /tmp/test_interview
unzip /path/to/delivery/skeleton.zip
uv sync && uv run pytest -v

unzip -o /path/to/delivery/exercise.zip
bash setup.sh
uv run python scripts/start.py &
sleep 3
uv run python scripts/verify.py
kill %1
```

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
