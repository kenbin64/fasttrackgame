# One-Time Login

Last updated: 2026-03-06 • Version 1.0

## Overview
One-Time Login (OTL) enables passwordless authentication using a short-lived, single-use token delivered to a verified channel (email or SMS). Tokens expire quickly, cannot be reused, and may optionally bind to the requesting device and IP for enhanced security.

## Flow
1. Initiate login by entering your email or phone number.
2. We validate the identifier and send a one-time token (link or code).
3. Open the link or enter the code in the prompt on the same device.
4. If valid and within the expiry window, we establish a session and optionally enroll a device key for future fast login.

## Token Characteristics
- Single-use: redeemed once; subsequent attempts fail.
- Short-lived: configurable expiry (default 10–15 minutes).
- Scope-bound: may be tied to device fingerprint and approximate IP to reduce phishing.
- Replay-resistant: nonce + HMAC signed; stored hashed server-side.

## Security Considerations
- Rate limiting: per-identifier and per-IP limits, with exponential backoff.
- Abuse prevention: captcha or risk engine for anomalous patterns.
- Anti-phishing: clear domain, recognizable email templates, no sensitive data in links.
- Link hardening: rotating signing keys, strict TTLs, and redirect allowlists.
- Session hardening: httpOnly, Secure, SameSite cookies; short access tokens; refresh rotation.

## Recovery and Revocation
- If you did not request a login, ignore the token; it will expire automatically.
- You can revoke active sessions from account settings.
- Contact support to freeze your account if you suspect compromise.

## Developer Notes (Implementation-agnostic)
- Prefer MAGIC LINK + backup short code delivery.
- Store only hashed tokens with expiry; delete on redemption.
- Include device binding claim (ua hash) and rate-limit keys.
- Log structured security events for audit and anomaly detection.

## Privacy
We only use your provided contact to authenticate you and for necessary security notifications, as described in our Privacy Notice.