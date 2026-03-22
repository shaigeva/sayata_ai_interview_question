# Ticket 2: Missing Quote for "Nano Insurance Co"

**Priority:** High

This request returns fewer quotes than expected.

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
