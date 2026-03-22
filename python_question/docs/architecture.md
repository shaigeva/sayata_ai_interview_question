# Sayata Platform Architecture

## About Sayata

Sayata is a leading insurance marketplace that connects businesses with insurance
carriers. Our platform streamlines the quoting and binding process for commercial
insurance policies, making it faster and more transparent for all parties
involved.

## Platform Architecture Overview

The Sayata quoting platform operates as a middleware layer between businesses
seeking insurance and the carriers that provide it. When a business submits their
details, the platform fans out requests to multiple insurance carriers
simultaneously, aggregates the returned quotes, and presents them to the user in
a normalized format.

Each carrier exposes its own API with its own conventions. Some respond
synchronously, others use polling or callback patterns. The platform abstracts
these differences behind a unified submission → quote → bind workflow.

## System Components

1. **Submission Service** — Accepts business details and orchestrates the quoting
   process across all configured carriers.
2. **Carrier Clients** — Adapters for each carrier's API, responsible for
   translating between the platform's internal data model and each carrier's
   unique request/response format.
3. **Quote Aggregator** — Collects quotes from all carriers and stores them
   against the original submission.
4. **Binding Service** — Handles the acceptance of a specific quote by routing
   the bind request to the appropriate carrier.

## Local Development Setup

```
You (candidate)              Carrier Simulators
┌──────────────┐            ┌───────────────────┐
│  server.py   │───────────▶│ Carrier A  :8001   │
│  (port 8000) │───────────▶│ Carrier B  :8002   │
│              │            │ Carrier C  :8003   │
│              │            │ Carrier D  :8004   │
└──────────────┘            └───────────────────┘
```

- **Your server** (`src/sayata/server.py`) receives submissions, fetches quotes
  from carriers, and handles binds.
- **Carrier simulators** are local mock APIs that behave like real insurance
  carrier systems. They're read-only for you — don't modify them.
- **Carrier clients** (`src/sayata/carriers/`) contain the logic for calling each
  carrier's API.

Currently, only Carrier A and Carrier B are integrated. Carriers C and D are
running but not connected.
