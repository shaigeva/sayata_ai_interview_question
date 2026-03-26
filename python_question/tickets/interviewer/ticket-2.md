# Ticket 2: Missing Quote for Unsupported Limit

## Priority: High

## Description

When a business requests a limit that Carrier A doesn't support (e.g. $1.5M),
Carrier A returns a 200 with `{"error": "incompatible option"}`. The current
code treats this as a valid response and produces no quote.

The candidate needs to:
1. Discover Carrier A's supported values (the endpoint is not obvious —
   the error message gives no hint)
2. Read and apply the directional fallback rules from `business-rules.md`
   (Principle 5): limits round UP, retentions round DOWN
3. Implement fallback logic in the carrier client

## Steps to Reproduce

1. Submit with an unsupported limit:
   ```
   POST /submissions
   {
     "business_name": "Nano Insurance Co",
     "industry": "technology",
     "annual_revenue": 200000,
     "requested_limit": 1500000,
     "requested_retention": 50000
   }
   ```

2. Retrieve: `GET /submissions/{id}` — only 1 quote (Carrier B), Carrier A missing.

## The Traps

**Trap 1 — Finding the options endpoint.** The error message just says
"incompatible option" with no hint. The endpoint is `/quoting_options` (not
`/options`). Candidate can discover it via FastAPI's `/docs` endpoint or by
reading business-rules.md which mentions "options or capabilities endpoint."

**Trap 2 — Fallback direction.** Without the docs, an AI agent will implement
generic "closest value" logic. For limit 1.5M with options [500K, 1M, 2M, 3M]:
- Naive "closest": 1M (distance 500K) — **WRONG**
- Correct per business rules: 2M (nearest >=) — **RIGHT**
This is the key test of doc extraction. The AI produces working but incorrect code.

**Trap 3 — Retention direction is opposite.** For retention 75K with options
[25K, 50K, 100K, 250K]:
- Naive "closest": either 50K or 100K
- Correct per business rules: 50K (nearest <=) — **retention rounds DOWN**

## What to Look For

- Does the candidate discover `/quoting_options` via API exploration or `/docs`?
- Do they read and apply the directional rules from business-rules.md?
- Does the naive AI solution round the wrong direction? Does the candidate catch it?
- Does the fallback logic mutate the submission object (breaking other carriers)?
