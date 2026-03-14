# User Intent — Sayata AI Interview Question

## What This Project Is

A take-home-style coding interview exercise for Sayata, designed to evaluate
candidates on three axes:

1. **Coding ability** — Can they read, debug, and extend a working codebase?
2. **AI tooling proficiency** — Do they effectively leverage AI assistants to
   move faster, explore APIs, and parallelize work?
3. **Problem solving** — Can they diagnose issues, read documentation for buried
   requirements, and figure out unfamiliar systems?

## How the Interview Works

- **Duration:** ~1–1.5 hours on Zoom with interviewers present.
- **Pre-interview:** Candidate receives the skeleton repo ahead of time so they
  can set up their environment and preferred AI tools (Cursor, Copilot, Claude
  Code, etc.). They're told something like "you will be asked to implement
  endpoints that work with an API."
- **During interview:** Candidate receives all tasks at once (in text form) and
  works through them. They can ask the interviewers questions.
- **Expectation:** Candidates are NOT expected to finish everything. The tasks
  escalate in difficulty so weaker candidates still complete something meaningful
  and stronger candidates are appropriately challenged.

## Why Parallelism Matters

A core signal we're looking for: can the candidate run multiple AI-assisted
workstreams at the same time? Without parallelism, the interview degrades into
"watch the AI generate code" — which isn't what we want to measure. Tasks are
deliberately designed to be independent so candidates CAN work on multiple things
concurrently. Whether they do is signal.

## The Domain

Sayata is an insurance marketplace. The flow is:

1. **Submission** — A user provides details about their business (industry,
   revenue, etc.).
2. **Quoting** — Sayata sends submission details to insurance carriers via their
   APIs. Each carrier returns a quote with premium, limit (max payout), and
   retention (deductible).
3. **Binding** — The user accepts a quote, and Sayata sends a bind request to
   the carrier's API.

Different carriers have different API styles: some return quotes synchronously,
some require polling, some use webhooks. This variety is the source of task
complexity.

## Ticket Design Philosophy

Tickets come in two versions, stored in `tickets/interviewer/` and
`tickets/candidate/`:

- **Candidate tickets** are intentionally minimal — just the symptom and a repro,
  like a real bug report from a PM or QA. Even ticket titles should be neutral
  and describe the symptom ("Missing Quote"), not hint at the cause ("Quotes
  Missing for High-Value Policies"). The body is the same: "this request returns
  1 quote instead of 2." No root cause analysis, no hints about which carrier is
  failing, no pointers to relevant code. The investigation, diagnosis, and
  solution design is work the candidate should do — ideally with their AI tools.
  Giving them the analysis defeats the purpose of the exercise.

- **Interviewer tickets** contain the full context: root cause, what to look for,
  how the candidate should ideally approach the problem, and evaluation criteria.
  These help interviewers follow along and assess the candidate's process.

## What the Candidate Receives

### A Working Skeleton

The repo ships with a baseline end-to-end flow that already works:

- POST a submission → returns "created"
- GET the submission → returns quotes from 2 carrier simulators (Carrier A and
  Carrier B)
- POST a bind request → sends bind to carrier, returns "bound"

The candidate does NOT build from scratch. They extend and fix a working system.

### Carrier Simulators

Local Python servers (FastAPI) that simulate carrier APIs. These run alongside
the candidate's server — all in the same Docker container, same process,
different ports. They have in-memory state only and are deterministic for
troubleshooting tasks.

Carriers should be inspectable (e.g., `GET /status` endpoint).

### Two Key Documents

1. **Domain/Principles Doc** — A deliberately large-ish internal-style document
   ("Sayata Quoting Platform — Architecture & Business Rules") with ~8–10
   business principles. Most are already implemented or irrelevant. One critical
   rule is buried in the middle: "Always try to offer the best quotes — if a
   carrier doesn't support a requested limit or retention, offer the closest
   available option." Whether the candidate extracts this rule (and feeds the doc
   to their AI tool) is signal.

2. **Candidate Instructions Doc** — Clear, concise "here's what you're doing
   today" document with setup instructions, task descriptions, and how to verify
   work. This removes reliance on interviewers to explain everything perfectly.

### Test Infrastructure

- pytest is pre-installed and configured.
- A stub test file exists that imports from the actual codebase — so candidates
  don't waste time on test setup.
- A Python `requests`-based test script sends real HTTP calls and checks
  responses — serves as both documentation of expected behavior and verification.

### Package Management

- `uv` for Python package management. Clear setup instructions provided.

## The Tasks

### Task 1: Bug — Quotes Missing for High-Value Policies (Easy)

**Symptom:** Test expects 2 quotes, gets 1.
**Root cause:** Carrier B returns prices as comma-formatted strings (`"2,343"`).
`int("2,343")` throws `ValueError`. Server has a `try/except` that silently
swallows the error.
**Intent:** Tests basic debugging. The candidate needs to look at the carrier
response, see the formatting issue, and fix the parsing. The silent exception is
a deliberate trap.

### Task 2: Bug + Feature — Quotes Missing for High-Limit Requests (Easy→Medium)

**Symptom:** Test expects 2 quotes, gets 1.
**Root cause:** Carrier A returns HTTP 200 with an error body when the requested
limit exceeds its maximum. Server checks `response.status_code == 200` and
naively parses, hitting an error.
**Proper fix:** Per the domain doc's buried business rule — when a carrier
doesn't support the exact requested limit/retention, request the closest
available option. Carrier A exposes `GET /options` listing supported values.
**Intent:** Two-part task. First diagnose why quotes are missing (API returns 200
but with an error body). Then implement the correct behavior by discovering the
business rule in the domain doc and using the `/options` endpoint.

### Task 3: Feature — Integrate Polling Carrier (Medium-Hard)

**Description:** Carrier C returns a `quote_id` instead of a quote. Server must
poll `GET /quotes/{id}` until status is `"ready"`.
**Intent:** Tests ability to implement async patterns. Background task fires off
polling, stores results in memory. When user queries submission, completed
polling results are included. No task queue or database needed.

### Task 4: Feature — New Carrier with Unfamiliar API (Hard)

**Description:** Carrier D is running but has a completely different API shape —
different field names, different endpoint structure. Minimal documentation.
**Intent:** Tests AI-driven exploration. Candidate who points their AI tool at
the carrier's endpoints (hitting them, reading responses) will move fast.
Candidate who tries to code blind won't.

## Design Constraints

- **Tasks must be parallelizable** — they touch different carriers/files so
  candidates can work on multiple simultaneously.
- **Carrier simulators must be deterministic** — specific submissions reliably
  trigger specific behaviors for troubleshooting tasks.
- **Tasks 1 and 2 use different carriers/submissions** so the candidate can't
  conflate them.
- **Everything is in-memory** — no persistence, no databases, no external
  services.
- **One command to start everything** — minimize operational overhead so
  candidates spend time on actual work.

## What We Evaluate

- Tasks completed and correctness
- Code quality and structure
- How effectively they use AI tools
- Debugging and problem-solving approach
- Whether they read and extract from documentation
- Whether they parallelize work
- How they handle ambiguity (Task 4)
