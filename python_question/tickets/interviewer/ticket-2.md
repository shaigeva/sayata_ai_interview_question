# Ticket 2: Quotes Missing for High-Limit Requests

## Priority: High

## Description

When a business requests a high coverage limit (e.g. $5M), we're not returning
the expected number of quotes. At least one carrier is failing to produce a
quote, but the reason isn't immediately clear from the server response.

The root cause is that some carriers don't support the exact requested limit
or retention values. The candidate needs to discover the carrier's supported
values (via API exploration) and implement fallback logic per the domain rules
in `docs/domain.md` — specifically: when the exact limit isn't available,
use the nearest available limit that is >= the requested one; same for retention.

## Steps to Reproduce

1. Submit a business requesting a high coverage limit:
   ```
   POST /submissions
   {
     "business_name": "Large Enterprise",
     "industry": "manufacturing",
     "annual_revenue": 2000000,
     "requested_limit": 5000000,
     "requested_retention": 50000
   }
   ```

2. Retrieve the submission:
   ```
   GET /submissions/{id}
   ```

3. Fewer quotes are returned than expected.

## Expected Behavior

The platform should return quotes from all configured carriers. If a carrier
doesn't support the exact requested limit or retention, we should still
attempt to get a quote using the nearest supported value (see `docs/domain.md`).

## What to Look For

- Does the candidate explore the carrier APIs to find supported values?
- Do they read and apply the domain rules from `docs/domain.md`?
- Can they implement the fallback logic cleanly within the existing architecture?
- Some carriers expose endpoints that list their supported options.
