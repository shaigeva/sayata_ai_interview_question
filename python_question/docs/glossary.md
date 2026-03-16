# Insurance Domain Glossary

## What is a Submission?

A submission contains the business details needed to request an insurance quote:
the company name, industry vertical, annual revenue, and the coverage parameters
(limit and retention) the business is seeking.

## What is a Quote?

A quote is a carrier's offer to insure the business under specific terms. It
includes the premium (annual cost of the insurance), the limit (maximum payout
the carrier will make in the event of a claim), and the retention (the deductible
the business pays before insurance kicks in).

## What is Binding?

Binding is the act of accepting a quote. Once a user binds a quote, it becomes
a policy. The bind request is sent to the carrier, which confirms acceptance.

## Limits and Retentions

- **Limit**: The maximum amount the insurer will pay for a covered claim. Common
  values range from $500K to $10M.
- **Retention**: The amount the insured business must pay out of pocket before
  insurance coverage applies. Also called a deductible. Common values range from
  $10K to $500K.

Not all carriers support all limit/retention combinations. Some carriers have
fixed menus of supported values, while others accept any reasonable amount.
