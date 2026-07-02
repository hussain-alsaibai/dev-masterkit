# aws-sigv4-handrolled — Prompt for inline AWS SigV4 signing (stdlib only)

## Description

How to sign an AWS request (specifically Secrets Manager `GetSecretValue`)
using only Python's stdlib `hmac` and `hashlib`. Use this when you need
a zero-dependency path to one specific AWS action and don't want to ship
`boto3`.

## When to use

- You need exactly one AWS API call (e.g. fetch a secret at startup)
- Adding `boto3` to a stdlib-only project would violate the zero-dep rule
- Writing a teaching / reference implementation

## The prompt

```
We need to call AWS Secrets Manager GetSecretValue with stdlib only.
Do NOT pull in boto3. Produce a function:

    def get_secret(secret_id: str, region: str = "us-east-1") -> str:
        ...

Steps:
  1. Read AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY from env.
  2. Build the canonical request:
       method = "GET"
       canonical_uri = "/"
       canonical_querystring = ""
       canonical_headers = f"host:secretsmanager.{region}.amazonaws.com\nx-amz-date:{amz_date}\n"
       signed_headers = "host;x-amz-date"
       payload_hash = hashlib.sha256(b"").hexdigest()
       canonical_request = "\n".join([
           method, canonical_uri, canonical_querystring,
           canonical_headers, signed_headers, payload_hash,
       ])
  3. Build string to sign:
       algorithm = "AWS4-HMAC-SHA256"
       credential_scope = f"{date}/{region}/secretsmanager/aws4_request"
       hashed_canonical = hashlib.sha256(canonical_request.encode()).hexdigest()
       string_to_sign = "\n".join([
           algorithm, amz_date, credential_scope, hashed_canonical,
       ])
  4. Derive the signing key (the 4-step HMAC chain):
       k_date    = hmac.new(("AWS4" + secret_key).encode(), date.encode(),
                            hashlib.sha256).digest()
       k_region  = hmac.new(k_date, region.encode(), hashlib.sha256).digest()
       k_service = hmac.new(k_region, b"secretsmanager", hashlib.sha256).digest()
       k_signing = hmac.new(k_service, b"aws4_request", hashlib.sha256).digest()
  5. Compute the signature:
       signature = hmac.new(k_signing, string_to_sign.encode(),
                            hashlib.sha256).hexdigest()
  6. Build the Authorization header:
       auth = (f"AWS4-HMAC-SHA256 Credential={access_key}/{credential_scope}, "
               f"SignedHeaders={signed_headers}, Signature={signature}")
  7. Send the request with `urllib.request.Request` and the headers:
       host, x-amz-date, x-amz-target: secretsmanager.GetSecretValue, authorization
  8. Parse JSON, return `SecretString`.

Scope guardrails (state these in the docstring):
  - Only valid for GetSecretValue on Secrets Manager.
  - Other AWS services need a different canonical request shape.
  - No retries, no pagination, no IAM auth, no sessions. Keep it ~50 LOC.

If a user needs more, point them to boto3 and stop trying to grow this.
```

## Why this exists

`tiny-secret` needed a no-deps way to fetch a single secret at boot. Pulling
in `boto3` would have broken the "0 dependencies" promise. Hand-rolling
SigV4 is ~50 LOC and only one action; anything more belongs in a real SDK.

Last verified: 2026-07-02
