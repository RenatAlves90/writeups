# LAB: Brute-forcing a stay-logged-in cookie

|                             |                                                                                                                                 |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Topic**                   | Authentication (Other mechanisms)                                                                                             |
| **Difficulty**              | Practitioner                                                                                                                 |
| **Date**                    | 2026-11-20                                                                                                                   |
| **Time**                    |    35                                                                                                                       |
| **Solved without solution** | yes                                                                                                                                 |
| **Link**                    | [lab-brute-forcing-a-stay-logged-in-cookie](https://portswigger.net/web-security/authentication/other-mechanisms/lab-brute-forcing-a-stay-logged-in-cookie) |

## 1. Objective

Bypass authentication to access the account page of the target user (`carlos`) by identifying the weak encoding/hashing structure of the `stay-logged-in` persistent cookie and brute-forcing its value.

## 2. Surface

- Primary authentication endpoint (`/login`) processing credentials alongside a `stay-logged-in` checkbox parameter.
- HTTP response headers issuing a persistent `stay-logged-in` cookie upon selecting the option during login.
- Target protected endpoint (`/my-account`) accessible via valid `stay-logged-in` cookie value.

## 3. Hypothesis

If the `stay-logged-in` cookie relies on predictable or reversible client-side data formats (such as Base64 encoding over a static string concatenation like `username:md5(password)`), an attacker can construct candidate persistent cookies for the target account (`carlos`) using a wordlist of candidate passwords without issuing first-stage login requests.

## 4. Payload that worked

Request:
```http
GET /my-account?id=carlos HTTP/2
Host: <host>.web-security-academy.net
Cookie: stay-logged-in=Y2FybG9zOmUwNDc1NTM4N2U1YjU5NjhlYzIxM2U0MWY3MGMxZDQ2; session=sess
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/jxl,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Sec-Ch-Ua: "Not:A-Brand";v="8", "Chromium";v="156"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "Linux"
Referer: https://<host>.web-security-academy.net/login
Accept-Encoding: gzip, deflate, br
Priority: u=0, i
Connection: keep-alive
```
Response:
HTTP/1.1 200 OK

## 5. Why it works

The application generates persistent `stay-logged-in` authentication cookies using a deterministic, un-salted encoding scheme: `Base64(username:md5(password))`. Because the backend validates authentication directly from the decoded persistent cookie structure upon accessing the protected route `/my-account` without checking active session state or account lockout counters, an attacker can forge valid persistent cookies for any target account (`carlos`) by pre-computing `Base64(carlos:md5(candidate_password))` across a wordlist. Submitting the correctly forged cookie directly to `/my-account` returns an HTTP `200 OK` response with the authenticated profile page, while invalid cookies trigger an HTTP `302 Found` redirect back to `/login`.
## 6. What I tried that failed

- Attempted a standard credential brute-force attack against the primary `/login` endpoint, which failed due to account-level lockout mechanisms that locked `carlos` for 1 minute after consecutive failed login attempts.
- Verified that the lockout persisted even when attempting to refresh or authenticate via alternate sessions, confirming the lockout counter is strictly bound to the target username context rather than the source IP.
- Initially analyzed brute-force results expecting an HTTP `302` redirect to indicate success (matching previous multi-stage authentication labs); however, because requests were sent directly to `/my-account`, invalid cookies returned `302` redirects to `/login` while the single valid cookie returned an HTTP `200 OK`.
- Rule extracted: When brute-forcing persistent authentication cookies directly against protected endpoints (`/my-account`), look for HTTP `200 OK` responses indicating successful page rendering, rather than HTTP `302` redirects which indicate failed authentication and redirection to the login page.
  
## 7. In a real target (bounty translation)

- Where it shows up: Legacy web applications using simple token serialization patterns (e.g., `Base64(username:hash(password))` or `Base64(user_id:timestamp:MD5(secret))`) for persistent "Remember Me" functionality.
- Quick detection: Inspect set-cookie headers post-login for `stay-logged-in` or `remember_me` tokens. Base64-decode the value to check for plaintext usernames, delimiters (`:`), or standard 32-character MD5 / 40-character SHA1 hex strings.
- Impact: Full account takeover of any known username without interacting with authentication or rate-limiting controls on the login form.
- In the report: Provide the decoded token structure breakdown alongside a successful GET request to `/my-account` authenticated solely via the forged `stay-logged-in` cookie.

## 8. Bypass / variants noticed

- Pre-computing wordlists using shell pipelines or Python scripts to map plaintext passwords to their `Base64(username:md5(password))` representation before launching automated proxy/fuzzing attacks.
- Using `ffuf` with status code matchers (`-mc 200`) or status code filters (`-fc 302`) on protected endpoints to instantly isolate the single valid forged cookie from false-positive authentication redirects.

## 9. Takeaway

Persistent authentication cookies ("Remember Me") must never contain predictable hashes of user passwords or reversible plaintext structures. Applications should issue cryptographically secure, high-entropy, randomly generated session tokens stored server-side (or use signed JWTs with non-reversible session identifiers).
