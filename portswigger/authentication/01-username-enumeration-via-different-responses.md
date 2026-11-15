# LAB: Username enumeration via different responses

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication                                                                                                                  |
| **Difficulty**              | Apprentice                                                                                                                   |
| **Date**                    | 2026-11-15                                                                                                                   |
| **Time**                    |                                                                                                                                 |
| **Solved without solution** |                                                                                                                                 |
| **Link**                    | [lab-username-enumeration-via-different-responses](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-different-responses) |

## 1. Objective

Determine a valid username through differential application responses and then brute-force their password to log into the account.

## 2. Surface

- The login form endpoint and its request/response handling.
- Error messages or response structures returned when submitting invalid usernames versus invalid passwords.
- Password brute-force functionality or request iteration using a wordlist.

## 3. Hypothesis

If an application returns distinctly different error messages or structures for invalid usernames compared to valid usernames with incorrect passwords, an attacker can enumerate valid usernames and subsequently brute-force their credentials.

## 4. Payload that worked

Request:
```http
POST /login HTTP/2
Host: host.web-security-academy.net
Cookie: session=<session>
Content-Length: 34
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://host.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://host.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

username=amarillo&password=7777777
```

Response:
```http
HTTP/2 302 Found
Location: /my-account?id=amarillo
Set-Cookie: session=<session>; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works

The application leaks information about whether a username exists through differential error responses ("Invalid username" versus generic password failure messages). By dividing the attack into two focused phases—first enumerating the valid username and then brute-forcing only that specific user's password—the total number of required requests drops dramatically from a massive combinatorial explosion (thousands of username-password pairs) to two short, efficient passes.

## 6. What I tried that failed

No failed payloads. What worked was optimizing the workflow instead of running a blind Cartesian product (`Cluster Bomb`):
- Attempting to brute-force usernames and passwords simultaneously would require thousands of requests and obscure the distinct error messages.
- Splitting the process using `ffuf` allowed isolating the exact response length (`-fs 3244`) corresponding to "Invalid username", leaving only the valid user's response exposed.
- Rule extracted: always decouple authentication enumeration steps. Find the valid user first to reduce the attack surface before attempting credential brute-forcing.

## 7. In a real target (bounty translation)

- Where it shows up: Login portals, account recovery forms, and authentication APIs that fail to implement generic error messages.
- Quick detection: Submitting known invalid usernames versus common names (e.g., `admin`, `test`) and comparing response body text, status codes, or error headers.
- Impact: Account enumeration leading to targeted credential brute-forcing or password spraying attacks.
- In the report: Evidence of distinct responses revealing user existence, followed by a successful credential recovery demonstration.

## 8. Bypass / variants noticed

- Testing differential response lengths or status codes using CLI fuzzers like `ffuf` with size filters (`-fs`) to bypass rate-limiting or heavy Burp Suite Free UI delays.
- Analyzing response timing variations if error messages are textually identical.

## 9. Takeaway

Authentication interfaces must always return generic, uniform error messages for failed login attempts to prevent user enumeration.
