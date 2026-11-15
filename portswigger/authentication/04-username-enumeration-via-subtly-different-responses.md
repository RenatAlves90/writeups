# LAB: Username enumeration via subtly different responses

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication                                                                                                                  |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-15                                                                                                                   |
| **Time**                    |           15                                                                                                                      |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-username-enumeration-via-subtly-different-responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-subtly-different-responses) |

## 1. Objective

Determine a valid username through subtle differential application responses (such as a single punctuation mark discrepancy like a trailing period) and then brute-force their password to gain access.

## 2. Surface

- The login form endpoint and its request/response handling.
- Subtle error message text changes (e.g., presence or absence of a period `.` at the end of an error string).
- Response size and content length variations caused by micro-discrepancies in the HTML body.

## 3. Hypothesis

If an application attempts to obscure user enumeration by returning superficially similar error messages, but leaves a minor syntactical difference (such as an extra period at the end of the error string for invalid users versus valid users), an attacker can identify the valid user by carefully analyzing response differences or utilizing precise size filtering (`-fs`) in CLI tools like `ffuf`.

## 4. Payload that worked

Request:
```http
POST /login HTTP/2
Host: hoist.web-security-academy.net
Cookie: session=session
Content-Length: 31
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://hoist.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://hoist.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
username=access&password=amanda
```

Response:
```http
HTTP/2 302 Found
Location: /my-account?id=access
Set-Cookie: session=session; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works

The application leaks user existence through a nearly invisible syntax change in the error response—specifically, a single missing or extra period (`.`) at the conclusion of the invalid login message. By decoupling the attack into two focused phases (first enumerating the valid username using a CLI fuzzer with precise length filtering, and then running a targeted brute-force pass exclusively against that username), the scope drops from thousands of combinatorial attempts down to two fast, efficient cycles.

## 6. What I tried that failed

No failed payloads. What worked was careful analysis and workflow optimization:
- Initial visual inspection or standard bulk testing failed to highlight the error because the text looked identical at a glance.
- Analyzing response-by-response comparisons or filtering out the massive bulk of standard responses revealed the micro-discrepancy (a single character difference shifting the `Content-Length` by a few bytes).
- Rule extracted: when error messages look identical, rely on binary diffing, length metrics (`-fs`), or word/character count checks rather than human visual inspection.

## 7. In a real target (bounty translation)

- Where it shows up: Mature authentication portals that attempt to prevent enumeration but introduce subtle logic flaws, template rendering discrepancies, or minor string mismatches in error handling.
- Quick detection: Scripting automated comparisons of response bodies across a user wordlist to spot outlier responses that deviate by only a handful of bytes.
- Impact: Account enumeration leading to credential stuffing or targeted brute-force attacks.
- In the report: Side-by-side comparison of raw responses demonstrating the subtle character or length discrepancy that exposes user existence.

## 8. Bypass / variants noticed

- Using automated diff tools or CLI fuzzers (`ffuf`) with strict size filters to instantly flag responses that deviate by even 1 or 2 bytes due to micro-syntax changes.
- Examining response timing variations if text and length are entirely masked.

## 9. Takeaway

Micro-discrepancies in error strings—such as a single punctuation mark or trailing space—completely break the illusion of generic error handling. Always validate raw response bodies programmatically during security assessments.
