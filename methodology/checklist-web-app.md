# Web App Checklist

## Auth

- [ ] Registration: duplicate email, weak password policy, user enumeration in errors/timing
- [ ] Login: rate limit, lockout, remember-me token strength, MFA bypass
- [ ] Password reset: token in URL, token reuse, token doesn't expire, host header injection
- [ ] Session: cookie flags (HttpOnly/Secure/SameSite), fixation, logout invalidation server-side

## Access control

- [ ] IDOR on every id/uuid/email in URL, body, JSON, headers
- [ ] Horizontal: second account, same tenant, swap identifiers
- [ ] Vertical: force-browsing admin endpoints, method change (GET→PUT→DELETE)
- [ ] API versioning: /v1/ vs /v2/, GraphQL field-level authz

## Input handling

- [ ] Reflected XSS in every parameter and every form field
- [ ] Stored XSS in profile, comments, file names, metadata
- [ ] SSRF on URL-accepting params, image import, webhooks
- [ ] SQLi in filters, sort, search; note error-based, time-based

## Upload

- [ ] Extension bypass, Content-Type bypass, magic bytes, double extension
- [ ] Path traversal in filename
- [ ] Stored XSS via SVG

## Disclosure

- [ ] .git/, .env, swagger.json, source maps, backups
- [ ] Stack traces, verbose errors, debug headers
- [ ] API keys in JS bundles

## Response observation (always, on every endpoint)

- [ ] Read raw response in Repeater — never judge by the rendered page
- [ ] Follow redirects OFF by default; if 3xx, read the body BEFORE following
- [ ] Diff rendered view vs raw response — the difference is a finding
- [ ] Read all headers: Location, Set-Cookie, X-\* debug headers
- [ ] Look for: HTML comments, hidden inputs, ignored JSON fields, verbose errors
