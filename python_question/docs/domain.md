# Sayata Quoting Platform — Architecture & Business Rules

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

### System Components

1. **Submission Service** — Accepts business details and orchestrates the quoting
   process across all configured carriers.
2. **Carrier Clients** — Adapters for each carrier's API, responsible for
   translating between the platform's internal data model and each carrier's
   unique request/response format.
3. **Quote Aggregator** — Collects quotes from all carriers and stores them
   against the original submission.
4. **Binding Service** — Handles the acceptance of a specific quote by routing
   the bind request to the appropriate carrier.

## Business Principles

The following principles govern how the platform should behave. These have been
established through collaboration with our insurance partners and reflect
industry best practices.

### Principle 1: Transparency in Pricing

All premiums displayed to the user must accurately reflect the carrier's quoted
amount. No hidden fees or adjustments should be applied by the platform. The
carrier's premium is the premium — the platform does not mark up or modify it.

### Principle 2: Carrier Diversity

We aim to present quotes from as many carriers as possible for each submission.
A broader set of quotes gives the user more choice and increases the likelihood
of finding the best coverage at the best price. Every configured carrier should
be queried for every submission.

### Principle 3: Graceful Degradation

If a carrier is unavailable or returns an error, the platform should still
return quotes from the remaining carriers. A single carrier failure must not
prevent the user from seeing other available options. Partial results are always
better than no results.

### Principle 4: Data Integrity

All data flowing through the platform must be validated at ingestion. Carrier
responses should be parsed carefully and any unexpected formats should be handled
rather than silently dropped. Logging is encouraged for troubleshooting but
should not expose sensitive business data.

### Principle 5: Best Available Coverage

Always try to offer the best quotes to the user. If a carrier does not support
the exact requested limit or retention, the platform should request a quote for
the closest available option rather than simply skipping that carrier. Carriers
that expose an options or capabilities endpoint should be consulted to determine
what values they support, and the nearest supported value should be used as a
fallback.

### Principle 6: Consistent User Experience

Regardless of which carriers are queried or how their APIs behave, the user
should see a consistent response format. Quote data should always include the
carrier name, premium, limit, retention, and a unique quote identifier. Internal
carrier-specific field names or conventions should never leak into the user-facing
API.

### Principle 7: Auditability

Every submission, quote request, and bind action should be traceable. While
full audit logging is outside the scope of the current implementation, the
system should be designed so that adding audit trails later is straightforward.
Unique IDs should be generated for every transaction.

### Principle 8: Security by Default

Carrier API communications should use HTTPS in production. API keys and
credentials should never be hardcoded. For this exercise, simulators run over
HTTP on localhost, which is acceptable for development.

### Principle 9: Performance Targets

Quote retrieval should complete within 30 seconds for synchronous carriers. For
asynchronous carriers (polling-based), the platform should continue to poll
within a reasonable window (up to 60 seconds) before timing out. Users should
not be blocked from viewing partial results while other carriers are still
processing.

### Principle 10: Extensibility

Adding a new carrier should require only a new carrier client module and
registering it with the server. No changes to the core submission or quoting
logic should be needed. The carrier client interface is the contract — as long
as a new client implements `get_quote` and `bind_quote`, it integrates
seamlessly.

## Insurance Domain Background

### What is a Submission?

A submission contains the business details needed to request an insurance quote:
the company name, industry vertical, annual revenue, and the coverage parameters
(limit and retention) the business is seeking.

### What is a Quote?

A quote is a carrier's offer to insure the business under specific terms. It
includes the premium (annual cost of the insurance), the limit (maximum payout
the carrier will make in the event of a claim), and the retention (the deductible
the business pays before insurance kicks in).

### What is Binding?

Binding is the act of accepting a quote. Once a user binds a quote, it becomes
a policy. The bind request is sent to the carrier, which confirms acceptance.

### Limits and Retentions

- **Limit**: The maximum amount the insurer will pay for a covered claim. Common
  values range from $500K to $10M.
- **Retention**: The amount the insured business must pay out of pocket before
  insurance coverage applies. Also called a deductible. Common values range from
  $10K to $500K.

Not all carriers support all limit/retention combinations. Some carriers have
fixed menus of supported values, while others accept any reasonable amount.

## UX Principles (Frontend Reference)

> Note: These principles apply to the frontend application and are included here
> for completeness. Backend developers should focus on the API behavior described
> in the Business Principles section above.

- Quote comparison should display all available options side by side.
- Premiums should be formatted with currency symbols and thousand separators.
- Loading states should indicate which carriers are still processing.
- Error states should be specific — "Carrier X is unavailable" rather than
  generic error messages.
- The bind action should require explicit user confirmation before proceeding.
