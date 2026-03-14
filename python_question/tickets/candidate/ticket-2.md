# Ticket 2: Missing Quotes for "Large Enterprise"

**Priority:** High

This request returns fewer quotes than expected.

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
