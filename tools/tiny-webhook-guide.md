# tiny-webhook — Production Webhook Handler (HMAC + idempotency + DLQ + retry)

**Repo:** github.com/hussain-alsaibai/tiny-webhook
**Install:** pip install tiny-webhook

> **Not published (verified 2026-11-03).** `pip install tiny-webhook` fails - the
> name returns **HTTP 404** on the PyPI JSON API. Install from the
> repository instead:
>
> ```bash
> pip install git+https://github.com/hussain-alsaibai/tiny-webhook.git
> ```
**Last verified:** 2026-08-14

HMAC verification for GitHub, Stripe, Slack, Discord, Telegram, SendGrid. File-backed idempotency, dead-letter queue, async retry with backoff. /health, /dlq, /routes, /metrics endpoints.
