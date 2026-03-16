# Business Rules & Operating Principles

The following principles govern how the platform should behave. These have been
established through collaboration with our insurance partners and reflect
industry best practices.

## Principle 1: Transparency in Pricing

All premiums displayed to the user must accurately reflect the carrier's quoted
amount. No hidden fees or adjustments should be applied by the platform. The
carrier's premium is the premium — the platform does not mark up or modify it.

## Principle 2: Carrier Diversity

We aim to present quotes from as many carriers as possible for each submission.
A broader set of quotes gives the user more choice and increases the likelihood
of finding the best coverage at the best price. Every configured carrier should
be queried for every submission.

## Principle 3: Graceful Degradation

If a carrier is unavailable or returns an error, the platform should still
return quotes from the remaining carriers. A single carrier failure must not
prevent the user from seeing other available options. Partial results are always
better than no results.

## Principle 4: Data Integrity

All data flowing through the platform must be validated at ingestion. Carrier
responses should be parsed carefully and any unexpected formats should be handled
rather than silently dropped. Logging is encouraged for troubleshooting but
should not expose sensitive business data.

## Principle 5: Best Available Coverage

Always try to offer the best quotes to the user. If a carrier does not support
the exact requested limit or retention, the platform should request a quote for
the closest available option rather than simply skipping that carrier. Carriers
that expose an options or capabilities endpoint should be consulted to determine
what values they support, and the nearest supported value should be used as a
fallback.

## Principle 6: Consistent User Experience

Regardless of which carriers are queried or how their APIs behave, the user
should see a consistent response format. Quote data should always include the
carrier name, premium, limit, retention, and a unique quote identifier. Internal
carrier-specific field names or conventions should never leak into the user-facing
API.

## Principle 7: Auditability

Every submission, quote request, and bind action should be traceable. While
full audit logging is outside the scope of the current implementation, the
system should be designed so that adding audit trails later is straightforward.
Unique IDs should be generated for every transaction.

## Principle 8: Security by Default

Carrier API communications should use HTTPS in production. API keys and
credentials should never be hardcoded. For this exercise, simulators run over
HTTP on localhost, which is acceptable for development.

## Principle 9: Performance Targets

Quote retrieval should complete within 30 seconds for synchronous carriers. For
asynchronous carriers (polling-based), the platform should continue to poll
within a reasonable window (up to 60 seconds) before timing out. Users should
not be blocked from viewing partial results while other carriers are still
processing.

## Principle 10: Extensibility

Adding a new carrier should require only a new carrier client module and
registering it with the server. No changes to the core submission or quoting
logic should be needed. The carrier client interface is the contract — as long
as a new client implements `get_quote` and `bind_quote`, it integrates
seamlessly.
