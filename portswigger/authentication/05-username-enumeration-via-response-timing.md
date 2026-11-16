# LAB: Username enumeration via response timing

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication                                                                                                                  |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-15                                                                                                                   |
| **Time**                    |        46                                                                                                                         |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-username-enumeration-via-response-timing](https://portswigger.net/web-security/authentication/password-based/lab-username-enumeration-via-response-timing) |

## 1. Objective

Determine a valid username through response timing analysis and subsequently brute-force their password to gain access.

## 2. Surface

- The login form endpoint and its request/response handling.
- Response duration metrics to identify processing delays caused by valid usernames.
- Wordlist iteration and latency monitoring.

## 3. Hypothesis

If an application takes longer to respond when a valid username is provided due to backend processing differences, measuring response times allows for successful user enumeration even when status codes and response lengths are identical.

## 4. Payload that worked

Request:
```http
POST /login HTTP/2
Host: host.web-security-academy.net
Cookie: session=session
Content-Length: 38
Cache-Control: max-age=0
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Origin: https://0a0200ab033e31cd81b702ca00380070.web-security-academy.net
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://0a0200ab033e31cd81b702ca00380070.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

username=announcements&password=killer
```

Response:
```http
HTTP/2 302 Found
Location: /my-account?id=announcements
Set-Cookie: session=session; Secure; HttpOnly; SameSite=None
X-Frame-Options: SAMEORIGIN
Content-Length: 0
```

## 5. Why it works
The application enforces rate-limiting based on the client IP supplied in the `X-Forwarded-For` header rather than the network socket connection IP, allowing IP spoofing to reset the failure counter per request. When a valid username is submitted alongside an intentionally long password string, the backend executes a computationally heavy password verification algorithm, causing a measurable delay in response duration compared to invalid usernames that fail instantly.

## 6. What I tried that failed
- Spent significant time analyzing response bodies for textual micro-discrepancies or content-length differences, which yielded no results because error messages and body sizes were completely identical.
- Initial brute-force attempts triggered an IP block after 4 failed requests, which was initially verified by switching VPN servers to confirm the IP restriction.
- Rule extracted: When response bodies match 1:1 and rate limits trigger quickly, pivot to checking for IP-trust headers (`X-Forwarded-For`) and measuring server latency (Response Duration) using baseline tests with valid credentials (e.g., `wiener`) and long payloads.

## 7. In a real target (bounty translation)

- Where it shows up: Authentication portals and APIs with asymmetric processing times for valid versus invalid accounts.
- Quick detection: Measuring baseline response times and identifying statistical outliers.
- Impact: Account enumeration leading to targeted credential brute-forcing.
- In the report: Latency comparisons demonstrating measurable time deltas for valid inputs.

## 8. Bypass / variants noticed
- Bypassing IP-based lockout controls using `pitchfork` mode in `ffuf` to pair unique IP addresses line-by-line with candidate values without causing combinatorial request explosions.
- Amplifying timing deltas by sending extra-long password strings to increase server hashing workload during validation.

## 9. Takeaway

Backend execution time differences completely undermine identical response bodies, making timing side-channels a critical vector for user enumeration.
