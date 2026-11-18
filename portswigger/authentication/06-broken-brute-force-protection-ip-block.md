# LAB: Broken brute-force protection, IP block

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication                                                                                                                  |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-17                                                                                                                   |
| **Time**                    |                                                                                                                                 |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-broken-bruteforce-protection-ip-block](https://portswigger.net/web-security/authentication/password-based/lab-broken-bruteforce-protection-ip-block) |

## 1. Objective

Determine the password for a valid target account (`carlos`) by bypassing an IP-based lockout mechanism that resets its failure counter when a successful login occurs.

## 2. Surface

- Login form endpoint (`/login`) accepting `username` and `password` parameters.
- IP-based brute-force tracking mechanism that triggers a block after a fixed number of consecutive failed authentication attempts from the same IP.
- Session handling behavior following successful authentication requests.

## 3. Hypothesis

If the server tracks failed login attempts per IP but resets the failure counter upon *any* successful login from that IP, an attacker can interleave valid logins (using a known account like `wiener:peter`) between failed brute-force attempts to reset the counter before reaching the IP block threshold.

## 4. Payload that worked

Request (Interleaved Reset Request):
POST /login HTTP/1.1
Host: [lab-id].web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 31

username=wiener&password=peter

Request:
```http
POST /login HTTP/2
Host: host.web-security-academy.net
Cookie: session=session
Content-Length: 30
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

username=carlos&password=pepper
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

The application tracks failed authentication attempts per IP address and triggers a lockout after 3 consecutive failures. However, the backend flaw lies in state management: any successful authentication from that IP resets the global failure counter back to zero. By structuring a brute-force attack to alternate every 2 failed attempts against `carlos` with 1 successful login using valid credentials (`wiener:peter`), the IP-based failure counter is continuously cleared before hitting the lockout threshold of 3, allowing systematic credential enumeration.

## 6. What I tried that failed
- Performing a standard dictionary attack against `carlos` without interleaved reset requests failed immediately, as the 3rd consecutive incorrect attempt triggered a full IP lockout block.
- Rule extracted: When IP lockouts trigger on short thresholds (e.g., 3 failed attempts), verify if valid logins reset the IP failure counter state before attempting large-scale wordlist execution.
  
## 7. In a real target (bounty translation)

- Where it shows up: Login portals, administrative panels, and authentication APIs where rate-limiting logic is scoped globally per IP and cleared on authentication success without tracking failed attempts per target account.
- Quick detection: Perform multiple invalid logins up to the threshold minus one, send a single valid login with owned credentials, and verify if the subsequent failed attempt is allowed without triggering a block.
- Impact: Complete evasion of IP-based brute-force protections, allowing persistent dictionary attacks against arbitrary user accounts.
- In the report: Provide request logs demonstrating alternating valid/invalid login sequences and document how the failure counter fails to trigger an IP lockout.

## 8. Bypass / variants noticed

- Interleaving valid credential pairs (`wiener:peter`) every N-1 failed requests in tools like Turbo Intruder or custom automation scripts to keep the IP failure counter continuously at zero.
- Automating state reset patterns via customized macro sequences in Burp Suite Intruder or multi-wordlist pitchfork combinations.

## 9. Takeaway

Flawed state management in rate-limiting mechanisms can undermine brute-force defenses. Account protection controls should track authentication failures independently per account/IP tuple and enforce lockouts based on total consecutive failures across specific accounts rather than resetting global IP counters on unrelated success events.
