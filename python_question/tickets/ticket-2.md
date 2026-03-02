# Ticket 2: Quotes Missing for High-Limit Requests

## Priority: High

## Description

When a business requests a high coverage limit (e.g. $5M), we're not returning
the expected number of quotes. It appears that at least one carrier is failing
to produce a quote, but the reason isn't immediately clear from the server
response.

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
attempt to get a quote — consult the domain documentation (`docs/domain.md`)
for the relevant business rules on how to handle this.

## Notes

- Pay close attention to how each carrier's API responds to unsupported values.
- Some carriers expose endpoints that list their supported options.
- The domain document has specific guidance on how to handle limit/retention
  mismatches.
