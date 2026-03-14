# Ticket 1: Missing Quote for "Beg Tech Corp"

**Priority:** High

This request returns 1 quote instead of 2.

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
