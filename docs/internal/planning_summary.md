# Interview Question — Planning Summary

## Overview

An interview question for Sayata, designed to evaluate coding ability, AI tooling
proficiency, and problem-solving skills.

- **Duration:** ~1–1.5 hours, on Zoom with interviewers present
- **Format:** Candidate receives a skeleton repo ahead of time to set up their
  preferred AI tooling. During the session, they receive multiple independent
  tasks/tickets and work through as many as they can.
- **Parallelism is key:** Without it, the candidate just watches their AI tool
  generate code. Tasks are designed to be independent so the candidate can run
  multiple AI-assisted workstreams concurrently. This is a core skill being
  evaluated.
- **Not expected to finish everything.** Escalating complexity means weaker
  candidates still complete something, stronger candidates get further.

## Domain

Sayata is an insurance marketplace.

- **Submission:** A user provides details about their business.
- **Quote:** Sayata sends submission details to insurance carriers via API and
  receives quotes back. Key fields include premium, limit (max payout), and
  retention (deductible).
- **Bind:** A quote can be bound (accepted) via another API call to the carrier.

Carriers have different APIs — some return quotes synchronously, some require
polling, some use webhooks.

## Technical Setup

- **Candidate's server:** FastAPI (Python). This is what the candidate works on.
- **Carrier simulators:** Local Python servers with in-memory state, included in
  the repo. Multiple instances simulate different carriers.
- **No auth**, single hard-coded user scenario, all state in memory.
- **One command to start everything** — minimize operational overhead.
- **Test script:** Python `requests`-based script that sends API calls and checks
  responses. Serves as both documentation and verification.
- **Carrier simulators should be inspectable** (e.g., `GET /status`).

## Starting Point (Skeleton)

The repo ships with a working end-to-end flow:

1. POST a submission → returns "created"
2. GET the submission → returns a list of quotes (from 2 carrier simulator instances)
3. POST a bind request for a quote → sends bind to carrier, returns "bound"

This baseline works. The candidate's tasks build on top of it.

## Documents

### 1. Domain/Principles Doc (large-ish)

Internal-style documentation: "Sayata Quoting Platform — Architecture & Business
Rules." Contains ~8–10 business principles, most of which are already implemented
or irrelevant to the tasks. Includes insurance domain background, UX principles
that don't apply to the backend, etc.

**Key buried rule:** "Always try to offer the best quotes — if a carrier doesn't
support a requested limit or retention, offer the closest available option."

The candidate is expected to feed this doc to their AI tool and extract relevant
requirements. Whether they do this (and how effectively) is signal.

### 2. Candidate Instructions Doc

Clear, concise "here's what you're doing today" document:

- What the repo contains and how to run it
- The tasks/tickets
- That they're expected to use AI tooling
- That they can ask the interviewers questions
- How to verify their work (the test script)
- References the domain doc for business rules

Solves the problem of relying on interviewers to explain everything perfectly.

## Task List

**General note for all tasks:** Everything is in-memory. No persistence or
databases needed. Background work (e.g., polling) can use in-memory state and
fire-and-forget background tasks.

### Task 1: Bug — Quotes missing for high-value policies

- **Type:** Troubleshooting
- **Difficulty:** Easy
- **Symptom:** A test case expects 2 quotes but gets 1.
- **Root cause:** Carrier B returns prices as comma-formatted strings. Prices
  under $1,000 parse fine (`int("500")`). Prices ≥ $1,000 come as `"2,343"` —
  `int("2,343")` throws `ValueError`. Server has `try/except` that silently
  swallows the error.
- **Must be deterministic:** A specific submission reliably triggers a price > $1,000.
- **Different carrier/submission than Task 2**, so the candidate can't conflate them.

### Task 2: Bug — Quotes missing for high-limit requests + support closest option

- **Type:** Troubleshooting + Implementation
- **Difficulty:** Easy → Medium
- **Symptom:** A test case expects 2 quotes but gets 1.
- **Root cause:** Carrier A returns HTTP 200 with an error body when the requested
  limit exceeds its maximum. Server checks `response.status_code == 200` and
  tries to parse a quote from the error body.
- **Proper fix:** Per the domain doc's business rule — when a carrier doesn't
  support the exact requested limit or retention, request the closest available
  option. Carrier A exposes `GET /options` with its supported values.
- **Two-part task:** First, diagnose the bug (why quotes are missing). Then,
  implement the correct behavior by reading the domain doc's "closest option"
  rule and mapping to supported values.
- **Difficulty tunable:** Error message in the 200 body can be more or less
  descriptive.

### Task 3: Feature — Integrate polling carrier (Carrier C)

- **Type:** Implementation
- **Difficulty:** Medium-Hard
- **Description:** Carrier C doesn't return quotes synchronously. It returns a
  `quote_id`, and the server must poll `GET /quotes/{id}` until the status is
  `"ready"`.
- **In-memory is fine:** The server can fire off a background task that polls the
  carrier and stores results in memory. No need for a task queue or database.
  When the user queries the submission, any completed polling results are
  included in the response.

### Task 4: Feature — Integrate a new carrier with an unfamiliar API

- **Type:** Implementation
- **Difficulty:** Hard
- **Description:** Carrier D is running but has a different API shape — different
  field names, different endpoint structure. Minimal documentation provided. The
  candidate needs to explore the API (hit endpoints, read responses) and build
  the integration.
- **Tests AI-driven exploration:** The candidate who points their AI at the
  carrier's endpoints will move fast; the one who tries to code blind won't.

## Design Principles

- **Tasks should be parallelizable:** Touch different files/endpoints. Each
  carrier as its own module.
- **Advance notice should hint at parallel work.**
- **Carrier simulators must be deterministic** for troubleshooting tasks.
- **Evaluation rubric needed:** Tasks completed, code quality, AI tool usage
  effectiveness, debugging/problem-solving approach.
- **4–5 well-defined tasks** rather than an overwhelming list.
