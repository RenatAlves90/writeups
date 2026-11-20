# LAB: 2FA bypass using a brute-force attack

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication (Multi-factor authentication)                                                                                  |
| **Difficulty**              | Expert                                                                                                                 |
| **Date**                    | 2026-11-19                                                                                                                   |
| **Time**                    |         230                                                                                                                        |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-2fa-bypass-using-a-brute-force-attack](https://portswigger.net/web-security/authentication/multi-factor/lab-2fa-bypass-using-a-brute-force-attack) |

## 1. Objective

Bypass 2FA protection on the target user account (`carlos`) by exploiting flawed rate-limiting logic on the 2FA submission endpoint to brute-force the 4-digit verification code.

## 2. Surface

- Primary authentication page (`/login`) processing first-factor credentials (`carlos:montoya`).
- Secondary authentication endpoint (`/login2`) processing the 4-digit `mfa-code` submission.
- Session cookie state management across Stage 1 and Stage 2 authentication states.
- IP-based or session-based rate-limiting mechanism protecting the 2FA verification endpoint.

## 3. Hypothesis

If the 2FA verification endpoint (`/login2`) enforces rate limiting based on invalid attempt counts per IP or session without invalidating the 2FA session upon rate-limit failure, an attacker can interleave valid request flows or bypass/reset IP counters to brute-force the 4-digit code (`0000`-`9999`).

## 4. Payload that worked

Request
[py script](./17-2FA-bypass-using-a-brute-force-attack.py)

Response:
```text
[Thread-29] POST /login2 (1920) -> status 200 | Location:  | Incorrect: True
[Thread-9] POST /login -> status 302 | Location: /login2 | session: <session>
[Thread-23] POST /login2 (1510) -> status 200 | Location:  | Incorrect: True
[Thread-14] POST /login2 (0915) -> status 200 | Location:  | Incorrect: True
[Thread-7] POST /login -> status 302 | Location: /login2 | session: <session>
[Thread-15] POST /login -> status 302 | Location: /login2 | session: <session>
[Thread-10] POST /login -> status 302 | Location: /login2 | session: <session>
...
[Thread-21] [SUCCESS] MFA: 0601 | session: <session> | csrf: zT2DAeWQYloi7YVoGWDHH8RBTtdKKlqK

--- FINAL RESULT ---
MFA Code : 0601
Session  : <session>
CSRF     : zT2DAeWQYloi7YVoGWDHH8RBTtdKKlqK
/my-account: status 200
```

## 5. Why it works

The application enforces strict server-side state synchronization between the active session cookie and the generated CSRF token during the 2FA verification flow at `/login2`. Reusing existing CSRF tokens, swapping tokens across sessions, or maintaining static headers fails because each 2FA request requires a fresh, dynamically coupled token pair. By developing a multi-threaded Python script using `requests.Session()` and `threading.Thread`, it was possible to programmatically complete Stage 1 (`/login`), extract the freshly generated session cookie and matching CSRF token, submit a 4-digit `mfa-code` candidate within that isolated session scope, and immediately terminate all worker threads via a `threading.Event()` signal upon receiving a valid authentication response.
## 6. What I tried that failed

- Attempted to manually brute-force the 2FA code using Burp Suite Repeater/Intruder with static or reused CSRF tokens and session cookies, resulting in persistent `500 Internal Server Error` or "Invalid CSRF token" responses due to missing session-token synchronization.
- Attempted replacing only the session cookie while keeping the CSRF token static (and vice-versa), which triggered invalid token errors because the backend strictly pairs the specific CSRF token to its corresponding transient session context.
- Attempted reusing a single CSRF token across multiple 2FA payload attempts, which failed because tokens are invalidated after a single use or attempt.
- Rule extracted: When 2FA verification endpoints validate per-request CSRF tokens bound strictly to transient session state, manual proxy repeater attacks fail. Automation scripts must dynamically fetch a new session cookie and CSRF token pair for every single 2FA attempt.

## 7. In a real target (bounty translation)

- Where it shows up: 2FA validation steps where rate limits reset on session regeneration or where failure counters permit sufficient headroom to brute-force small search spaces (e.g., 4-digit codes) before lockouts trigger.
- Quick detection: Submit sequential incorrect 2FA codes on a test account to identify rate-limiting thresholds and test whether re-authenticating Stage 1 or resetting tracking headers clears the block.
- Impact: Complete 2FA bypass, enabling full account takeover when first-factor credentials are known.
- In the report: Provide request logs showing first-factor authentication followed by automated execution of the 4-digit 2FA space leading to account access.

## 8. Bypass / variants noticed

- Developing custom Python brute-force scripts using requests.Session() and re to handle dynamic session cookie retrieval and HTML CSRF token extraction concurrently per attempt.

- Implementing multi-threading (threading.Thread split across numerical ranges) with global threading.Event() stop signals and thread-safe locking (threading.Lock()) to halt execution immediately when a valid 2FA code is discovered, preserving the active session cookie.

## 9. Takeaway

2FA verification endpoints must enforce strict, low-threshold rate limits tied globally to the account context. Additionally, 4-digit codes should expire quickly, and sessions must be completely invalidated after a small number of consecutive failed 2FA verification attempts.
