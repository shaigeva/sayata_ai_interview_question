# Ticket 3: Integrate Carrier C

## Priority: Medium

## Description

Carrier C is a new insurance carrier that we need to integrate into our quoting
platform. Their API server is already running on port 8003, but we haven't
connected it to our submission flow yet.

Unlike Carriers A and B, Carrier C does not return quotes immediately — it uses
an async pattern (submit a quote request, then poll or retrieve the result
later). The candidate needs to discover this by exploring the API and implement
the appropriate integration.

## Acceptance Criteria

- When a submission is created, a quote should be requested from Carrier C.
- Carrier C quotes should appear in the submission's quotes list when retrieved
  via `GET /submissions/{id}`.
- The integration should follow the existing carrier client pattern
  (see `src/sayata/carriers/base.py`).
- Carrier C should be registered in the server alongside the existing carriers.

## What to Look For

- Does the candidate explore the Carrier C API to understand its async pattern?
- Can they adapt the existing carrier client pattern for a non-immediate response?
- Do they handle the polling/retrieval step cleanly?
- Carrier C is running on `http://localhost:8003`.
- The existing carrier clients in `src/sayata/carriers/` show the expected
  pattern for new integrations.
