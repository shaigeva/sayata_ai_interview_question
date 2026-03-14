# Ticket 4: Integrate Carrier D

## Priority: Low

## Description

Carrier D is another insurance carrier we need to add to the platform. Their
API server is running on port 8004, but it has not been integrated yet.

Carrier D uses a completely different API structure from our existing carriers —
different endpoint paths, different field names, different response shapes. The
candidate needs to discover the API structure by exploring the service (hint:
it has an OpenAPI/Swagger spec or self-describing endpoint).

## Acceptance Criteria

- When a submission is created, a quote should be requested from Carrier D.
- Carrier D quotes should appear in the submission's quotes list, normalized
  to our standard quote format (carrier name, premium, limit, retention,
  quote ID).
- The integration should follow the existing carrier client pattern
  (see `src/sayata/carriers/base.py`).
- Carrier D should be registered in the server alongside the existing carriers.

## What to Look For

- Does the candidate discover the self-describing API endpoint (e.g., /openapi.json, /docs)?
- Can they map the different field names to our standard format?
- Do they follow the existing carrier client pattern consistently?
- Carrier D is running on `http://localhost:8004`.
- Their API uses different terminology and endpoint structure from our other
  carriers.
