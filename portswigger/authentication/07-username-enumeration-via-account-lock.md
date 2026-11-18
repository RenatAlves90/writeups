# LAB: Username enumeration via account lock

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication                                                                                                                  |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-17                                                                                                                   |
| **Time**                    |                     15                                                                                                            |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-username-enumeration-via-account-lock](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-account-lock) |

## 1. Objective

Determine a valid username by observing account locking behavior after repeated failed login attempts, then brute-force the password of the valid account to gain access.

## 2. Surface

- Login form endpoint (`/login`) processing authentication attempts.
- Account lockout mechanism that disables or locks specific user accounts after a defined threshold of consecutive failed login attempts.
- Response messages reflecting account status (e.g., specific warning or lockout notifications).

## 3. Hypothesis

If an application increments a failure counter tied specifically to a user account (rather than the source IP) and triggers an account lockout warning after a fixed number of incorrect password attempts, an attacker can enumerate valid usernames by checking which account triggers the specific lockout message or error state.

## 4. Payload that worked

Request:
```http
POST /login HTTP/2
Host: <host>.web-security-academy.net
Cookie: session=sess
Content-Length: 26
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
X-Forwarded-For: 1232

username=ak&password=12345
```

Response:
```http
HTTP/2 302 Found
Location: /my-account?id=ak
Set-Cookie: session=sess; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works

The application processes authentication attempts by evaluating the username first. If the username exists, it increments the failure counter for that specific account. Once the threshold (e.g., 5 consecutive failures) is reached, the server changes the response message or status to explicitly indicate an account lockout, whereas non-existent usernames return a generic invalid credentials message without altering an account state.

## 6. What I tried that failed

- Initially looked for micro-discrepancies in response times or error message text on the first failed attempt, which were identical across both valid and invalid usernames.
- Attempted brute-forcing passwords before locking out the account, which failed because the account became locked and required administrative reset or waiting out the lockout window.
- Rule extracted: When account locking is enabled, systematically send N-1 incorrect password attempts for each candidate user from a wordlist. The account that triggers the lockout warning on the Nth attempt is the valid target.

## 7. In a real target (bounty translation)

- Where it shows up: Legacy or improperly configured authentication portals where account lockout messages leak user existence or where failure counters increment for valid accounts prior to credential verification.
- Quick detection: Submit repeated incorrect password attempts for a test account versus random strings and monitor for differential response text or explicit lockout notifications.
- Impact: Accurate enumeration of valid user accounts in systems that lack proper account lockout protections or generic error messaging.
- In the report: Provide request/response pairs demonstrating the specific lockout message returned only for valid accounts after reaching the failure threshold.

## 8. Bypass / variants noticed

- Using multi-threaded tooling (`ffuf` or Burp Suite Intruder) with carefully paced request sequences to hit the exact lockout threshold for each candidate user in a wordlist without triggering false positives.

## 9. Takeaway

Authentication interfaces must return uniform, generic error messages for all failed login attempts regardless of whether the username exists, and account lockouts should be paired with CAPTCHAs, rate limiting, or IP-based controls rather than leaking account validity through explicit lockout messages.
