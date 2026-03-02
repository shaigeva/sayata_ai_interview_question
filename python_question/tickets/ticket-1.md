# Ticket 1: Quotes Missing for High-Value Policies

## Priority: High

## Description

We've received reports that when a business with high annual revenue submits
for a quote, we're only returning one quote instead of two. Both Carrier A and
Carrier B should be returning quotes for every valid submission.

## Steps to Reproduce

1. Submit a business with high annual revenue (e.g. $5M+):
   ```
   POST /submissions
   {
     "business_name": "Big Tech Corp",
     "industry": "technology",
     "annual_revenue": 5000000,
     "requested_limit": 1000000,
     "requested_retention": 50000
   }
   ```

2. Retrieve the submission:
   ```
   GET /submissions/{id}
   ```

3. Only 1 quote is returned instead of 2.

## Expected Behavior

Both Carrier A and Carrier B should return quotes for this submission. The
submission should have 2 quotes.

## Notes

- This works fine for lower revenue businesses (e.g. $500K annual revenue).
- The issue seems specific to higher-value policies.
- No errors are visible in the server logs.
